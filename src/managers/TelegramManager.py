from os import getenv

from requests import get, post
from json import loads

class TelegramManager:
    def __init__(self):
        self.apiHash = getenv("TELEGRAM_API_HASH")
        self.apiId = getenv("TELEGRAM_API_ID")
        self.botToken = getenv("BOT_TOKEN")
        self.baseUrl = f"http://localhost:8081/bot{self.botToken}"

    def getAuth(self):
        try:
            if(get(f"{self.baseUrl}/getMe").status_code == 200):
                return True
        except:
            return False
        return False