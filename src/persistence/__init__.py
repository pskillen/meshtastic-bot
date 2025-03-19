import abc
import logging
from pathlib import Path


class BaseSqlitePersistenceStore(abc.ABC):
    db_path: Path

    def __init__(self, db_path: str):
        self.db_path = Path(db_path)
        self._initialize_db()
        if self.db_path.is_relative_to(Path.cwd()):
            path_string = self.db_path.relative_to(Path.cwd())
        else:
            path_string = self.db_path
        logging.info(f"Connected to {self.__class__.__name__} DB at {path_string}")

    @abc.abstractmethod
    def _initialize_db(self):
        pass
