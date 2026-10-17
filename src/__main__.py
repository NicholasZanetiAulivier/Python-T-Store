import sys
from dotenv import load_dotenv
from PySide6 import QtWidgets

from botapi.bot import BotAPIProcess
from widgets.GuiApplication import Application

telegramProcess: BotAPIProcess = None

if __name__ == "__main__":
    #Load env
    load_dotenv()

    #Start telegram bot API
    telegramProcess = BotAPIProcess()
    telegramProcess.startBot()

    try:
        #Start App
        app = Application()
        returnCode = app.runApp()
        telegramProcess.stopBot()
        sys.exit(returnCode)
    except:
        telegramProcess.stopBot()