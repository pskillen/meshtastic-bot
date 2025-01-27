from datetime import datetime
from typing import Optional


class User:
    id: str
    long_name: str
    short_name: str
    macaddr: str
    hw_model: str
    public_key: str


class Position:
    altitude: int
    time: int
    location_source: str
    latitude: float
    longitude: float


class DeviceMetrics:
    battery_level: int
    voltage: float
    channel_utilization: float
    air_util_tx: float
    uptime_seconds: int


class MeshNode:
    num: int
    user: Optional[User]
    position: Optional[Position]
    last_heard: int
    device_metrics: Optional[DeviceMetrics]
    is_favorite: bool
    packets_today: int
    packet_breakdown_today: dict[str, int]

    def to_dict(self) -> dict:
        return {
            'num': self.num,
            'user': {
                'id': self.user.id,
                'longName': self.user.long_name,
                'shortName': self.user.short_name,
                'macaddr': self.user.macaddr,
                'hwModel': self.user.hw_model,
                'publicKey': self.user.public_key
            },
            'position': {
                'altitude': self.position.altitude,
                'time': self.position.time,
                'locationSource': self.position.location_source,
                'latitude': self.position.latitude,
                'longitude': self.position.longitude
            },
            'lastHeard': self.last_heard,
            'deviceMetrics': {
                'batteryLevel': self.device_metrics.battery_level,
                'voltage': self.device_metrics.voltage,
                'channelUtilization': self.device_metrics.channel_utilization,
                'airUtilTx': self.device_metrics.air_util_tx,
                'uptimeSeconds': self.device_metrics.uptime_seconds
            },
            'isFavorite': self.is_favorite,
            'packetsToday': self.packets_today,
            'packetBreakdownToday': self.packet_breakdown_today
        }

    @classmethod
    def from_dict(cls, node_data: dict):
        user_data = node_data.get('user', {})
        user = User()
        user.id = user_data.get('id', '')
        user.long_name = user_data.get('longName', '')
        user.short_name = user_data.get('shortName', '')
        user.macaddr = user_data.get('macaddr', '')
        user.hw_model = user_data.get('hwModel', '')
        user.public_key = user_data.get('publicKey', '')

        position_data = node_data.get('position', {})
        position = Position()
        position.latitude = position_data.get('latitude', 0.0)
        position.longitude = position_data.get('longitude', 0.0)
        position.altitude = position_data.get('altitude', 0)
        position.time = position_data.get('time', 0)
        position.location_source = position_data.get('locationSource', '')

        device_metrics_data = node_data.get('deviceMetrics', {})
        device_metrics = DeviceMetrics()
        device_metrics.battery_level = device_metrics_data.get('batteryLevel', 0)
        device_metrics.voltage = device_metrics_data.get('voltage', 0.0)
        device_metrics.channel_utilization = device_metrics_data.get('channelUtilization', 0.0)
        device_metrics.air_util_tx = device_metrics_data.get('airUtilTx', 0.0)
        device_metrics.uptime_seconds = device_metrics_data.get('uptimeSeconds', 0)

        node = MeshNode()
        node.num = node_data.get('num', 0)
        node.user = user
        node.position = position
        node.last_heard = node_data.get('lastHeard', 0)
        node.device_metrics = device_metrics
        node.is_favorite = node_data.get('isFavorite', False)
        node.packets_today = node_data.get('packetsToday', 0)
        node.packet_breakdown_today = node_data.get('packetBreakdownToday', {})

        return node

class NodeInfoCollection:
    DEFAULT_ONLINE_THRESHOLD = 7200  # 2 hours

    nodes: dict[str, MeshNode]
    online_threshold_sec: int

    def __init__(self):
        self.nodes = {}
        self.online_threshold_sec = NodeInfoCollection.DEFAULT_ONLINE_THRESHOLD

    def add_node(self, node: MeshNode):
        self.nodes[node.user.id] = node

    def get_by_id(self, node_id: str) -> MeshNode | None:
        return self.nodes.get(node_id)

    def get_by_short_name(self, short_name: str) -> MeshNode | None:
        for node in self.nodes.values():
            if node.user.short_name.lower() == short_name.lower():
                return node
        return None

    def get_online_nodes(self):
        return {k: v for k, v in self.nodes.items() if
                v.last_heard > datetime.now().timestamp() - self.online_threshold_sec}

    def get_offline_nodes(self):
        return {k: v for k, v in self.nodes.items() if
                v.last_heard <= datetime.now().timestamp() - self.online_threshold_sec}

    def list(self) -> list[MeshNode]:
        return list(self.nodes.values())
