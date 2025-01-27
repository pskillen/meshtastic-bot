import logging

from meshtastic.protobuf.mesh_pb2 import MeshPacket

from src.bot import MeshtasticBot
from src.commands.command import AbstractCommand


class NodesCommand(AbstractCommand):
    max_node_count_summary = 6
    max_node_count_detailed = 4

    def __init__(self, bot: MeshtasticBot):
        self.bot = bot

    def get_busy_nodes(self):
        return sorted(self.bot.nodes.list(),
                      key=lambda n:
                      self.bot.nodes.node_packets_today.get(n.user.id, 0), reverse=True)

    def handle_packet(self, packet: MeshPacket) -> None:
        sender = packet['fromId']
        message = packet['decoded']['text']
        words = message.split()

        # command format is "!nodes <command> <args"
        if len(words) < 2:
            # send the node summary
            self.send_online_node_list(sender)
            return

        command = words[1]
        args = words[2:] if len(words) > 2 else []

        if command == 'busy':
            if len(args) == 0:
                self.send_busy_node_list(sender)
            elif args[0] == 'detailed':
                busy_nodes = self.get_busy_nodes()
                for i, node in enumerate(busy_nodes[:self.max_node_count_detailed]):
                    self.send_detailed_nodeinfo(sender, node.user.id)
            else:
                response = f"Unknown command: !nodes busy '{args}' - valid args are 'detailed'"
                logging.debug(f"Sending response: '{response}'")
                self.bot.interface.sendText(response, destinationId=sender)
        else:
            response = f"Unknown command: !nodes'{command}' - valid commands are 'busy (detailed)'"
            logging.debug(f"Sending response: '{response}'")
            self.bot.interface.sendText(response, destinationId=sender)

    def send_online_node_list(self, sender: str):
        nodes = self.bot.nodes.list()
        online_nodes = self.bot.nodes.get_online_nodes()
        offline_nodes = self.bot.nodes.get_offline_nodes()

        # get nodes sorted by last_head
        sorted_nodes = sorted(nodes, key=lambda n: n.last_heard, reverse=True)
        response = f"{len(online_nodes)} nodes online, {len(offline_nodes)} offline."

        # Add up to 10 nodes with the most packets received today
        response += "\nRecent nodes:\n"
        for i, node in enumerate(sorted_nodes[:self.max_node_count_summary]):
            response += f"- {node.user.short_name} ({MeshtasticBot.pretty_print_last_heard(node.last_heard)})\n"

        logging.debug(f"Sending response: '{response}'")
        self.bot.interface.sendText(response, destinationId=sender)

    def send_busy_node_list(self, sender: str):
        online_nodes = self.bot.nodes.get_online_nodes()

        # get nodes sorted by number of packets received
        busy_nodes = self.get_busy_nodes()
        response = f"{len(online_nodes)} nodes online."

        # Add up to 10 nodes with the most packets received today
        response += "\nBusy nodes:\n"
        for i, node in enumerate(busy_nodes[:self.max_node_count_summary]):
            packets_today = self.bot.nodes.node_packets_today.get(node.user.id, 0)
            response += f"- {node.user.short_name} ({packets_today} pkts)\n"

        # reset time
        response += f"(last reset at {self.bot.nodes.packet_counter_reset_time.strftime('%H:%M:%S')})"

        logging.debug(f"Sending response: '{response}'")
        self.bot.interface.sendText(response, destinationId=sender)

    def send_detailed_nodeinfo(self, sender: str, node_id: str):
        node = self.bot.nodes.get_by_id(node_id)

        if not node:
            return

        packets_today = self.bot.nodes.node_packets_today.get(node.user.id, 0)
        packet_breakdown_today = self.bot.nodes.node_packets_today_breakdown.get(node.user.id, {})

        # summarise the node user and packet metrics
        response = f"{node.user.long_name} ({node.user.short_name})\n"
        response += f"Last heard: {MeshtasticBot.pretty_print_last_heard(node.last_heard)}\n"
        response += f"Pkts today: {packets_today}\n"

        # sort packets breakdown by count descending
        sorted_breakdown = sorted(packet_breakdown_today.items(), key=lambda x: x[1], reverse=True)
        for packet_type, count in sorted_breakdown:
            response += f"- {packet_type}: {count}\n"

        logging.debug(f"Sending response: '{response}'")
        self.bot.interface.sendText(response, destinationId=sender)
