
import os
import sys

from PySide2 import QtWidgets

from modules.ui_theme import set_app_theme
from win.LoginWin import LoginWin


if __name__ == '__main__':
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    app = QtWidgets.QApplication(sys.argv)
    set_app_theme(app)
    login_win = LoginWin()
    login_win.ui.show()
    sys.exit(app.exec_())
