import json
import re
from urllib.parse import urljoin

import requests
from PySide2.QtGui import QPixmap
from PySide2.QtWidgets import QMessageBox

from modules.ocr import classify_captcha
from modules.utils import (
    captcha_url,
    http_head,
    login_url,
    request_get,
    request_post,
    runtime_path,
    save_config,
    security_check_url,
)
from modules.hex_md5 import hex_md5


def _extract_form_action(page_text):
    match = re.search(r'(?is)<form[^>]*action=["\']([^"\']+)["\']', page_text)
    if not match:
        return security_check_url
    return urljoin(login_url, match.group(1))


def _extract_hidden_inputs(page_text):
    hidden_inputs = {}
    for match in re.finditer(r"(?is)<input\b([^>]+)>", page_text):
        attrs = match.group(1)
        type_match = re.search(r'type=["\']([^"\']+)["\']', attrs, re.IGNORECASE)
        if not type_match or type_match.group(1).lower() != "hidden":
            continue

        name_match = re.search(r'name=["\']([^"\']+)["\']', attrs, re.IGNORECASE)
        if not name_match:
            continue

        value_match = re.search(r'value=["\']([^"\']*)["\']', attrs, re.IGNORECASE)
        hidden_inputs[name_match.group(1)] = value_match.group(1) if value_match else ""

    return hidden_inputs


def _extract_login_button_onclick(page_text):
    button_match = re.search(
        r'(?is)<input\b[^>]*\bid=["\']loginButton["\'][^>]*>',
        page_text,
    )
    if not button_match:
        return ""

    onclick_match = re.search(
        r'(?is)\bonclick\s*=\s*(["\'])(.*?)\1',
        button_match.group(0),
    )
    return onclick_match.group(2) if onclick_match else ""


def _extract_token(page_text):
    token_input = re.search(r'(?is)<input\b[^>]*(?:name|id)=["\']tokenValue["\'][^>]*>', page_text)
    if token_input:
        value_match = re.search(r'value=["\']([^"\']+)["\']', token_input.group(0), re.IGNORECASE)
        if value_match:
            return value_match.group(1)

    patterns = (
        r'name=["\']tokenValue["\'][^>]*value=["\']([^"\']+)["\']',
        r'id=["\']tokenValue["\'][^>]*value=["\']([^"\']+)["\']',
        r'tokenValue["\']?\s*[:=]\s*["\']([^"\']+)["\']',
    )
    for pattern in patterns:
        match = re.search(pattern, page_text, re.IGNORECASE)
        if match:
            return match.group(1)
    return ""


def _extract_login_error(page_text):
    known_errors = (
        "验证码错误",
        "token校验失败",
        "用户名或密码错误",
        "账号或密码错误",
        "用户名或密码不正确",
        "密码错误",
    )
    for error_text in known_errors:
        if error_text in page_text:
            return error_text

    generic_patterns = (
        r'(?s)<[^>]*class=["\'][^"\']*(?:error|alert)[^"\']*["\'][^>]*>(.*?)</[^>]+>',
        r'(?s)<font[^>]*color=["\']?red["\']?[^>]*>(.*?)</font>',
    )
    for pattern in generic_patterns:
        match = re.search(pattern, page_text, re.IGNORECASE)
        if not match:
            continue
        message = re.sub(r"<[^>]+>", "", match.group(1)).strip()
        if message:
            return message

    return ""


def _is_login_success(page_text, response_url):
    return "退出系统" in page_text or "/student/" in response_url or "的培养方案" in page_text


def _detect_password_rule(page_text):
    onclick_code = _extract_login_button_onclick(page_text)
    if not onclick_code:
        return None, ""

    normalized = re.sub(r"\s+", "", onclick_code)
    double_md5_pattern = (
        r"hex_md5\(hex_md5\(\$\('#input_password'\)\.val\(\)(?:,'1\.8')?\)"
        r"(?:,'1\.8')?\)\+'\*'\+"
        r"hex_md5\(hex_md5\(\$\('#input_password'\)\.val\(\)(?:,'1\.8')?\)"
        r"(?:,'1\.8')?\)"
    )
    if re.search(double_md5_pattern, normalized, re.IGNORECASE):
        return "double_md5_pair", onclick_code

    legacy_md5_pattern = (
        r"hex_md5\(\$\('#input_password'\)\.val\(\)\+'\{Urp602019\}'\)"
        r"\+'\*'\+hex_md5\(\$\('#input_password'\)\.val\(\)\)"
    )
    if re.search(legacy_md5_pattern, normalized, re.IGNORECASE):
        return "legacy_magic_md5_pair", onclick_code

    if "hex_md5($('#input_password').val())" in normalized.lower():
        return "plain_md5", onclick_code

    return None, onclick_code


def _get_password_rules(page_text):
    rules = []
    detected_rule, _ = _detect_password_rule(page_text)
    if detected_rule:
        rules.append(detected_rule)

    for fallback_rule in ("double_md5_pair", "legacy_magic_md5_pair", "plain_md5"):
        if fallback_rule not in rules:
            rules.append(fallback_rule)
    return rules


