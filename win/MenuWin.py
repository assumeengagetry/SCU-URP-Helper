from PySide2.QtUiTools import QUiLoader

from modules.AutoCourseGrabbing import AutoCourseGrabbing
from win.AddWin import AddWin
from win.SelectedWin import SelectedWin
from win.StartWin import StartWin


class MenuWin:
    def __init__(self):
        super().__init__()
        self.ui = QUiLoader().load('./ui/menu.ui')
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
