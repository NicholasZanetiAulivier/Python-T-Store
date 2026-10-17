from PySide6.QtWidgets import QWidget, QPlainTextEdit, QPushButton, QVBoxLayout, QLabel
from PySide6.QtCore import Slot

class LoginManager:

    SUCCESSFUL_LOGIN: int = 1

    def __init__(self, loginPage: QWidget, sendSignal):
        self.sendSignal = sendSignal

        self.page: QWidget = loginPage
        
        self.title: QLabel = self.page.title
        self.loginButton: QPushButton = self.page.loginButton
        self.password: QPlainTextEdit = self.page.password

        self.loginButton.clicked.connect(self.login)

    def show(self):
        self.page.show()

    def close(self):
        self.page.setVisible(False)
    
    @Slot()
    def login(self):
        self.sendSignal(self.SUCCESSFUL_LOGIN)