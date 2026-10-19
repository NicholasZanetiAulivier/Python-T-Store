import sys
from dotenv import load_dotenv

from botapi.bot import BotAPIProcess
from widgets.GuiApplication import Application

telegramProcess: BotAPIProcess = None

def main():
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
            app.filesManager.__del__()
            telegramProcess.stopBot()
            sys.exit(returnCode)
        finally:
            telegramProcess.stopBot()
            del telegramProcess
            pass

main()