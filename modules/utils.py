import json
import os
import random
from datetime import datetime

import requests


http_main = requests.session()
REQUEST_TIMEOUT = 15

login_url = "http://zhjw.scu.edu.cn/login"
security_check_url = "http://zhjw.scu.edu.cn/j_spring_security_check"
captcha_url = "http://zhjw.scu.edu.cn/img/captcha.jpg"
course_select_url = "http://zhjw.scu.edu.cn/student/courseSelect/courseSelect/index"
free_course_select_url = "http://zhjw.scu.edu.cn/student/courseSelect/freeCourse/courseList"
course_submit_url = "http://zhjw.scu.edu.cn/student/courseSelect/selectCourse/checkInputCodeAndSubmit"
select_captcha_url = "http://zhjw.scu.edu.cn/student/courseSelect/selectCourse/getYzmPic.jpg"
selected_courses_url = "http://zhjw.scu.edu.cn/student/courseSelect/thisSemesterCurriculum/callback"
course_quit_url = "http://zhjw.scu.edu.cn/student/courseSelect/quitCourse/index"
course_delete_url = "http://zhjw.scu.edu.cn/student/courseSelect/delCourse/deleteOne"

# Backwards-compatible aliases used by older window modules.
http_url_init = login_url
http_urls_select_res = selected_courses_url
http_urls_course_select = course_select_url
http_urls_course_list = free_course_select_url
http_urls_post = course_submit_url
http_urls_delete = course_delete_url
http_urls_course_quit = course_quit_url

http_head = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 "
    "Safari/537.36 Edg/105.0.1343.33"
}

query_class_data = {
    "kkxsh": "",
    "kch": "",
    "kcm": "",
    "skjs": "",
    "kclbdm": "",
    "xq": "0",
    "jc": "0",
}

post_class_data = {
    "dealType": 5,
    "kcIds": "",
    "kcms": "",
    "fajhh": "",
    "sj": "0_0",
    "kkxsh": "",
    "kclbdm": "",
    "kclbdm2": "",
    "inputCode": "",
    "tokenValue": "",
}

default_config = {
    "username": "",
    "password": "",
    "major_id": "",
    "sleep_time": 2,
    "sleep_jitter": 0.5,
}


def print_log(message, level="INFO"):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    level = (level or "INFO").upper()
    prefix = {
        "SUCCESS": "[+]",
        "INFO": "[*]",
        "ERROR": "[!]",
        "DEBUG": "[DEBUG]",
    }.get(level, "[*]")
    print("[{}]{} {}".format(ts, prefix, message))


def config_path():
    return os.path.join(app_dir(), "config.json")


def app_dir():
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def runtime_path(filename):
    return os.path.join(app_dir(), filename)


def request_get(url, **kwargs):
    kwargs.setdefault("headers", http_head)
    kwargs.setdefault("timeout", REQUEST_TIMEOUT)
    return http_main.get(url, **kwargs)


def request_post(url, **kwargs):
    kwargs.setdefault("headers", http_head)
    kwargs.setdefault("timeout", REQUEST_TIMEOUT)
    return http_main.post(url, **kwargs)


def load_config():
    path = config_path()
    if not os.path.exists(path):
        return default_config.copy()

    try:
        with open(path, "r", encoding="utf-8") as handle:
            data = json.load(handle)
    except (json.JSONDecodeError, OSError):
        return default_config.copy()

    config = default_config.copy()
    config.update(data)
    return config


def save_config(config):
    path = config_path()
    current = load_config()
    current.update(config)
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(current, handle, ensure_ascii=False, indent=2)


def get_major_id():
    return str(load_config().get("major_id", "") or "")


def set_major_id(major_id):
    major_id = str(major_id or "")
    save_config({"major_id": major_id})
    post_class_data["fajhh"] = major_id
    return major_id


def get_sleep_interval(fallback=2):
    config = load_config()
    try:
        base = float(config.get("sleep_time", fallback))
    except (TypeError, ValueError):
        base = float(fallback)

    try:
        jitter = float(config.get("sleep_jitter", 0.5))
    except (TypeError, ValueError):
        jitter = 0.5

    return max(0.1, base + random.uniform(-abs(jitter), abs(jitter)))


def sanitize_text(value):
    if not isinstance(value, str):
        return value
    return value.encode("utf-8", "ignore").decode("utf-8", "ignore")


def encode_course_name(value):
    value = sanitize_text(value or "")
    return "".join(str(int(hex(ord(ch)).zfill(4), 16)) + "," for ch in value)


def normalize_course_list(raw_value):
    if isinstance(raw_value, str):
        return json.loads(raw_value) if raw_value else []
    if isinstance(raw_value, list):
        return raw_value
    return []
