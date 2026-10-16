from PySide6.QtUiTools import QUiLoader
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QFile, QIODevice

class Application(QApplication):
    LOGIN_SRC: str = "src/widgets/loginPage.ui"

    loader:QUiLoader = QUiLoader()

    def __init__(self, /, *, cursorFlashTime = ..., doubleClickInterval = ..., keyboardInputInterval = ..., wheelScrollLines = ..., startDragTime = ..., startDragDistance = ..., styleSheet = ..., autoSipEnabled = ...):
        super().__init__(cursorFlashTime=cursorFlashTime, doubleClickInterval=doubleClickInterval, keyboardInputInterval=keyboardInputInterval, wheelScrollLines=wheelScrollLines, startDragTime=startDragTime, startDragDistance=startDragDistance, styleSheet=styleSheet, autoSipEnabled=autoSipEnabled)
        self.login = Application.loadUiFile(Application.LOGIN_SRC)

    def loadUiFile(source: str, width: int = 800, height: int = 600):
        file = QFile(source)
        print(source)
        if not file.open(QIODevice.ReadOnly):
           raise RuntimeError(f"Cannot open {source}: {file.errorString()}")
        data = Application.loader.load(file)
        data.setFixedSize(width,height)
        file.close()
        if not data:
            raise RuntimeError(Application.loader.errorString())
        return data

    def runApp(self):
        self.login.show()
        return self.exec()