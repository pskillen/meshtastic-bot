import logging
import sys
import time
from datetime import datetime, timezone

import schedule
from meshtastic.protobuf.mesh_pb2 import MeshPacket
from pubsub import pub
from requests import HTTPError

from src.api.StorageAPI import StorageAPIWrapper
from src.commands.factory import CommandFactory
from src.data_classes import MeshNode
from src.helpers import pretty_print_last_heard, safe_encode_node_name
from src.persistence.commands_logger import AbstractCommandLogger
from src.persistence.node_db import AbstractNodeDB
from src.persistence.node_info import AbstractNodeInfoStore
from src.persistence.packet_dump import dump_packet
from src.persistence.user_prefs import AbstractUserPrefsPersistence
from src.responders.responder_factory import ResponderFactory
from src.tcp_interface import AutoReconnectTcpInterface, SupportsMessageReactionInterface


class MeshtasticBot:
    admin_nodes: list[str]

    interface: SupportsMessageReactionInterface
    init_complete: bool

    my_id: str
    my_nodenum: int
    node_db: AbstractNodeDB
    node_info: AbstractNodeInfoStore
    command_logger: AbstractCommandLogger

    user_prefs_persistence: AbstractUserPrefsPersistence

    storage_apis: list[StorageAPIWrapper]

    def __init__(self, address: str):
        self.address = address

        self.admin_nodes = []

        self.interface = None
        self.init_complete = False

        self.my_id = None
        self.my_nodenum = None
        self.node_db = None
        self.node_info = None
        self.command_logger = None
        self.user_prefs_persistence = None
        self.storage_apis = []
        self.pending_traces = {}

        pub.subscribe(self.on_receive, "meshtastic.receive")
        pub.subscribe(self.on_traceroute, "meshtastic.traceroute")
        pub.subscribe(self.on_receive_text, "meshtastic.receive.text")
        pub.subscribe(self.on_node_updated, "meshtastic.node.updated")
        pub.subscribe(self.on_connection, "meshtastic.connection.established")

    def connect(self):
        logging.info(f"Connecting to Meshtastic node at {self.address}...")
        self.init_complete = False

        old_packet_queue = None
        if self.interface and hasattr(self.interface, 'packet_queue'):
            old_packet_queue = self.interface.packet_queue

        self.interface = AutoReconnectTcpInterface(
            hostname=self.address,
            error_handler=self._handle_interface_error,
            packet_queue=old_packet_queue,
        )

        logging.info("Connected. Listening for messages...")

    def _handle_interface_error(self, error):
        self.disconnect()

        logging.error(f"Handling interface error: {error}")
        backoff_time = 5  # Initial back-off time in seconds
        max_backoff_time = 300  # Maximum back-off time in seconds (5 minutes)
        backoff_rate = 1.5  # Exponential back-off rate

        while True:
            try:
                self.connect()
                self.init_complete = True
                logging.info("Reconnected successfully")
                break
            except Exception as e:
                logging.error(f"Reconnection attempt failed: {e}")
                if backoff_time == max_backoff_time:
                    logging.error("Max backoff time reached. Exiting.")
                    sys.exit(1)
                backoff_time = min(backoff_time * backoff_rate, max_backoff_time)  # Exponential back-off
                logging.info(f"Next reconnection attempt in {backoff_time} seconds")
                time.sleep(backoff_time)

    def disconnect(self):
        self.init_complete = False
        try:
            if self.interface:
                self.interface.close()
                self.interface._disconnected()
        except OSError as ex:
            logging.warning(f"Failed to close connection. Continuing anyway: {ex}")

    def on_connection(self, interface, topic=pub.AUTO_TOPIC):
        self.my_nodenum = interface.localNode.nodeNum  # in dec
        self.my_id = f"!{hex(self.my_nodenum)[2:]}"

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

        sender = self.node_db.get_by_id(from_id)
        logging.info(f"Received private message: '{message}' from {sender.long_name if sender else from_id}")

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
        sender = self.node_db.get_by_id(from_id)

        logging.info(f"DEBUG: Received public message from {sender.long_name if sender else from_id}: {message}")

        # Allow !tr in public channels
        words = message.split()
        if words and words[0].lower() == "!tr":
            logging.info(f"Received public !tr from {sender.long_name if sender else from_id}")
            # Import here to avoid circular imports if any, though factory is better
            from src.commands.factory import CommandFactory
            command_instance = CommandFactory.create_command("!tr", self)
            if command_instance:
                try:
                    # By default commands reply in DM (reply_in_dm).
                    # If we want public reply, we'd need to modify the command or use reply_in_channel.
                    # But for now, let's just let it run. It will DM the user back (which is cleaner).
                    command_instance.handle_packet(packet)
                    return # Stop processing responders
                except Exception as e:
                    logging.error(f"Error handling public command: {e}")

        responder = ResponderFactory.match_responder(message, self)
        if responder:
            try:
                outcome = responder.handle_packet(packet)

                if outcome:
                    logging.info(
                        f"Handled message from {sender.long_name if sender else from_id} with responder {responder.__class__.__name__}: {message}")
                    self.command_logger.log_responder_handled(from_id, responder, message)
            except Exception as e:
                logging.error(f"Error handling message: {e}")

    def on_traceroute(self, packet, route):
        """Callback for when a traceroute response is received."""
        target_id = packet.get('fromId')
        
        if target_id not in self.pending_traces:
            logging.debug(f"Received traceroute from {target_id} but no pending request found.")
            return

        requester_id = self.pending_traces.pop(target_id)
        
        # Format the OUTBOUND route
        route_ids = route.route
        hops = []
        for node_id_int in route_ids:
            # Convert int to !hex string
            node_id_str = f"!{node_id_int:08x}"
            node = self.node_db.get_by_id(node_id_str)
            if node:
                 hops.append(f"{node.short_name}")
            else:
                 hops.append(f"{node_id_str}")

        route_str = " -> ".join(hops) if hops else "Direct (or unknown)"
        
        response_out = f"Trace TO {target_id} ({len(hops)} hops):\n{route_str}"
        logging.info(f"Sending traceroute OUT result to {requester_id}: {response_out}")
        self.interface.sendText(response_out, destinationId=requester_id)
        
        # Format the INBOUND route (if available)
        if hasattr(route, 'route_back') and route.route_back:
            hops_back = []
            for node_id_int in route.route_back:
                 node_id_str = f"!{node_id_int:08x}"
                 node = self.node_db.get_by_id(node_id_str)
                 if node:
                     hops_back.append(f"{node.short_name}")
                 else:
                     hops_back.append(f"{node_id_str}")
            back_str = " -> ".join(hops_back)
            
            response_in = f"Trace FROM {target_id} ({len(hops_back)} hops):\n{back_str}"
            logging.info(f"Sending traceroute IN result to {requester_id}: {response_in}")
            # Small delay to ensure order
            time.sleep(1) 
            self.interface.sendText(response_in, destinationId=requester_id)

    def on_receive(self, packet: MeshPacket, interface):
        if packet.get('fromId') == '!69828b98':
            logging.info(f"DEBUG: Received ANY packet from mte4: {packet}")

        # dump the packet to disk (if enabled)
        dump_packet(packet)

        for storage_api in self.storage_apis:
            try:
                storage_api.store_raw_packet(packet)
            except HTTPError as ex:
                logging.warning(f"Error storing packet: {ex.response.text}")
                pass
            except Exception as ex:
                logging.warning(f"Error storing packet in API: {ex}")
                pass

        sender = packet['fromId']
        node = self.node_db.get_by_id(sender)
        if not node:
            # logging.warning(f"Received packet from unknown sender {sender}")
            return

        if node:
            portnum = packet['decoded']['portnum'] if 'decoded' in packet else 'unknown'
            if sender == self.my_id and portnum == 'TELEMETRY_APP':
                # Ignore telemetry packets sent by self
                pass
            else:
                # Increment packets_today for this node
                self.node_info.node_packet_received(sender, portnum)

        if sender == self.my_id:
            recipient_id = packet['toId']
            recipient = self.node_db.get_by_id(recipient_id)
            portnum = packet['decoded']['portnum']

            logging.debug(
                f"Received packet from self: {recipient.long_name if recipient else recipient_id} (port {portnum})")

    def on_node_updated(self, node, interface):
        if interface.localNode and self.my_nodenum is None:
            self.my_nodenum = interface.localNode.nodeNum
            self.my_id = f"!{hex(self.my_nodenum)[2:]}"

        # Check if the node is a new user
        if node['user'] is not None:
            mesh_node = MeshNode.from_dict(node)
            last_heard_int = node.get('lastHeard', 0)
            last_heard = datetime.fromtimestamp(last_heard_int, tz=timezone.utc)
            self.node_db.store_node(mesh_node)
            self.node_info.update_last_heard(mesh_node.user.id, last_heard)

            for storage_api in self.storage_apis:
                try:
                    storage_api.store_node(mesh_node)
                except HTTPError as ex:
                    logging.warning(f"Error storing node: {ex.response.text}")
                    pass
                except Exception as ex:
                    logging.warning(f"Error storing node: {ex}")
                    pass

            if self.init_complete:
                last_heard_str = pretty_print_last_heard(last_heard)
                logging.info(f"New user: {mesh_node.user.long_name} (last heard {last_heard_str})")

    def print_nodes(self):
        # filter nodes where last heard is more than 2 hours ago
        online_nodes = self.node_info.get_online_nodes()
        offline_nodes = self.node_info.get_offline_nodes()

        # print all nodes, sorted by last heard descending
        logging.info(f"Online nodes: ({len(online_nodes)})")
        sorted_nodes = sorted(online_nodes, key=lambda x: online_nodes[x], reverse=True)
        for node_id in sorted_nodes:
            if node_id == self.my_id:
                continue
            node = self.node_db.get_by_id(node_id)
            last_heard = self.node_info.get_last_heard(node_id)
            last_heard = pretty_print_last_heard(last_heard)
            encoded_name = safe_encode_node_name(node.long_name)
            logging.info(f"- {encoded_name} (last heard {last_heard})")

        logging.info(f"- Plus {len(offline_nodes)} offline nodes")

    def get_global_context(self):
        return {
            'nodes': self.node_db.list_nodes(),
            'online_nodes': self.node_info.get_online_nodes(),
            'offline_nodes': self.node_info.get_offline_nodes(),
        }

    def start_scheduler(self):
        schedule.every().day.at("00:00").do(self.node_info.reset_packets_today)
        while True:
            schedule.run_pending()
            try:
                time.sleep(1)
            except KeyboardInterrupt:
                return

    def get_node_by_short_name(self, short_name: str) -> MeshNode.User | None:
        for node in self.node_db.list_nodes():
            if node.short_name.lower() == short_name.lower():
                return node
        return None
