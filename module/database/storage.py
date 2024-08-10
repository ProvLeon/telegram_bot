import datetime
import sqlite3

class Database:
    def __init__(self, db_name='subscribers.db'):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self.create_table()
        self.alter_reminders_table()


    def create_table(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS subscribers (
                user_id INTEGER PRIMARY KEY,
                subscribed BOOLEAN
            )
        ''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS reminders (
                reminder_time TEXT,
                class_name TEXT,
                platform_info TEXT
                concepts TEXT
            )
        ''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS discussions (
                date Date,
                topic TEXT
            )
        ''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS discussion_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                username TEXT,
                message TEXT
                )
        ''')
        self.conn.commit()


    def alter_reminders_table(self):
        try:
            self.cursor.execute('ALTER TABLE reminders ADD COLUMN concepts TEXT')
            self.conn.commit()
        except sqlite3.OperationalError:
            # Column already exists, do nothing
            pass


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

    def add_reminder(self, reminder_time, class_name, platform_info, concepts):
        self.cursor.execute('INSERT INTO reminders (reminder_time, class_name, platform_info, concepts) VALUES (?,?,?,?)',
                            (reminder_time, class_name, platform_info, concepts))
        self.conn.commit()


    def get_reminders(self):
        self.cursor.execute('SELECT reminder_time, class_name, platform_info, concepts FROM reminders')
        return [{'time': row[0],
                 'class_name': row[1],
                 'platform_info': row[2] if len(row) > 2 else None,
                 'concepts': row[3] if len(row) > 3 else None}
                for row in self.cursor.fetchall()]

    def add_discussion(self, topic):
        date = datetime.date.today()
        self.cursor.execute('INSERT INTO discussions (date, topic) VALUES (?, ?)', (date, topic))
        self.conn.commit()

    def get_discussions(self):
        self.cursor.execute('SELECT date, topic FROM discussions ORDER BY date DESC LIMIT 1')
        row = self.cursor.fetchone()
        return {'date': row[0], 'topic': row[1]} if row else None
    #def remove_discussion(self):
    #    self.cursor.execute('DELETE FROM discussions')
    #    self.conn.commit()

    def add_message_to_history(self, user_id, username, message):
        self.cursor.execute('INSERT INTO discussion_history (user_id, username, message) VALUES (?, ?, ?)', (user_id, username, message))
        self.conn.commit()

    def get_discussion_history(self):
        self.cursor.execute('SELECT user_id, username, message FROM discussion_history ORDER BY id DESC LIMIT 10')
        return [{'user_id': row[0], 'username': row[1], 'message': row[2]} for row in self.cursor.fetchall()]

    def remove_discussion(self):
        self.cursor.execute('DELETE FROM discussions')
        self.cursor.execute('DELETE FROM discussion_history')
        self.conn.commit()

    def clear_database(self):
        self.cursor.execute('DROP TABLE IF EXISTS subscribers')
        self.cursor.execute('DROP TABLE IF EXISTS reminders')
        self.cursor.execute('DROP TABLE IF EXISTS discussions')
        self.cursor.execute('DROP TABLE IF EXISTS discussion_history')
        self.conn.commit()
        self.create_table()
        self.alter_reminders_table()


    def close(self):
        self.conn.close()

db = Database()
