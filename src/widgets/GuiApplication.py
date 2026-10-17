from PySide6.QtUiTools import QUiLoader
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QFile, QIODevice
from managers.LoginManager import LoginManager
from managers.FilesManager import FilesManager

class Application(QApplication):

    #Constants
    LOGIN_SRC: str = "src/widgets/loginPage.ui"
    FILE_MANAGEMENT_SRC: str = "src/widgets/contentPage.ui"

    loader:QUiLoader = QUiLoader()

    #Managers
    loginManager: LoginManager = None
    filesManager: FilesManager = None

    def __init__(self, /, *, cursorFlashTime = ..., doubleClickInterval = ..., keyboardInputInterval = ..., wheelScrollLines = ..., startDragTime = ..., startDragDistance = ..., styleSheet = ..., autoSipEnabled = ...):
        super().__init__(cursorFlashTime=cursorFlashTime, doubleClickInterval=doubleClickInterval, keyboardInputInterval=keyboardInputInterval, wheelScrollLines=wheelScrollLines, startDragTime=startDragTime, startDragDistance=startDragDistance, styleSheet=styleSheet, autoSipEnabled=autoSipEnabled)
        login = Application.loadUiFile(Application.LOGIN_SRC)
        self.loginManager = LoginManager(login, self.signal)
        files = Application.loadUiFile(Application.FILE_MANAGEMENT_SRC)
        self.filesManager = FilesManager(files, self.signal)

    def loadUiFile(source: str, width: int = 800, height: int = 600):
        file = QFile(source)
        if not file.open(QIODevice.ReadOnly):
           raise RuntimeError(f"Cannot open {source}: {file.errorString()}")
        data = Application.loader.load(file)
        data.setFixedSize(width,height)
        file.close()
        if not data:
            raise RuntimeError(Application.loader.errorString())
        return data

    def signal(self, sig: int):
        match sig:
            case LoginManager.SUCCESSFUL_LOGIN:
                self.filesManager.show()
                self.loginManager.close()

    def runApp(self):
        self.loginManager.show()
        return self.exec()