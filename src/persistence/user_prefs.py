import abc
import logging
import sqlite3


class UserPrefs:
    user_id: str
    respond_to_testing: bool

    def __init__(self, user_id: str):
        self.user_id = user_id
        self.respond_to_testing = False


class AbstractUserPrefsPersistence(abc.ABC):
    @abc.abstractmethod
    def get_user_prefs(self, user_id: str) -> UserPrefs:
        pass

    @abc.abstractmethod
    def persist_user_prefs(self, user_id: str, user_prefs: UserPrefs):
        pass


class SqliteUserPrefsPersistence(AbstractUserPrefsPersistence):
    db_path: str

    def __init__(self, db_path: str):
        self.db_path = db_path
        self._initialize_db()

    def _initialize_db(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_prefs (
                    user_id TEXT PRIMARY KEY,
                    respond_to_testing BOOLEAN
                )
            ''')
            conn.commit()

        logging.info('Connected to user prefs DB at ' + self.db_path)

    def get_user_prefs(self, user_id: str) -> UserPrefs:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT respond_to_testing FROM user_prefs WHERE user_id = ?', (user_id,))
            row = cursor.fetchone()
            if row:
                user_prefs = UserPrefs(user_id)
                user_prefs.respond_to_testing = bool(row[0])
                return user_prefs
            else:
                return UserPrefs(user_id)

    def persist_user_prefs(self, user_id: str, user_prefs: UserPrefs):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO user_prefs (user_id, respond_to_testing)
                VALUES (?, ?)
                ON CONFLICT(user_id) DO UPDATE SET
                respond_to_testing=excluded.respond_to_testing
            ''', (user_id, user_prefs.respond_to_testing))
            conn.commit()
