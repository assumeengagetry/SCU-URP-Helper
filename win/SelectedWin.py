from PySide2.QtUiTools import QUiLoader

from modules.ui_theme import add_card_shadow, polish_table, polish_window


class SelectedWin:
    def __init__(self, sself):
        super().__init__()
        self.ui = QUiLoader().load('./ui/selected.ui')
        polish_window(self.ui, 'SCU URP Helper - 选课结果')
        add_card_shadow(self.ui.toolbarCard)
        self.ui.table.setColumnCount(8)
        self.ui.table.setHorizontalHeaderLabels(["课程号", "属性", "方式", "教师", "周数", "星期", "时间", "课程"])
        polish_table(self.ui.table)
        self.ui.delete_btn.clicked.connect(self.delete)
        self.course_grabbing = sself.course_grabbing
        self.course_grabbing.selectRes(self)

    def delete(self):
        self.course_grabbing.delete(self)
