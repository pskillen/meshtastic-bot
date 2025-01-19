from datetime import datetime, timezone
from typing import Dict

import meshtastic.tcp_interface
from meshtastic.protobuf.mesh_pb2 import MeshPacket
from pubsub import pub

from src.commands.factory import CommandFactory
from src.data_classes import MeshNode, User, Position, DeviceMetrics


class MeshtasticBot:
    interface: meshtastic.tcp_interface.TCPInterface
    nodes: dict[str, MeshNode]
    init_complete: bool

    ONLINE_THRESHOLD = 7200  # 2 hours

    def __init__(self, address: str):
        self.address = address
        self.nodes = {}
        self.init_complete = False

    def connect(self):
        print(f"Connecting to Meshtastic node at {self.address}...")
        self.init_complete = False
        pub.subscribe(self.on_receive_text, "meshtastic.receive.text")
        # pub.subscribe(self.on_receive_user, "meshtastic.receive.user")
        pub.subscribe(self.on_node_updated, "meshtastic.node.updated")
        pub.subscribe(self.on_connection, "meshtastic.connection.established")
        self.interface = meshtastic.tcp_interface.TCPInterface(hostname=self.address)

        print("Connected. Listening for messages...")

    def disconnect(self):
        self.interface.close()
        self.init_complete = False

    def on_connection(self, interface, topic=pub.AUTO_TOPIC):
        self.init_complete = False
        print('Connected to Meshtastic node')
        self.print_nodes()

    def on_receive_text(self, packet: MeshPacket, interface):
        """Callback function triggered when a text message is received."""

        message = packet['decoded']['text']
        sender = packet['fromId']
        to_id = packet['toId']

        if to_id == '^all':
            return

        print(f"Received message: '{message}' from {sender}")

        words = message.split()
        command_name = words[0]
        command_instance = CommandFactory.create_command(command_name, self)
        if command_instance:
            try:
                command_instance.handle_packet(packet)
            except Exception as e:
                print(f"Error handling message: {e}")

    # def on_receive_user(self, packet, interface):
    #     print(f"Received user: {packet}")

    def on_node_updated(self, node, interface):
        # Check if the node is a new user
        if node['user'] is not None:
            mesh_node = self.parse_mesh_node(node)
            self.nodes[mesh_node.user.id] = mesh_node

            if self.init_complete:
                last_heard = MeshtasticBot.pretty_print_last_heard(mesh_node.last_heard)
                print(f"New user: {mesh_node.user.long_name} (last heard {last_heard})")

    @staticmethod
    def parse_mesh_node(data: Dict) -> MeshNode:
        user_data = data.get('user', {})
        user = User()
        user.id = user_data.get('id', '')
        user.long_name = user_data.get('longName', '')
        user.short_name = user_data.get('shortName', '')
        user.macaddr = user_data.get('macaddr', '')
        user.hw_model = user_data.get('hwModel', '')
        user.public_key = user_data.get('publicKey', '')

        position_data = data.get('position', {})
        position = Position()
        position.latitude = position_data.get('latitude', 0.0)
        position.longitude = position_data.get('longitude', 0.0)
        position.altitude = position_data.get('altitude', 0)
        position.time = position_data.get('time', 0)
        position.location_source = position_data.get('locationSource', '')

        device_metrics_data = data.get('deviceMetrics', {})
        device_metrics = DeviceMetrics()
        device_metrics.battery_level = device_metrics_data.get('batteryLevel', 0)
        device_metrics.voltage = device_metrics_data.get('voltage', 0.0)
        device_metrics.channel_utilization = device_metrics_data.get('channelUtilization', 0.0)
        device_metrics.air_util_tx = device_metrics_data.get('airUtilTx', 0.0)
        device_metrics.uptime_seconds = device_metrics_data.get('uptimeSeconds', 0)

        mesh_node = MeshNode()
        mesh_node.num = data.get('num', 0)
        mesh_node.user = user
        mesh_node.position = position
        mesh_node.last_heard = data.get('lastHeard', 0)
        mesh_node.device_metrics = device_metrics
        mesh_node.is_favorite = data.get('isFavorite', False)

        return mesh_node

    @staticmethod
    def pretty_print_last_heard(last_heard_timestamp: int) -> str:
        now = datetime.now(timezone.utc)
        last_heard = datetime.fromtimestamp(last_heard_timestamp, timezone.utc)
        delta = now - last_heard

        if delta.days > 0:
            return f"{delta.days}d ago"
        elif delta.seconds >= 3600:
            hours = delta.seconds // 3600
            return f"{hours}h ago"
        elif delta.seconds >= 60:
            minutes = delta.seconds // 60
            return f"{minutes}m ago"
        else:
            return f"{delta.seconds}s ago"

    def print_nodes(self):
        # filter nodes where last heard is more than 2 hours ago
        online_nodes = {k: v for k, v in self.nodes.items() if
                        v.last_heard > datetime.now().timestamp() - self.ONLINE_THRESHOLD}
        offline_nodes = {k: v for k, v in self.nodes.items() if
                         v.last_heard <= datetime.now().timestamp() - self.ONLINE_THRESHOLD}

        # print all nodes, sorted by last heard descending
        print("Online nodes:")
        sorted_nodes = sorted(online_nodes.values(), key=lambda x: x.last_heard, reverse=True)
        for node in sorted_nodes:
            last_heard = MeshtasticBot.pretty_print_last_heard(node.last_heard)
            print(f"- {node.user.long_name} (last heard {last_heard})")

        print(f"- Plus {len(offline_nodes)} offline nodes")

    def get_global_context(self):
        return {
            'nodes': self.nodes,
            'online_nodes': {k: v for k, v in self.nodes.items() if
                             v.last_heard > datetime.now().timestamp() - self.ONLINE_THRESHOLD},
            'offline_nodes': {k: v for k, v in self.nodes.items() if
                              v.last_heard <= datetime.now().timestamp() - self.ONLINE_THRESHOLD}
        }
