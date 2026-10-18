from os import getenv, listdir

from requests import get, post
from json import loads

class TelegramManager:
    def __init__(self):
        self.apiHash = getenv("TELEGRAM_API_HASH")
        self.apiId = getenv("TELEGRAM_API_ID")
        self.botToken = getenv("BOT_TOKEN")
        self.baseUrl = f"http://localhost:8081/bot{self.botToken}"
        self.username = f"@{getenv("USERNAME")}"
        self.chatId = int(getenv("CHAT_ID"))
        self.documentsDir = None

    def getAuth(self):
        try:
            if(get(f"{self.baseUrl}/getMe").status_code == 200):
                return True
        except:
            return False
        return False

    def getChat(self):
        res = get(f"{self.baseUrl}/getChat?chat_id={self.chatId}")
        if(res.status_code == 200):
            return loads(res.text)

    def sendDocument(self, file):
        body = {
            "chat_id" : self.chatId
        }
        res = post(f"{self.baseUrl}/sendDocument",files={'document': file}, data=body)
        if(res.status_code == 200):
            return loads(res.text)

    def sendMessage(self, message):
        body = {
            "chat_id": self.chatId,
            "text": message
        }
        res = post(f"{self.baseUrl}/sendMessage", json=body)
        if res.status_code == 200:
            return loads(res.text)
        raise RuntimeError(res.text)

    def getDocument(self, file_id):
        filePath = loads(get(f"{self.baseUrl}/getFile?file_id={file_id}").text)["result"]["file_path"]
        return filePath
        