import abc
import datetime
import json


class AbstractNodeInfoStore(abc.ABC):
    DEFAULT_ONLINE_THRESHOLD = 7200  # 2 hours
    online_threshold_sec: int
    packet_counter_reset_time: datetime.datetime

    def __init__(self):
        self.online_threshold_sec = self.DEFAULT_ONLINE_THRESHOLD
        self.packet_counter_reset_time = datetime.datetime.now()

    @abc.abstractmethod
    def node_packet_received(self, node_id: str, packet_type: str) -> None:
        pass

    @abc.abstractmethod
    def reset_packets_today(self) -> None:
        pass

    @abc.abstractmethod
    def get_online_nodes(self) -> dict[str, datetime.datetime]:
        pass

    @abc.abstractmethod
    def get_offline_nodes(self) -> dict[str, datetime.datetime]:
        pass

    @abc.abstractmethod
    def get_all_nodes(self) -> dict[str, datetime.datetime]:
        pass

    @abc.abstractmethod
    def get_last_heard(self, node_id) -> datetime.datetime | None:
        pass


class InMemoryNodeInfoStore(AbstractNodeInfoStore):
    # node_id -> last_heard
    nodes_last_heard: dict[str, datetime.datetime]

    # node_id -> packet_count
    node_packets_today: dict[str, int]

    # node_id -> packet_type -> packet_count
    node_packets_today_breakdown: dict[str, dict[str, int]]

    def __init__(self):
        super().__init__()
        self.nodes_last_heard = {}
        self.node_packets_today = {}
        self.node_packets_today_breakdown = {}

    def node_packet_received(self, node_id: str, packet_type: str):
        self.nodes_last_heard[node_id] = datetime.datetime.now()

        if node_id not in self.node_packets_today:
            self.node_packets_today[node_id] = 1
        else:
            self.node_packets_today[node_id] += 1

        if node_id not in self.node_packets_today_breakdown:
            self.node_packets_today_breakdown[node_id] = {}

        if packet_type not in self.node_packets_today_breakdown[node_id]:
            self.node_packets_today_breakdown[node_id][packet_type] = 1
        else:
            self.node_packets_today_breakdown[node_id][packet_type] += 1

    def reset_packets_today(self):
        self.node_packets_today = {}
        self.node_packets_today_breakdown = {}

    def get_online_nodes(self):
        return {k: v for k, v in self.nodes_last_heard.items() if
                v > datetime.datetime.now() - datetime.timedelta(seconds=self.online_threshold_sec)}

    def get_offline_nodes(self):
        return {k: v for k, v in self.nodes_last_heard.items() if
                v <= datetime.datetime.now() - datetime.timedelta(seconds=self.online_threshold_sec)}

    def get_all_nodes(self) -> dict[str, datetime.datetime]:
        return self.nodes_last_heard

    def load_from_file(self, node_info_file: str):
        with open(node_info_file, 'r') as file:
            data = json.load(file)
            self.nodes_last_heard = {k: datetime.datetime.fromisoformat(v) for k, v in data['nodes_last_heard'].items()}
            self.node_packets_today = data['node_packets_today']
            self.node_packets_today_breakdown = data['node_packets_today_breakdown']

    def persist_to_file(self, node_info_file: str):
        with open(node_info_file, 'w') as file:
            data = {
                'nodes_last_heard': {k: v.isoformat() for k, v in self.nodes_last_heard.items()},
                'node_packets_today': self.node_packets_today,
                'node_packets_today_breakdown': self.node_packets_today_breakdown
            }
            json.dump(data, file, indent=4)
