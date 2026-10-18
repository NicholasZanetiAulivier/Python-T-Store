from io import FileIO
from os.path import getsize
from pathlib import Path
from enum import Enum
from time import sleep
from datetime import datetime
from functools import partial
from os import getenv, path, remove

from PySide6.QtWidgets import QWidget, QPushButton, QLabel, QLineEdit, QTableWidget, QTabWidget, QFileDialog, QTableWidgetItem
from PySide6.QtCore import Slot, Qt
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
    UPLOADING = 7

class FilesManager:
    FILE_PARTS_MAX_SIZE= 1992294400

    db: DatabaseManager = DatabaseManager()
    tg: TelegramManager = TelegramManager()


    def __init__(self, files: QWidget, sendSignal):
        self.sendSignal = sendSignal

        self.downloadLocation: str = getenv("DOWNLOAD_DIRECTORY")

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
        self.searchButton.clicked.connect(lambda: self.loadFileList(self.search.text()))

        self.setUploadState(UploadState.NO_FILE)

        attempts = 100
        while not FilesManager.tg.getAuth():
            if attempts <= 0:
                raise RuntimeError("Local Telegram Bot API was unable to be accessed")
            sleep(0.5)
            attempts -= 1
        self.loadFileList()

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
            case UploadState.UPLOADING:
                self.fileName.setEnabled(False)
                self.status.setText("File is being uploaded, please wait")
                self.fileSize.setText(f"{self.currentSize} bytes")
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
        try:
            self.currentName = self.fileName.text()
            self.setUploadState(UploadState.UPLOADING)

            cases = [
                self.checkForDuplicateFileName(),
                self.checkForInvalidFileName(),
            ]

            if not all(cases):
                return

            res = self.uploadFile()
            
            self.setUploadState(UploadState.UPLOAD_SUCCESS)
        except:
            self.setUploadState(UploadState.UPLOAD_FAIL)
            FilesManager.db.rollback()

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
        newFileId = FilesManager.db.runQuery(
            """
            INSERT INTO files(file_name, created_at, size_bytes) VALUES (?,?,?) RETURNING rowid
            """,
            [self.currentName, datetime.now(), self.currentSize]
        )[0][0]
        
        curr = self.currentSize
        order = 1
        while curr > 0:
            part = self.currentFile.read(self.FILE_PARTS_MAX_SIZE)
            curr -= self.FILE_PARTS_MAX_SIZE
            res = FilesManager.tg.sendDocument(part)
            if res == None:
                raise RuntimeError("Unable to upload file")

            doc = res["result"]["document"]

            FilesManager.db.runQuery(
                """
                INSERT INTO file_parts(file_id, part_id, part_unique_id, size_bytes, part_order) 
                VALUES(?,?,?,?,?)
                """,
                [newFileId, doc["file_id"], doc["file_unique_id"], doc["file_size"], order]
            )
            order += 1
        FilesManager.db.commit()
        self.loadFileList(self.search.text())

    def loadFileList(self, search = None):
        res = None
        if search == None or len(str(search)) <= 0:
            res = FilesManager.db.runQuery(
                """
                SELECT created_at, file_name, size_bytes, rowid FROM files
                """
            )
        else:
            res = FilesManager.db.runQuery(
                """
                SELECT created_at, file_name, size_bytes, rowid FROM files WHERE file_name REGEXP ?
                """,
                [search]
            )

        self.table.setRowCount(len(res))
        if(len(res) <= 0):
            self.table.setColumnCount(5)
            self.table.verticalHeader().setVisible(False)
            self.table.setHorizontalHeaderLabels(["Uploaded At", "File Name", "Byte Size", "Download", "Delete"])
            self.table.resizeColumnsToContents()
            self.table.resizeRowsToContents()
            self.table.setAlternatingRowColors(True)
            return
        
        self.table.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        for i in range(len(res)):
            for j in range(len(res[0])-1):
                self.table.setItem(i, j, QTableWidgetItem(str(res[i][j])))
            fileId = res[i][3]
            downloadButton = QPushButton(self.table)
            downloadButton.setText("Download")
            downloadButton.clicked.connect(partial(self.handleDownload, fileId))
            self.table.setCellWidget(i,3,downloadButton)

            deleteButton = QPushButton(self.table)
            deleteButton.setText("Delete")
            deleteButton.clicked.connect(partial(self.handleDelete, fileId))
            self.table.setCellWidget(i,4,deleteButton)
        pass
        self.table.resizeColumnsToContents()
        self.table.resizeRowsToContents()
        self.table.setAlternatingRowColors(True)

    def handleDelete(self, id):
        FilesManager.db.runQuery(
            """
            DELETE FROM file_parts WHERE file_id = ?
            """,
            [id]
        )

        FilesManager.db.runQuery(
            """
            DELETE FROM files WHERE rowid = ?
            """,
            [id]
        )

        FilesManager.db.commit()
        self.loadFileList(self.search.text())

    def handleDownload(self, id):

        parts = FilesManager.db.runQuery(
            """
            SELECT part_id, part_order FROM file_parts WHERE file_id= ? ORDER BY part_order ASC 
            """,
            [id]
        )
        fileName = FilesManager.db.runQuery(
            """
            SELECT file_name FROM files WHERE rowid = ?
            """,
            [id]
        )[0][0]
        downloadPath = f"{self.downloadLocation}/{fileName}"
        num = 1
        while path.exists(downloadPath):
            downloadPath = f"{self.downloadLocation}/{num}{fileName}"
            num += 1

        for row in parts:
            pathId = row[0]
            partDocument = FilesManager.tg.getDocument(pathId)
            with open(downloadPath, "ab") as downloadedFile:
                with open(partDocument, "rb") as partFile:
                    downloadedFile.write(partFile.read())
                remove(partDocument)
        print("Download done")
        
    @Slot(int)
    def changeTab(self, id):
        if id == 0:
            pass
        elif id == 1 :
            pass