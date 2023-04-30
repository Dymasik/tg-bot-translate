import sqlite3


class SQLite:
    def __init__(self, database):
        self.connection = sqlite3.connect(database, check_same_thread=False)
        self.cursor = self.connection.cursor()
        with self.connection:
            self.cursor.execute("""CREATE TABLE IF NOT EXISTS words (
                                        user text NOT NULL,
                                        word text NOT NULL
                                    ); """)
            self.cursor.execute("""CREATE TABLE IF NOT EXISTS texts (
                                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                                        saved_text text NOT NULL
                                    ); """)
            
    def save_text(self, text):
        with self.connection:
            entry = self.cursor.execute("INSERT INTO texts (saved_text) VALUES (?)",
                                        (text,))
            print(f"Text entry created {entry.lastrowid}")
            return entry.lastrowid
        
    def get_text(self, id):
        with self.connection:
            entry = self.cursor.execute("SELECT saved_text FROM texts WHERE id = ?",
                                        (id,))
            return str(entry.fetchall()[0])

    def create_entry(self, user_id, text):
        with self.connection:
            entry = self.cursor.execute("INSERT INTO words (user, word) VALUES (?, ?)",
                                        (str(user_id), text))
            print("Translation entry created")
            return entry
        
    def saved_exists(self, user_id):
        result = self.cursor.execute("SELECT * FROM words WHERE user = ?", (str(user_id),)).fetchall()
        print("Entry existence checked: ")
        print(bool(len(result)))
        return bool(len(result))

    def select_saved(self, user_id):
        with self.connection:
            print("Started selecting saved words.")
            entry = self.cursor.execute("SELECT word FROM words WHERE user = ?", (str(user_id),))
            print("Finished.")
            return entry

    def close(self):
        self.connection.close()
