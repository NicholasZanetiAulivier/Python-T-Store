from io import FileIO
from os.path import getsize
from pathlib import Path
from enum import Enum
from time import sleep

from PySide6.QtWidgets import QWidget, QPushButton, QLabel, QLineEdit, QTableWidget, QTabWidget, QFileDialog
from PySide6.QtCore import Slot
from pathvalidate import is_valid_filename
from managers.DatabaseManager import DatabaseManager
from managers.TelegramManager import TelegramManager


class UploadState(Enum):
    NO_FILE = 1
    FILE_UPLOADED = 2
    DUPLICATE_FILE_NAME = 3
    INVALID_FILE_NAME = 4 
    UPLOAD_SUCCESS = 5
    UPLOAD_FAIL = 6

class FilesManager:
    db: DatabaseManager = DatabaseManager()
    tg: TelegramManager = TelegramManager()


    def __init__(self, files: QWidget, sendSignal):
        self.sendSignal = sendSignal

        self.currentSize: int = 0
        self.currentName: str = ""
        self.currentFile: FileIO =None
        
        self.page: QWidget = files

        self.tabs: QTabWidget = self.page.tabs
        
        self.uploadTab: QWidget = self.page.uploadTab

        self.uploadButton: QPushButton = self.page.uploadButton
        self.status: QLabel = self.page.status
        self.fileName: QLineEdit = self.page.fileName
        self.fileSize: QLabel = self.page.fileSize
        self.confirmButton: QPushButton = self.page.confirmButton
        
        self.downloadTab: QWidget = self.page.downloadTab
        
        self.search: QLineEdit = self.page.search
        self.searchButton: QPushButton = self.page.searchButton
        self.table: QTableWidget = self.page.table

        self.tabs.currentChanged.connect(self.changeTab)

        self.uploadButton.clicked.connect(self.openFileDialog)
        self.confirmButton.clicked.connect(self.handleConfirm)

        self.setUploadState(UploadState.NO_FILE)

        attempts = 100
        while not FilesManager.tg.getAuth():
            if attempts <= 0:
                raise RuntimeError("Local Telegram Bot API was unable to be accessed")
            sleep(0.5)
            attempts -= 1
        if not FilesManager.tg.sendMessage("Bot initialized"):
            raise RuntimeError("Unable to send a basic message")

    def __del__(self):
        if(self.currentFile):
            self.currentFile.close()

    def show(self):
            self.page.show()
    
    def close(self):
        self.page.setVisible(False)

    def setUploadState(self, state: UploadState):
        match state:
            case UploadState.NO_FILE:
                self.fileName.setText("")
                self.fileName.setEnabled(False)
                self.status.setText("No file")
                self.fileSize.setText("-")
                self.confirmButton.setEnabled(False)
            case UploadState.DUPLICATE_FILE_NAME:
                self.fileName.setEnabled(True)
                self.status.setText("Another file has already been uploaded by that name")
                self.fileSize.setText(f"{self.currentSize} bytes")
                self.confirmButton.setEnabled(True)
            case UploadState.FILE_UPLOADED:
                self.fileName.setText(self.currentName)
                self.fileName.setEnabled(True)
                self.status.setText("File has been picked")
                self.fileSize.setText(f"{self.currentSize} bytes")
                self.confirmButton.setEnabled(True)
            case UploadState.INVALID_FILE_NAME:
                self.fileName.setEnabled(True)
                self.status.setText("File name is invalid")
                self.fileSize.setText(f"{self.currentSize} bytes")
                self.confirmButton.setEnabled(True)
            case UploadState.UPLOAD_SUCCESS:
                self.fileName.setEnabled(False)
                self.status.setText("File has successfully been uploaded")
                self.fileSize.setText("-")
                self.confirmButton.setEnabled(False)
            case UploadState.UPLOAD_FAIL:
                self.fileName.setEnabled(False)
                self.status.setText("File failed to upload. Try again")
                self.fileSize.setText("-")
                self.confirmButton.setEnabled(False)

    def openFileDialog(self):
        dialog = QFileDialog(self.page)
        dialog.setFileMode(QFileDialog.FileMode.ExistingFile)
        dialog.setViewMode(QFileDialog.ViewMode.List)
        fileNames: list[str] = None

        if dialog.exec():
            fileNames = dialog.selectedFiles()
        
        if fileNames:
            self.currentFile = open(fileNames[0], 'rb')
            self.currentSize = getsize(fileNames[0]);
            self.currentName = Path(fileNames[0]).name
            self.setUploadState(UploadState.FILE_UPLOADED)
        else:
            self.setUploadState(UploadState.UPLOAD_FAIL)
        pass

    def handleConfirm(self):
        self.currentName = self.fileName.text()
        self.confirmButton.setEnabled(False)

        cases = [
            self.checkForDuplicateFileName(),
            self.checkForInvalidFileName(),
        ]

        if not all(cases):
            return
        
        self.confirmButton.setEnabled(True)
        


    def checkForInvalidFileName(self) -> bool:
        if not is_valid_filename(self.currentName):
            self.setUploadState(UploadState.INVALID_FILE_NAME)
            return False
        return True

    def checkForDuplicateFileName(self) -> bool:
        db = FilesManager.db
        res = db.runQuery(
            """
            SELECT file_name FROM files WHERE file_name = ?
            """,
            [self.currentName]
        )
        if len(res) > 0:
            self.setUploadState(UploadState.DUPLICATE_FILE_NAME)
            return False
        return True

    def uploadFile(self):
        pass


    @Slot(int)
    def changeTab(self, id):
        if id == 0:
            self.setUploadState(UploadState.NO_FILE)
        elif id == 1 :
            pass