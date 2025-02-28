import abc
import logging
import sqlite3
from datetime import datetime


class UserPrefs:
    class Preference:
        value: any
        _time_set: datetime
        _num_changes: int

        # NB: deliberately don't have a constructor which takes all values, to prevent misuse

        @property
        def time_set(self):
            return self._time_set

        @property
        def num_changes(self):
            return self._num_changes

        @classmethod
        def from_values(cls, value: any, time_set: datetime, num_changes: int):
            pref = cls()
            pref.value = value
            pref._time_set = time_set
            pref._num_changes = num_changes
            return pref

    user_id: str
    respond_to_testing: Preference | None

    def __init__(self, user_id: str):
        self.user_id = user_id
        self.respond_to_testing = None


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
                    user_id TEXT,
                    setting_name TEXT,
                    setting_value TEXT,
                    time_set TEXT,
                    num_changes INTEGER,
                    PRIMARY KEY (user_id, setting_name)
                )
            ''')
            conn.commit()

        logging.info('Connected to user prefs DB at ' + self.db_path)

    def get_user_prefs(self, user_id: str) -> UserPrefs:
        with sqlite3.connect(self.db_path) as conn:
            # Fetch the data
            cursor = conn.cursor()
            cursor.execute('''
                SELECT setting_name, setting_value, time_set, num_changes
                  FROM user_prefs
                 WHERE user_id = ?
            ''', (user_id,))
            rows = cursor.fetchall()

            # Parse the data
            user_prefs = UserPrefs(user_id)
            for row in rows:
                setting_name, setting_value, time_set, num_changes = row
                preference = UserPrefs.Preference.from_values(
                    value=True if setting_value == 'True' else False if setting_value == 'False' else setting_value,
                    time_set=datetime.fromisoformat(time_set),
                    num_changes=num_changes
                )
                setattr(user_prefs, setting_name, preference)

            # Return value
            return user_prefs

    def persist_user_prefs(self, user_id: str, user_prefs: UserPrefs) -> UserPrefs:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            for key, preference in user_prefs.__dict__.items():
                if key == 'user_id':
                    continue

                cursor.execute('''
                    SELECT setting_value, num_changes
                      FROM user_prefs
                     WHERE user_id = ? AND setting_name = ?
                ''', (user_id, key))
                row = cursor.fetchone()

                if row:
                    old_value, old_num_changes = row
                    if old_value != str(preference.value):
                        num_changes = preference.num_changes + 1
                        time_set = datetime.now()
                    else:
                        num_changes = preference.num_changes
                        time_set = preference.time_set
                else:
                    num_changes = 0
                    time_set = datetime.now()

                # Store this value
                cursor.execute('''
                    INSERT INTO user_prefs (user_id, setting_name, setting_value, time_set, num_changes)
                    VALUES (?, ?, ?, ?, ?)
                    ON CONFLICT(user_id, setting_name) DO UPDATE SET
                        setting_value=excluded.setting_value,
                        time_set=excluded.time_set,
                        num_changes=excluded.num_changes
                ''', (user_id, key, str(preference.value), time_set.isoformat(), num_changes))

            # Commit all values
            conn.commit()

        return self.get_user_prefs(user_id)