def _build_password(password_plain, rule_name):
    if rule_name == "double_md5_pair":
        left_part = hex_md5(hex_md5(password_plain), "1.8")
        right_part = hex_md5(hex_md5(password_plain, "1.8"), "1.8")
        return left_part + "*" + right_part

    if rule_name == "legacy_magic_md5_pair":
        return hex_md5(password_plain) + "*" + hex_md5(password_plain, "1.8")

    if rule_name == "plain_md5":
        return hex_md5(password_plain, "1.8")

    raise ValueError("Unsupported password rule: {}".format(rule_name))


def _remember_login(sself, username, password):
    user_json = {"userList": []}
    try:
        with open("userinfo.json", "r", encoding="utf-8") as user_file:
            user_json = json.load(user_file)
    except (FileNotFoundError, json.JSONDecodeError):
        pass

    user_list = user_json.setdefault("userList", [])
    for item in user_list:
        if item.get("username") == username:
            item["password"] = password
            break
    else:
        user_list.append({"username": username, "password": password})

    with open("userinfo.json", "w", encoding="utf-8") as user_file:
        json.dump(user_json, user_file, ensure_ascii=False, indent=2)

    save_config({"username": username, "password": password})


def recognize_login_captcha(sself):
    image_content = getattr(sself, "captcha_content", None)
    if not image_content:
        QMessageBox.about(sself.ui, "[提示]", "请先刷新验证码")
        return ""
    try:
        code = classify_captcha(image_content)
    except Exception as exc:
        QMessageBox.about(sself.ui, "[错误]", "OCR识别失败：{}".format(exc))
        return ""
    sself.ui.captcha.setText(code)
    return code


def urp_setup(sself):
    try:
        response = request_get(login_url)
        if response.status_code != 200:
            QMessageBox.about(sself.ui, "[错误]", "登录页打开失败，状态码：{}".format(response.status_code))
            return ""

        sself.login_action_url = _extract_form_action(response.text)
        sself.login_hidden_inputs = _extract_hidden_inputs(response.text)
        sself.password_rules = _get_password_rules(response.text)
        sself.password_rule_index = 0
        token_value = _extract_token(response.text)
        if not token_value:
            QMessageBox.about(sself.ui, "[错误]", "随机token获取错误，教务系统登录页可能已变化")
            return ""

        http_captcha = request_get(captcha_url)
        sself.captcha_content = http_captcha.content
        captcha_file = runtime_path("captcha.jpg")
        with open(captcha_file, "wb") as http_capfile:
            http_capfile.write(sself.captcha_content)
    except requests.exceptions.RequestException as exc:
        QMessageBox.about(sself.ui, "[错误]", "网络错误：{}".format(exc))
        return ""

    pixmap = QPixmap(captcha_file)
    sself.ui.captcha_pic.setPixmap(pixmap)
    recognize_login_captcha(sself)
    return token_value


def urp_login(sself):
    username = sself.ui.username.currentText().strip()
    password = sself.ui.password.text()
    captcha = sself.ui.captcha.text().strip()

    if not username or not password or not captcha:
        QMessageBox.about(sself.ui, "[登录未成功]", "请填写学号、密码和验证码")
        return -1

    rules = getattr(sself, "password_rules", None) or ["double_md5_pair", "legacy_magic_md5_pair", "plain_md5"]
    first_rule_index = getattr(sself, "password_rule_index", 0)
    action_url = getattr(sself, "login_action_url", security_check_url)
    hidden_inputs = getattr(sself, "login_hidden_inputs", {}) or {}
    last_error = ""

    for rule_index in range(first_rule_index, len(rules)):
        post_data = dict(hidden_inputs)
        post_data["tokenValue"] = sself.tokenval
        post_data["j_username"] = username
        post_data["j_password"] = _build_password(password, rules[rule_index])
        post_data["j_captcha"] = captcha

        login_headers = dict(http_head)
        login_headers["Referer"] = login_url
        login_headers["Origin"] = "http://zhjw.scu.edu.cn"

        try:
            http_post = request_post(action_url, data=post_data, headers=login_headers)
        except requests.exceptions.RequestException as exc:
            QMessageBox.about(sself.ui, "[错误]", "网络错误：{}".format(exc))
            return -1

        if _is_login_success(http_post.text, http_post.url):
            if sself.ui.is_remember.isChecked():
                _remember_login(sself, username, password)
            return 0

        last_error = _extract_login_error(http_post.text)
        if last_error == "验证码错误" or "验证码" in last_error:
            QMessageBox.about(sself.ui, "[登录未成功]", "验证码不正确")
            return -1
        if last_error and "密码" in last_error and rule_index + 1 < len(rules):
            continue
        if last_error:
            QMessageBox.about(sself.ui, "[登录未成功]", last_error)
            return 1

    QMessageBox.about(sself.ui, "[登录未成功]", last_error or "未识别的登录响应，请重新获取验证码后再试")
    return 1
