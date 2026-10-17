from PySide6.QtWidgets import QWidget, QPushButton, QLabel, QPlainTextEdit, QTableWidget
from managers.DatabaseManager import DatabaseManager

class FilesManager:
    def __init__(self, files: QWidget, sendSignal):
        self.db: DatabaseManager = DatabaseManager()

        self.sendSignal = sendSignal
        
        self.page: QWidget = files
        
        self.uploadTab: QWidget = self.page.uploadTab

        self.uploadButton: QPushButton = self.page.uploadButton
        self.status: QLabel = self.page.status
        self.fileName: QPlainTextEdit = self.page.fileName
        self.extention: QLabel = self.page.extention
        self.fileSize: QLabel = self.page.fileSize
        self.confirmButton: QPushButton = self.page.confirmButton
        
        self.downloadTab: QWidget = self.page.downloadTab
        
        self.search: QPlainTextEdit = self.page.search
        self.searchButton: QPushButton = self.page.searchButton
        self.table: QTableWidget = self.page.table

    def show(self):
            self.page.show()
    
    def close(self):
        self.page.setVisible(False)
