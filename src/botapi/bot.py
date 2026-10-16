from subprocess import Popen, PIPE
from signal import CTRL_C_EVENT
from time import sleep
from dotenv import load_dotenv, dotenv_values
from os import getenv

class BotAPIProcess:

    def __init__(self):
        pass

    def startBot(self):
        process : Popen = Popen(
            [
                "telegram-bot-api/bin/telegram-bot-api.exe", 
                f"--api-id={getenv("TELEGRAM_API_ID")}",
                f"--api-hash={getenv("TELEGRAM_API_HASH")}"
                ],
            stdout=PIPE,
            text=True
        )
        self.process: Popen = process

    def stopBot(self):
        if self.process != None:
            self.process.terminate()


if __name__=="__main__":
    load_dotenv()

    api = BotAPIProcess()
    api.startBot()
    
    sleep(5)
    api.process.terminate()
    sleep(5)
    
    print(api.process.returncode)
