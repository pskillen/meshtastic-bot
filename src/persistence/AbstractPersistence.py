import abc
from abc import ABC


class AbstractPersistence(ABC):
    @abc.abstractmethod
    def store_node_id(self, node_id: int):
        pass
