import abc
import datetime

from src.data_classes import MeshNode


class AbstractNodeDB(abc.ABC):

    @abc.abstractmethod
    def store_node(self, node_user: MeshNode.User):
        pass

    @abc.abstractmethod
    def get_by_id(self, node_id: str) -> MeshNode.User | None:
        pass

    @abc.abstractmethod
    def get_by_short_name(self, short_name: str) -> MeshNode.User | None:
        pass

    @abc.abstractmethod
    def list_nodes(self) -> list[MeshNode.User]:
        pass

    @abc.abstractmethod
    def store_position(self, node_id: str, position: MeshNode.Position):
        pass

    @abc.abstractmethod
    def get_last_position(self, node_id: str) -> MeshNode.Position | None:
        pass

    @abc.abstractmethod
    def get_position_log(self, node_id: str,
                         start: datetime.datetime,
                         end: datetime.datetime) -> list[MeshNode.Position]:
        pass

    @abc.abstractmethod
    def store_device_metrics(self, node_id: str, device_metrics: MeshNode.DeviceMetrics):
        pass

    @abc.abstractmethod
    def get_last_device_metrics(self, node_id: str) -> MeshNode.DeviceMetrics | None:
        pass

    @abc.abstractmethod
    def get_device_metrics_log(self, node_id: str,
                               start: datetime.datetime,
                               end: datetime.datetime) -> list[MeshNode.DeviceMetrics]:
        pass


class SqliteNodeDB(AbstractNodeDB):
    def __init__(self, db_file: str):
        self.db_file = db_file

    def store_node(self, node_user: MeshNode.User):
        pass

    def get_by_id(self, node_id: str) -> MeshNode.User | None:
        pass

    def get_by_short_name(self, short_name: str) -> MeshNode.User | None:
        pass

    def list_nodes(self) -> list[MeshNode.User]:
        pass

    def store_position(self, node_id: str, position: MeshNode.Position):
        pass

    def get_last_position(self, node_id: str) -> MeshNode.Position | None:
        pass

    def get_position_log(self, node_id: str,
                         start: datetime.datetime,
                         end: datetime.datetime) -> list[MeshNode.Position]:
        pass

    def store_device_metrics(self, node_id: str, device_metrics: MeshNode.DeviceMetrics):
        pass

    def get_last_device_metrics(self, node_id: str) -> MeshNode.DeviceMetrics | None:
        pass

    def get_device_metrics_log(self, node_id: str,
                               start: datetime.datetime,
                               end: datetime.datetime) -> list[MeshNode.DeviceMetrics]:
        pass
