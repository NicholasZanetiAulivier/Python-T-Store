from PySide6.QtWidgets import QWidget, QLineEdit, QPushButton, QLabel
from PySide6.QtCore import Slot
from os import getenv
from bcrypt import checkpw

class LoginManager:

    SUCCESSFUL_LOGIN: int = 1

    def __init__(self, loginPage: QWidget, sendSignal):
        self.passwordHash = getenv("PASSWORD_HASH")

        if not self.passwordHash:
            raise RuntimeError("PASSWORD_HASH must be set")

        self.sendSignal = sendSignal

        self.page: QWidget = loginPage
        
        self.title: QLabel = self.page.title
        self.loginButton: QPushButton = self.page.loginButton
        self.password: QLineEdit = self.page.password

        self.loginButton.clicked.connect(self.login)
        self.password.returnPressed.connect(self.login)

    def show(self):
        self.page.show()

    def close(self):
        self.page.setVisible(False)
    
    @Slot()
    def login(self):
        if checkpw(self.password.text().encode('utf-8'), self.passwordHash.encode('utf-8')):
            self.sendSignal(self.SUCCESSFUL_LOGIN)
        else:
            self.title.setText("LOGIN FAILED!")
            self.password.setText("")