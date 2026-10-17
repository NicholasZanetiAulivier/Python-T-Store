from pathlib import Path,WindowsPath
import sqlite3

class DatabaseManager:

    DB_PATH = './data/db.sqlite3'

    def __init__(self):
        self.createDB()
        self.createTable()

        pass

    def __del__(self):
        self.connection.close()

    def createDB(self):
        path = Path(Path(__file__).parent.parent.parent.resolve(), DatabaseManager.DB_PATH)
        if not path.exists():
            path.parent.mkdir(exist_ok=True)
            path.touch(exist_ok=True)
        
        self.connection = sqlite3.connect(DatabaseManager.DB_PATH)
        return True

    def runQuery(self, query: str, args: tuple = None):
        cursor = self.connection.cursor()
        try:
            if args == None:
                cursor.execute(query)
            else:
                cursor.execute(query, args)
        except:
            raise RuntimeError(f"Failed to run query {query}")
        self.connection.commit()
        return cursor.fetchall()


    def createTable(self):

        self.runQuery(
            """
            CREATE TABLE IF NOT EXISTS files (
                file_name TEXT NOT NULL,
                created_at DATETIME NOT NULL,
                size_bytes UNSIGNED BIG INT NOT NULL
            )
            """
        )