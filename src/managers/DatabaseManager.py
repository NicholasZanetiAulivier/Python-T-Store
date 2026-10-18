from pathlib import Path
import sqlite3
import re

class DatabaseManager:

    DB_PATH = './data/db.sqlite3'

    def __init__(self):
        self.createDB()
        self.createTable()

        pass

    def __del__(self):
        self.connection.rollback()
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
        return cursor.fetchall()


    def createTable(self):
        self.runQuery("PRAGMA foreign_keys = ON")

        self.runQuery(
            """
            CREATE TABLE IF NOT EXISTS files (
                rowid INTEGER NOT NULL PRIMARY KEY,
                file_name TEXT NOT NULL,
                created_at DATETIME NOT NULL,
                size_bytes UNSIGNED BIG INT NOT NULL
            )
            """
        )

        self.runQuery(
            """
            CREATE TABLE IF NOT EXISTS file_parts(
                file_id INTEGER NOT NULL,
                part_id TEXT NOT NULL,
                part_unique_id TEXT NOT NULL,
                size_bytes UNSIGNED BIG INT NOT NULL,
                part_order INTEGER NOT NULL,
                FOREIGN KEY (file_id) REFERENCES files(rowid),
                UNIQUE (file_id, part_order)
            )
            """
        )

        # Define a custom regex function
        def regexp(pattern, item):
            return re.search(pattern, item) is not None

        # Register the regexp function with SQLite
        self.connection.create_function("REGEXP", 2, regexp)
        self.commit()

    def commit(self):
        self.connection.commit()

    def rollback(self):
        self.connection.rollback()