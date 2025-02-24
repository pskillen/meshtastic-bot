import logging
import time
from datetime import datetime

import meshtastic.tcp_interface
import schedule
from meshtastic.protobuf.mesh_pb2 import MeshPacket
from pubsub import pub

from src.commands.factory import CommandFactory
from src.data_classes import MeshNode, NodeInfoCollection
from src.helpers import pretty_print_last_heard
from src.loggers import UserCommandLogger
from src.tcp_interface import AutoReconnectTcpInterface


class MeshtasticBot:
    admin_nodes: list[str]

    interface: meshtastic.tcp_interface.TCPInterface
    init_complete: bool

    my_id: str
    nodes: NodeInfoCollection
    command_logger: UserCommandLogger

    def __init__(self, address: str):
        self.address = address

        self.admin_nodes = []

        self.interface = None
        self.init_complete = False

        self.my_id = None
        self.nodes = NodeInfoCollection()
        self.command_logger = UserCommandLogger()

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
            command_text = command_instance.get_command_for_logging(message)
            self.command_logger.log_command(from_id, command_text)
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
            portnum = packet['decoded']['portnum'] if 'decoded' in packet else 'unknown'
            if sender == self.my_id and portnum == 'TELEMETRY_APP':
                # Ignore telemetry packets sent by self
                pass
            else:
                self.nodes.increment_packets_today(node.user.id, portnum)

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
                last_heard = pretty_print_last_heard(mesh_node.last_heard)
                logging.info(f"New user: {mesh_node.user.long_name} (last heard {last_heard})")

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
            last_heard = pretty_print_last_heard(node.last_heard)
            logging.info(f"- {node.user.long_name} (last heard {last_heard})")

        logging.info(f"- Plus {len(offline_nodes)} offline nodes")

    def get_global_context(self):
        return {
            'nodes': self.nodes.list(),
            'online_nodes': self.nodes.get_online_nodes(),
            'offline_nodes': self.nodes.get_offline_nodes(),
        }

    def start_scheduler(self):
        schedule.every().day.at("00:00").do(self.nodes.reset_packets_today)
        while True:
            schedule.run_pending()
            try:
                time.sleep(1)
            except KeyboardInterrupt:
                return

    def get_node_by_short_name(self, short_name: str) -> MeshNode | None:
        for node in self.nodes.list():
            if node.user.short_name.lower() == short_name.lower():
                return node
        return None
