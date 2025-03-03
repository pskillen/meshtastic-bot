import abc
import json
import logging
from abc import ABC

from src.bot import MeshtasticBot


class AbstractStatePersistence(ABC):

    def get_state(self, bot: MeshtasticBot) -> dict:
        return {
            'node_data': bot.nodes.to_dict(),
        }

    def import_state(self, bot: MeshtasticBot, data: dict):
        bot.nodes.from_dict(data['node_data'])

    @abc.abstractmethod
    def persist_state(self, bot: MeshtasticBot):
        pass

    @abc.abstractmethod
    def load_state(self, bot: MeshtasticBot):
        pass


class FileBasedStatePersistence(AbstractStatePersistence):
    def __init__(self, file_path: str):
        self.file_path = file_path

    def persist_state(self, bot: MeshtasticBot):
        try:
            with open(self.file_path, 'w') as f:
                json.dump(self.get_state(bot), f)
        except Exception:
            logging.error(f"Failed to persist state info", exc_info=True)

    def load_state(self, bot: MeshtasticBot):
        try:
            with open(self.file_path, 'r') as f:
                data = json.load(f)
                self.import_state(bot, data)

            logging.info(f"Successfully loaded state from {self.file_path}")
        except FileNotFoundError:
            logging.warning(f"State file {self.file_path} not found")
        except Exception as e:
            logging.error(f"Failed to load state file {self.file_path}", exc_info=True)
            pass
