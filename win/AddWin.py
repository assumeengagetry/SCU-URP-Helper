from PySide2.QtUiTools import QUiLoader

from modules.ui_theme import add_card_shadow, polish_table, polish_window


class AddWin:
    def __init__(self, sself):
        super().__init__()
        self.ui = QUiLoader().load('./ui/add.ui')
        polish_window(self.ui, 'SCU URP Helper - 添加课程')
        add_card_shadow(self.ui.toolbarCard)
        self.ui.table.setColumnCount(10)
        self.ui.table.setHorizontalHeaderLabels(["课程编号", "课程名", "校区", "课余量", "位置", "教室", "周数", "星期", "时间", "教师"])
        polish_table(self.ui.table)
        self.ui.query_info.setPlaceholderText('输入课程关键词，例如：大数据')
        self.ui.query_btn.clicked.connect(self.query)
        self.ui.add_btn.clicked.connect(self.add_course)
        self.query_content = self.ui.query_info.text()
        self.course_grabbing = sself.course_grabbing
        self.selected_row = self.ui.table.selectedItems()


    def query(self):
        self.course_grabbing.query_course(self)

    def add_course(self):
        self.course_grabbing.add_course(self)
