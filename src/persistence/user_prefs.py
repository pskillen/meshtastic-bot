import abc


class UserPrefs:
    user_id: int
    respond_to_testing: bool

    def __init__(self, user_id: int):
        self.user_id = user_id
        self.respond_to_testing = False


class AbstractUserPrefsPersistence(abc.ABC):
    @abc.abstractmethod
    def get_user_prefs(self, user_id: str) -> UserPrefs:
        pass

    @abc.abstractmethod
    def persist_user_prefs(self, user_id: str, user_prefs: UserPrefs):
        pass
