import json

from PySide2.QtUiTools import QUiLoader
from PySide2.QtWidgets import QLineEdit

from modules.ui_theme import add_card_shadow, polish_window
from modules.utils import load_config
from modules.userLogin import recognize_login_captcha, urp_setup, urp_login
from win.MenuWin import MenuWin


class LoginWin:

    def __init__(self):
        super().__init__()
        self.ui = QUiLoader().load('./ui/login.ui')
        polish_window(self.ui, 'SCU URP Helper - 登录')
        add_card_shadow(self.ui.loginCard)
        self.ui.label_4.setText('新版接口')
        self.ui.username.setPlaceholderText('请输入学号')
        self.ui.password.setPlaceholderText('请输入密码')
        self.ui.password.setEchoMode(QLineEdit.Password)
        self.ui.captcha.setPlaceholderText('验证码')
        self.ui.refresh_captcha_btn.setText('刷新验证码')
        self.ui.ocr_btn.setText('OCR识别')
        self.ui.btn_login.setText('登录系统')
        self.ui.captcha_pic.setScaledContents(True)
        self.menu_win = None
        self.ui.btn_login.clicked.connect(self.login)
        self.ui.refresh_captcha_btn.clicked.connect(self.refresh_captcha)
        self.ui.ocr_btn.clicked.connect(self.recognize_captcha)
        self.captcha_content = None
        self.readUser()
        self.ui.username.currentIndexChanged.connect(self.update_passwd)
        self.tokenval = urp_setup(self)
        self.username = ""
        self.password = ""
        self.captcha = ""

    def readUser(self):
        config = load_config()
        config_username = str(config.get('username') or '')
        config_password = str(config.get('password') or '')
        if config_username:
            if self.ui.username.findText(config_username) == -1:
                self.ui.username.addItem(config_username)
            self.ui.username.setCurrentText(config_username)
            self.ui.username.setEditText(config_username)
            self.ui.password.setText(config_password)

        try:
            with open('userinfo.json', 'r', encoding='utf-8') as user_file:
                user_data = json.load(user_file)
                for e_user in user_data['userList']:
                    username = e_user["username"]
                    if self.ui.username.findText(username) == -1:
                        self.ui.username.addItem(username)
                if not self.ui.username.currentText() and user_data['userList']:
                    first_user = user_data['userList'][0]
                    self.ui.username.setCurrentText(first_user.get('username', ''))
                    self.ui.username.setEditText(first_user.get('username', ''))
                    self.ui.password.setText(first_user.get('password', ''))
        except FileNotFoundError:
            print("找不到用户信息文件")
        except (KeyError, json.JSONDecodeError):
            print("用户信息文件格式错误")

    def update_passwd(self):
        idx = self.ui.username.currentIndex()
        if idx < 0:
            return
        try:
            with open('userinfo.json', 'r', encoding='utf-8') as user_file:
                user_data = json.load(user_file)
                username = self.ui.username.currentText()
                for item in user_data.get('userList', []):
                    if item.get('username') == username:
                        self.ui.password.setText(item.get('password', ''))
                        return
        except FileNotFoundError:
            print("找不到用户信息文件")
        except json.JSONDecodeError:
            print("用户信息文件格式错误")

    def login(self):
        if not self.tokenval:
            self.tokenval = urp_setup(self)
            if not self.tokenval:
                return
        login_res = urp_login(self)
        if login_res != 0:
            self.tokenval = urp_setup(self)
            self.ui.captcha.clear()
        else:
            self.menu_win = MenuWin()
            self.menu_win.ui.show()
            self.ui.close()

    def refresh_captcha(self):
        self.ui.captcha.clear()
        self.tokenval = urp_setup(self)

    def recognize_captcha(self):
        recognize_login_captcha(self)
