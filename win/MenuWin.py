from PySide2.QtUiTools import QUiLoader

from modules.AutoCourseGrabbing import AutoCourseGrabbing
from modules.ui_theme import add_card_shadow, polish_window
from win.AddWin import AddWin
from win.SelectedWin import SelectedWin
from win.StartWin import StartWin


class MenuWin:
    def __init__(self):
        super().__init__()
        self.ui = QUiLoader().load('./ui/menu.ui')
        polish_window(self.ui, 'SCU URP Helper - 菜单')
        add_card_shadow(self.ui.menuCard)
        self.ui.label_4.setText('新版接口')
        self.ui.add_btn.setText('添加课程')
        self.ui.start_btn.setText('开始抢课')
        self.ui.query_btn.setText('选课结果')
        self.ui.add_btn.clicked.connect(self.go_add)
        self.ui.query_btn.clicked.connect(self.go_selected)
        self.ui.start_btn.clicked.connect(self.go_start)
        self.course_grabbing = AutoCourseGrabbing()
        self.add_win = None
        self.selected_win = None
        self.start_win = None


    def go_selected(self):
        """
        已选课程
        :return:
        """
        self.selected_win = SelectedWin(self)
        self.selected_win.ui.show()


    def go_add(self):
        """
        添加课程
        :return:
        """
        self.add_win = AddWin(self)
        self.add_win.ui.show()

    def go_start(self):
        """
        开始抢课
        :return:
        """
        self.start_win = StartWin(self)
        self.start_win.ui.show()
