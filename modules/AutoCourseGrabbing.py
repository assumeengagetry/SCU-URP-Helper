import json
import re
import time

import ddddocr
import requests.exceptions
from PySide2.QtCore import QThread
from PySide2.QtWidgets import QMessageBox, QTableWidgetItem

from modules.utils import (
    course_delete_url,
    course_quit_url,
    course_select_url,
    course_submit_url,
    encode_course_name,
    free_course_select_url,
    get_major_id,
    get_sleep_interval,
    normalize_course_list,
    post_class_data,
    query_class_data,
    request_get,
    request_post,
    runtime_path,
    sanitize_text,
    selected_courses_url,
    select_captcha_url,
    set_major_id,
)


class Thread_start(QThread):
    def __init__(self, sself):
        super().__init__()
        self.sself = sself
        self.course_grabbing = sself.course_grabbing

    def run(self):
        self.course_grabbing.start(self.sself)


class AutoCourseGrabbing:
    def __init__(self):
        self.data = {}
        self.fxid = get_major_id()
        self.numc = {}
        self.data_list = []
        self.ocr = None

    def _get_ocr(self):
        if self.ocr is None:
            self.ocr = ddddocr.DdddOcr(show_ad=False)
        return self.ocr

    def _message(self, sself, title, content):
        QMessageBox.about(sself.ui, title, content)

    def _emit_message(self, sself, content):
        if hasattr(sself, "communicate"):
            sself.communicate.message.emit(content)
        else:
            self._message(sself, "[提示]", content)

    def _set_start_enabled(self, sself, enabled):
        if hasattr(sself, "communicate"):
            sself.communicate.start_enabled.emit(enabled)
        else:
            sself.ui.start_btn.setEnabled(enabled)

    def _show_running_course(self, sself, course):
        if hasattr(sself, "communicate"):
            sself.communicate.table_data.emit(course)
        else:
            self.show_course_in_table(course, sself)

    def _extract_token(self, page_text):
        token_input = re.search(r'(?is)<input\b[^>]*(?:name|id)=["\']tokenValue["\'][^>]*>', page_text)
        if token_input:
            value_match = re.search(r'value=["\']([^"\']+)["\']', token_input.group(0), re.IGNORECASE)
            if value_match:
                return value_match.group(1)

        match = re.search(r'id=["\']tokenValue["\'][^>]*value=["\']([^"\']+)["\']', page_text, re.IGNORECASE)
        if match:
            return match.group(1)
        match = re.search(r'name=["\']tokenValue["\'][^>]*value=["\']([^"\']+)["\']', page_text, re.IGNORECASE)
        if match:
            return match.group(1)
        idx = page_text.find('id="tokenValue"')
        if idx != -1:
            return page_text[idx + 23: idx + 55]
        return ""

    def _extract_major_id_from_page(self, page_text):
        patterns = (
            r"fajhh=(\d+)",
            r'name["\']fajhh["\']\s+value["\'](\d+)["\']',
            r'value["\'](\d+)["\']\s+name["\']fajhh["\']',
            r'fajhh\s*=\s*["\'](\d+)["\']',
            r'fajhh["\']?\s*:\s*["\']?(\d+)["\']?',
        )
        for pattern in patterns:
            match = re.search(pattern, page_text)
            if match:
                self.fxid = set_major_id(match.group(1))
                return self.fxid
        return ""

    def _update_major_id_from_query(self, raw_data):
        for key in ("yxkclist", "dateList"):
            raw_list = raw_data.get(key)
            if not raw_list:
                continue
            try:
                data_list = normalize_course_list(raw_list)
            except (json.JSONDecodeError, TypeError):
                continue
            if not data_list:
                continue
            first = data_list[0]
            major_id = first.get("programPlanNumber") or first.get("programPlanCode") or first.get("fajhh")
            if major_id:
                self.fxid = set_major_id(major_id)
                return self.fxid
        return self.fxid

    def _course_id(self, course):
        return "{}_{}_{}".format(course.get("kch", ""), course.get("kxh", ""), course.get("zxjxjhh", ""))

    def _course_match(self, expected, actual):
        return (
            expected.get("kcm") == actual.get("kcm")
            and expected.get("kch") == actual.get("kch")
            and expected.get("kxh") == actual.get("kxh")
            and expected.get("jasm") == actual.get("jasm")
        )

    def _remaining_seats(self, course):
        try:
            return int(course.get("bkskyl", 0))
        except (TypeError, ValueError):
            return 0

    def _query_course_list(self, keyword):
        query_data = query_class_data.copy()
        query_data["kcm"] = sanitize_text(keyword).strip()
        if not query_data["kcm"]:
            return [], "请输入课程名称"

        try:
            page = request_get(course_select_url)
        except requests.exceptions.RequestException as exc:
            return [], "网络错误：{}".format(exc)

        if page.status_code != 200 or page.text.find("自由选课") == -1:
            return [], "当前非选课阶段，或者教务处网站挂了，或者你的网络不行"

        self._extract_major_id_from_page(page.text)

        try:
            response = request_post(free_course_select_url, data=query_data)
        except requests.exceptions.RequestException as exc:
            return [], "网络错误：{}".format(exc)

        if response.status_code != 200 or not response.text.strip():
            return [], "获取课程列表失败，可能网络异常或登录过期"

        try:
            raw_data = json.loads(response.text)
            data_list = normalize_course_list(raw_data.get("rwRxkZlList"))
        except (json.JSONDecodeError, TypeError):
            return [], "课程列表响应格式异常，可能登录过期或被重定向"

        self._update_major_id_from_query(raw_data)
        return data_list, ""

    def _select_captcha_code(self):
        image = request_get(select_captcha_url).content
        with open(runtime_path("verify.jpg"), "wb") as photo:
            photo.write(image)
        code = self._get_ocr().classification(image)
        return code[-4:]

    def _submit_course(self, course, token):
        major_id = self.fxid or get_major_id()
        local_post = post_class_data.copy()
        local_post["kcIds"] = course.get("kcId") or self._course_id(course)
        local_post["kcms"] = encode_course_name("{}_{}".format(course.get("kcm", ""), course.get("kxh", "")))
        local_post["fajhh"] = major_id
        local_post["tokenValue"] = token
        local_post["inputCode"] = self._select_captcha_code()
        return request_post(course_submit_url, data=local_post)

    def show_course_in_table(self, data_list, sself):
        if not isinstance(data_list, list):
            data_list = [data_list]
        sself.ui.table.setRowCount(len(data_list))
        for idx, class_data in enumerate(data_list):
            class_uuid = str(class_data.get("kch", "?????????"))
            class_name = str(class_data.get("kcm", "未知课程名称, 数据错误!!!"))[:15]
            class_area = str(class_data.get("kkxqm", "未知"))
            class_free = str(class_data.get("bkskyl", "??"))
            room_build = str(class_data.get("jxlm", "????"))[:4]
            class_room = str(class_data.get("jasm", "未知地点"))[:4]
            class_week = str(class_data.get("zcsm", "????"))
            class_days = str(class_data.get("skxq", "8"))
            class_time = str(class_data.get("skjc", "??"))
            try:
                class_ends = str(int(class_time) + int(class_data.get("cxjc", 1)) - 1)
            except (TypeError, ValueError):
                class_ends = "0"
            class_teacher = str(class_data.get("skjs", "未知教师"))[:9]

            sself.ui.table.setItem(idx, 0, QTableWidgetItem(class_uuid))
            sself.ui.table.setItem(idx, 1, QTableWidgetItem(class_name))
            sself.ui.table.setItem(idx, 2, QTableWidgetItem(class_area))
            sself.ui.table.setItem(idx, 3, QTableWidgetItem(class_free))
            sself.ui.table.setItem(idx, 4, QTableWidgetItem(room_build))
            sself.ui.table.setItem(idx, 5, QTableWidgetItem(class_room))
            sself.ui.table.setItem(idx, 6, QTableWidgetItem(class_week))
            sself.ui.table.setItem(idx, 7, QTableWidgetItem(class_days))
            sself.ui.table.setItem(idx, 8, QTableWidgetItem(class_time + "-" + class_ends))
            sself.ui.table.setItem(idx, 9, QTableWidgetItem(class_teacher))

    def selectRes(self, sself):
        try:
            res_data = request_get(selected_courses_url)
        except requests.exceptions.RequestException as exc:
            self._message(sself, "[错误]", "网络错误：{}".format(exc))
            return -2

        try:
            json_data = json.loads(res_data.text)
        except json.JSONDecodeError:
            self._message(sself, "[错误]", "已选课程响应格式异常，可能登录过期")
            return -2

        try:
            date_list = json_data.get("dateList") or []
            if date_list:
                self.fxid = set_major_id(date_list[0].get("programPlanCode", self.fxid))
        except (TypeError, IndexError):
            pass

        xkxx = json_data.get("xkxx") or [{}]
        selected_map = xkxx[0] if xkxx and isinstance(xkxx[0], dict) else {}
        sself.ui.table.setRowCount(len(selected_map))
        for idx, course_key in enumerate(selected_map):
            course = selected_map[course_key]
            exam_type = course.get("examTypeName", "")
            teacher_name = str(course.get("attendClassTeacher", "未知")).split(" ")[0] or "未知"
            course_type = course.get("coursePropertiesName", "")
            week_desc = ""
            day = ""
            start_time = ""
            end_time = ""
            time_place_list = course.get("timeAndPlaceList") or []
            if time_place_list:
                time_place = time_place_list[0]
                week_desc = str(time_place.get("weekDescription", ""))
                day = str(time_place.get("classDay", ""))
                start_time = str(time_place.get("classSessions", ""))
                try:
                    end_time = str(int(start_time) + int(time_place.get("continuingSession", 1)) - 1)
                except (TypeError, ValueError):
                    end_time = "0"
            course_name = course.get("courseName", "")
            sself.ui.table.setItem(idx, 0, QTableWidgetItem(course_key))
            sself.ui.table.setItem(idx, 1, QTableWidgetItem(course_type))
            sself.ui.table.setItem(idx, 2, QTableWidgetItem(exam_type))
            sself.ui.table.setItem(idx, 3, QTableWidgetItem(teacher_name))
            sself.ui.table.setItem(idx, 4, QTableWidgetItem(week_desc))
            sself.ui.table.setItem(idx, 5, QTableWidgetItem(day))
            sself.ui.table.setItem(idx, 6, QTableWidgetItem(start_time + "-" + end_time))
            sself.ui.table.setItem(idx, 7, QTableWidgetItem(course_name))

    def query_course(self, sself):
        query_content = sself.ui.query_info.text()
        data_list, error = self._query_course_list(query_content)
        if error:
            self._message(sself, "[错误]", error)
            return -1

        self.data_list = data_list
        self.show_course_in_table(data_list, sself)
        return data_list

    def add_course(self, sself):
        selected_rows = list({item.row() for item in sself.ui.table.selectedItems()})
        if not selected_rows:
            self._message(sself, "[提示]", "请先选中要添加的课程")
            return -1

        selected_courses = []
        for row in selected_rows:
            if 0 <= row < len(self.data_list):
                course = dict(self.data_list[row])
                course["kcId"] = self._course_id(course)
                selected_courses.append(course)

        keyword = sanitize_text(sself.ui.query_info.text()).strip()
        self.data[keyword] = selected_courses
        self.numc[keyword] = len(selected_courses)
        self._message(sself, "[成功]", "成功将{}门课程添加进列表".format(len(selected_courses)))
        return selected_courses

    def start(self, sself):
        self._set_start_enabled(sself, False)
        try:
            loop_time = max(0.1, float(sself.ui.time.text() or 2))
        except ValueError:
            loop_time = 2

        if len(self.data) == 0:
            self._emit_message(sself, "[尚未添加课程]:请先添加课程，然后再重新开始抢课")
            self._set_start_enabled(sself, True)
            return -1

        visit = {}
        for courses in self.data.values():
            for course in courses:
                visit[course.get("kcId") or self._course_id(course)] = False

        count = 0
        begin_time = time.time()
        last_time = time.time()

        while any(not selected for selected in visit.values()):
            count += 1
            elapsed = time.time() - begin_time
            all_time = "{}时{}分{}秒".format(elapsed // 3600, (elapsed % 3600) // 60, (elapsed % 60) // 1)
            polling_ms = int((time.time() - last_time) * 1000)
            last_time = time.time()
            sself.communicate.top_bar.emit(
                " 当前次数：{} 总共耗时：{} 轮询速度：{}ms/次".format(count, all_time, polling_ms)
            )

            try:
                page = request_get(course_select_url)
                self._extract_major_id_from_page(page.text)
                token = self._extract_token(page.text)
            except requests.exceptions.RequestException as exc:
                self._emit_message(sself, "网络错误：{}".format(exc))
                time.sleep(loop_time)
                continue

            for keyword, courses in list(self.data.items()):
                class_list, error = self._query_course_list(keyword)
                if error:
                    self._emit_message(sself, error)
                    continue

                for expected in list(courses):
                    visit_key = expected.get("kcId") or self._course_id(expected)
                    if visit.get(visit_key):
                        continue

                    for current in class_list:
                        if not self._course_match(expected, current):
                            continue

                        self._show_running_course(sself, current)
                        if self._remaining_seats(current) <= 0:
                            break

                        current = dict(current)
                        current["kcId"] = visit_key
                        try:
                            submit_res = self._submit_course(current, token)
                        except requests.exceptions.RequestException as exc:
                            self._emit_message(sself, "网络错误：{}".format(exc))
                            break

                        if submit_res.text.find("ok") != -1:
                            visit[visit_key] = True
                            self._emit_message(sself, current.get("kcm", "课程") + "抢课成功")
                            courses.remove(expected)
                            if not courses:
                                self.data.pop(keyword, None)
                            break

                        if submit_res.text.find("错误") != -1 or submit_res.text.find("验证码") != -1:
                            self._emit_message(sself, "选课验证码识别失败，正在重新尝试")
                            break

                        self._emit_message(sself, current.get("kcm", "课程") + "抢课失败：" + submit_res.text[:100])
                        break

            time.sleep(max(loop_time, get_sleep_interval(loop_time)))

        self._emit_message(sself, "抢课全部结束")
        self._set_start_enabled(sself, True)
        return 0

    def delete(self, sself):
        selected_rows = list({item.row() for item in sself.ui.table.selectedItems()})
        if not selected_rows:
            self._message(sself, "[提示]", "请先选中要退掉的课程")
            return -1

        for row in selected_rows:
            try:
                page = request_get(course_quit_url)
            except requests.exceptions.RequestException as exc:
                self._message(sself, "[错误]", "网络错误：{}".format(exc))
                continue

            token = self._extract_token(page.text)
            course_item = sself.ui.table.item(row, 0)
            name_item = sself.ui.table.item(row, 7)
            if course_item is None:
                continue
            course = course_item.text().split("_")
            if len(course) < 2:
                continue

            data = {
                "fajhh": self.fxid or get_major_id(),
                "kch": course[0],
                "kxh": course[1],
                "tokenValue": token,
            }
            post_res = request_post(course_delete_url, data=data)
            if post_res.text.find("删除课程成功") != -1:
                name = name_item.text() if name_item is not None else course_item.text()
                self._message(sself, "[成功]", name + "删除成功")

        self.selectRes(sself)
        return 0
