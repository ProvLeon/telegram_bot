import sqlite3

class Database:
    def __init__(self, db_name='subscribers.db'):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self.create_table()

    def create_table(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS subscribers (
                user_id INTEGER PRIMARY KEY,
                subscribed BOOLEAN
            )
        ''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS reminders (
                user_id INTEGER,
                reminder_time TEXT,
                class_name TEXT,
                platform_info TEXT
            )
        ''')
        self.conn.commit()


    def subscribe(self, user_id):
        self.cursor.execute('INSERT OR REPLACE INTO subscribers (user_id, subscribed) VALUES (?, ?)', (user_id, True))
        self.conn.commit()
    def unsubscribe(self, user_id):
        self.cursor.execute('DELETE FROM subscribers WHERE user_id = ?', (user_id,))
        self.conn.commit()

    def is_subscribed(self, user_id):
        self.cursor.execute('SELECT subscribed FROM subscribers WHERE user_id = ?', (user_id,))
        result = self.cursor.fetchone()
        return result[0] if result else False

    def get_all_subscribers(self):
        self.cursor.execute('SELECT user_id FROM subscribers WHERE subscribed = ?', (True,))
        return [row[0] for row in self.cursor.fetchall()]

    def add_reminder(self, user_id, reminder_time, class_name, platform_info):
        self.cursor.execute('INSERT INTO reminders (user_id, reminder_time, class_name, platform_info) VALUES (?,?,?, ?)', (user_id, reminder_time, class_name, platform_info))
        self.conn.commit()

    def get_reminders(self, user_id):
        self.cursor.execute('SELECT reminder_time, class_name FROM reminders WHERE user_id = ?', (user_id,))
        return [{'time': row[0], 'class_name': row[1]} for row in self.cursor.fetchall()]

    def clear_database(self):
        self.cursor.execute('DROP TABLE IF EXISTS subscribers')
        self.cursor.execute('DROP TABLE IF EXISTS reminders')
        self.conn.commit()
        self.create_table()


    def close(self):
        self.conn.close()

db = Database()
