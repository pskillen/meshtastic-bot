import logging
import time
from datetime import datetime, timezone

import meshtastic.tcp_interface
import schedule
from meshtastic.protobuf.mesh_pb2 import MeshPacket
from pubsub import pub

from src.commands.factory import CommandFactory
from src.data_classes import MeshNode, NodeInfoCollection
from src.loggers import UserCommandLogger
from src.persistence.node_info import AbstractNodeInfoPersistence
from src.persistence.state import AbstractStatePersistence, AppState
from src.tcp_interface import AutoReconnectTcpInterface


class MeshtasticBot:
    admin_nodes: list[str]

    interface: meshtastic.tcp_interface.TCPInterface
    init_complete: bool
    packet_counter_reset_time: datetime

    my_id: str
    nodes: NodeInfoCollection
    command_logger: UserCommandLogger

    node_persistence: AbstractNodeInfoPersistence | None
    state_persistence: AbstractStatePersistence | None

    def __init__(self, address: str):
        self.address = address

        self.admin_nodes = []

        self.interface = None
        self.init_complete = False
        self.packet_counter_reset_time = datetime.now()

        self.my_id = None
        self.nodes = NodeInfoCollection()
        self.command_logger = UserCommandLogger()

        self.node_persistence = None
        self.state_persistence = None

    def connect(self):
        logging.info(f"Connecting to Meshtastic node at {self.address}...")
        self.init_complete = False
        pub.subscribe(self.on_receive, "meshtastic.receive")
        pub.subscribe(self.on_receive_text, "meshtastic.receive.text")
        pub.subscribe(self.on_node_updated, "meshtastic.node.updated")
        pub.subscribe(self.on_connection, "meshtastic.connection.established")
        self.interface = AutoReconnectTcpInterface(hostname=self.address)

        logging.info("Connected. Listening for messages...")

    def disconnect(self):
        self.init_complete = False
        try:
            self.interface.close()
        except OSError:
            pass

    def on_connection(self, interface, topic=pub.AUTO_TOPIC):
        my_nodenum = interface.localNode.nodeNum  # in dec
        self.my_id = f"!{hex(my_nodenum)[2:]}"

        self.init_complete = False
        logging.info('Connected to Meshtastic node')
        self.print_nodes()

    def on_receive_text(self, packet: MeshPacket, interface):
        """Callback function triggered when a text message is received."""

        message = packet['decoded']['text']
        from_id = packet['fromId']
        to_id = packet['toId']

        if to_id != self.my_id:
            return

        sender = self.nodes.get_by_id(from_id)
        logging.info(f"Received message: '{message}' from {sender.user.long_name if sender else from_id}")

        words = message.split()
        command_name = words[0]
        command_instance = CommandFactory.create_command(command_name, self)
        if command_instance:
            self.command_logger.log_command(command_instance, from_id, message)
            try:
                command_instance.handle_packet(packet)
            except Exception as e:
                logging.error(f"Error handling message: {e}")
        else:
            self.command_logger.log_unknown_request(from_id, message)

    def on_receive(self, packet: MeshPacket, interface):
        sender = packet['fromId']
        node = self.nodes.get_by_id(sender)
        if not node:
            logging.warning(f"Received packet from unknown sender {sender}")
            return

        if node:
            # Update last_heard for this node
            node.last_heard = int(datetime.now().timestamp())
            # Increment packets_today for this node
            node.packets_today += 1

            if 'decoded' in packet:
                portnum = packet['decoded']['portnum']
                # increment breakdown by portnum
                if portnum in node.packet_breakdown_today:
                    node.packet_breakdown_today[portnum] += 1
                else:
                    node.packet_breakdown_today[portnum] = 1
            else:
                logging.warning(f"Received packet from {node.user.long_name} with no decoded data")

        if sender == self.my_id:
            recipient_id = packet['toId']
            recipient = self.nodes.get_by_id(recipient_id)
            portnum = packet['decoded']['portnum']

            logging.debug(
                f"Received packet from self: {recipient.user.long_name if recipient else recipient_id} (port {portnum})")

    def on_node_updated(self, node, interface):
        # Check if the node is a new user
        if node['user'] is not None:
            mesh_node = MeshNode.from_dict(node)
            self.nodes.add_node(mesh_node)

            if self.init_complete:
                last_heard = MeshtasticBot.pretty_print_last_heard(mesh_node.last_heard)
                logging.info(f"New user: {mesh_node.user.long_name} (last heard {last_heard})")

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
        online_nodes = self.nodes.get_online_nodes()
        offline_nodes = self.nodes.get_offline_nodes()

        # print all nodes, sorted by last heard descending
        logging.info(f"Online nodes: ({len(online_nodes)})")
        sorted_nodes = sorted(online_nodes.values(), key=lambda x: x.last_heard, reverse=True)
        for node in sorted_nodes:
            if node.user.id == self.my_id:
                continue
            last_heard = MeshtasticBot.pretty_print_last_heard(node.last_heard)
            logging.info(f"- {node.user.long_name} (last heard {last_heard})")

        logging.info(f"- Plus {len(offline_nodes)} offline nodes")

    def get_global_context(self):
        return {
            'nodes': self.nodes.list(),
            'online_nodes': self.nodes.get_online_nodes(),
            'offline_nodes': self.nodes.get_offline_nodes(),
        }

    def reset_packets_today(self):
        # sort nodes by packets_today, then print out any nodes with > 0 packets
        logging.info("Resetting packets_today counts...")
        sorted_nodes = sorted(self.nodes.list(), key=lambda x: x.packets_today, reverse=True)
        for node in sorted_nodes:
            if node.packets_today > 0:
                logging.info(f"- {node.user.long_name}: {node.packets_today} packets")
            node.packets_today = 0
            node.packet_breakdown_today = {}

        self.packet_counter_reset_time = datetime.now()
        logging.info(f"Reset all packets_today counts at {self.packet_counter_reset_time}")

    def start_scheduler(self):
        schedule.every().day.at("00:00").do(self.reset_packets_today)
        while True:
            schedule.run_pending()
            try:
                time.sleep(1)
            except KeyboardInterrupt:
                return

    def persist_all_data(self):
        if self.node_persistence:
            node_list = list(self.nodes.list())
            self.node_persistence.persist_node_info(node_list)
            logging.info("Node data persisted")

        if self.state_persistence:
            state = AppState(
                packet_counter_reset_time=self.packet_counter_reset_time,
                command_stats=self.command_logger.command_stats,
                unknown_command_stats=self.command_logger.unknown_command_stats,
            )
            self.state_persistence.persist_state(state)
            logging.info("State data persisted")

    def load_persisted_data(self):
        if self.state_persistence:
            state = self.state_persistence.load_state()
            if state:
                self.packet_counter_reset_time = state.packet_counter_reset_time or datetime.now()
                self.command_logger.command_stats = state.command_stats or {}
                self.command_logger.unknown_command_stats = state.unknown_command_stats or {}
                logging.info("State data loaded")

        if self.node_persistence:
            node_list = self.node_persistence.load_node_info()
            if node_list:
                for node in node_list:
                    self.nodes.add_node(node)
                logging.info("Node data loaded")

        # if the packet counter _should_ have been reset, reset it now
        if self.packet_counter_reset_time.date() != datetime.now().date():
            logging.info(f"Need to reset stale packet counts from {self.packet_counter_reset_time}")
            self.reset_packets_today()

    def get_node_by_short_name(self, short_name: str) -> MeshNode | None:
        for node in self.nodes.list():
            if node.user.short_name.lower() == short_name.lower():
                return node
        return None
