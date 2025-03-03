import logging
import time
from datetime import datetime

import meshtastic.tcp_interface
import schedule
from meshtastic.protobuf.mesh_pb2 import MeshPacket
from pubsub import pub

from src.commands.factory import CommandFactory
from src.data_classes import MeshNode, NodeInfoCollection
from src.helpers import pretty_print_last_heard, safe_encode_node_name
from src.persistence.commands_logger import AbstractCommandLogger
from src.persistence.user_prefs import AbstractUserPrefsPersistence
from src.responders.responder_factory import ResponderFactory
from src.tcp_interface import AutoReconnectTcpInterface


class MeshtasticBot:
    admin_nodes: list[str]

    interface: meshtastic.tcp_interface.TCPInterface
    init_complete: bool

    my_id: str
    nodes: NodeInfoCollection
    command_logger: AbstractCommandLogger

    user_prefs_persistence: AbstractUserPrefsPersistence

    def __init__(self, address: str):
        self.address = address

        self.admin_nodes = []

        self.interface = None
        self.init_complete = False

        self.my_id = None
        self.nodes = NodeInfoCollection()
        self.command_logger = None
        self.user_prefs_persistence = None

    def connect(self):
        logging.info(f"Connecting to Meshtastic node at {self.address}...")
        self.init_complete = False
        pub.subscribe(self.on_receive, "meshtastic.receive")
        pub.subscribe(self.on_receive_text, "meshtastic.receive.text")
        pub.subscribe(self.on_node_updated, "meshtastic.node.updated")
        pub.subscribe(self.on_connection, "meshtastic.connection.established")
        self.interface = AutoReconnectTcpInterface(
            hostname=self.address,
            error_handler=self._handle_interface_error
        )

        logging.info("Connected. Listening for messages...")

    def _handle_interface_error(self, error):
        self.disconnect()

        logging.error(f"Handling interface error: {error}")
        backoff_time = 5  # Initial back-off time in seconds
        max_backoff_time = 300  # Maximum back-off time in seconds (5 minutes)

        while True:
            try:
                self.interface = AutoReconnectTcpInterface(
                    hostname=self.address,
                    error_handler=self._handle_interface_error
                )
                self.interface.connect()
                logging.info("Reconnected successfully")
                break
            except Exception as e:
                logging.error(f"Reconnection attempt failed: {e}")
                backoff_time = min(backoff_time * 1.5, max_backoff_time)  # Exponential back-off
                logging.info(f"Next reconnection attempt in {backoff_time} seconds")
                time.sleep(backoff_time)

    def disconnect(self):
        self.init_complete = False
        try:
            self.interface.close()
        except OSError:
            pass

    def on_connection(self, interface, topic=pub.AUTO_TOPIC):
        my_nodenum = interface.localNode.nodeNum  # in dec
        self.my_id = f"!{hex(my_nodenum)[2:]}"

        self.init_complete = True
        logging.info('Connected to Meshtastic node')
        self.print_nodes()

    def on_receive_text(self, packet: MeshPacket, interface):
        """Callback function triggered when a text message is received."""

        to_id = packet['toId']

        if to_id == self.my_id:
            self.handle_private_message(packet)
        else:
            self.handle_public_message(packet)

    def handle_private_message(self, packet: MeshPacket):
        """Handle private messages."""
        message = packet['decoded']['text']
        from_id = packet['fromId']

        sender = self.nodes.get_by_id(from_id)
        logging.info(f"Received private message: '{message}' from {sender.user.long_name if sender else from_id}")

        words = message.split()
        command_name = words[0]
        command_instance = CommandFactory.create_command(command_name, self)
        if command_instance:
            self.command_logger.log_command(from_id, command_instance, message)
            try:
                command_instance.handle_packet(packet)
            except Exception as e:
                logging.error(f"Error handling message: {e}")
        else:
            self.command_logger.log_unknown_request(from_id, message)

    def handle_public_message(self, packet: MeshPacket):
        """Handle public messages."""
        message = packet['decoded']['text']
        from_id = packet['fromId']
        sender = self.nodes.get_by_id(from_id)

        responder = ResponderFactory.match_responder(message, self)
        if responder:
            try:
                outcome = responder.handle_packet(packet)

                if outcome:
                    logging.info(
                        f"Handled message from {sender.user.long_name if sender else from_id} with responder {responder.__class__.__name__}: {message}")
                    self.command_logger.log_responder_handled(from_id, responder, message)
            except Exception as e:
                logging.error(f"Error handling message: {e}")

    def on_receive(self, packet: MeshPacket, interface):
        sender = packet['fromId']
        node = self.nodes.get_by_id(sender)
        if not node:
            # logging.warning(f"Received packet from unknown sender {sender}")
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
            encoded_name = safe_encode_node_name(node.user.long_name)
            logging.info(f"- {encoded_name} (last heard {last_heard})")

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
