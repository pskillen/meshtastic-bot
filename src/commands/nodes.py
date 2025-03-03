from meshtastic.protobuf.mesh_pb2 import MeshPacket

from src.bot import MeshtasticBot
from src.commands.command import AbstractCommandWithSubcommands
from src.helpers import pretty_print_last_heard


class NodesCommand(AbstractCommandWithSubcommands):
    max_node_count_summary = 6
    max_node_count_detailed = 4

    def __init__(self, bot: MeshtasticBot):
        super().__init__(bot, 'nodes')
        self.sub_commands['busy'] = self.handle_busy

    def get_busy_nodes(self):
        return sorted(self.bot.nodes.list(),
                      key=lambda n:
                      self.bot.nodes.node_packets_today.get(n.user.id, 0), reverse=True)

    def handle_base_command(self, packet: MeshPacket, args: list[str]) -> None:
        nodes = self.bot.nodes.list()
        online_nodes = self.bot.nodes.get_online_nodes()
        offline_nodes = self.bot.nodes.get_offline_nodes()

        # get nodes sorted by last_head
        sorted_nodes = sorted(nodes, key=lambda n: n.last_heard, reverse=True)
        response = f"{len(online_nodes)} nodes online, {len(offline_nodes)} offline."

        # Add up to 10 nodes with the most packets received today
        response += "\nRecent nodes:\n"
        for i, node in enumerate(sorted_nodes[:self.max_node_count_summary]):
            response += f"- {node.user.short_name} ({pretty_print_last_heard(node.last_heard)})\n"

        self.reply(packet, response)

    def handle_busy(self, packet: MeshPacket, args: list[str]) -> None:
        sender = packet['fromId']

        if len(args) == 0:
            self.send_busy_node_list(sender)
        elif args[0] == 'detailed':
            busy_nodes = self.get_busy_nodes()
            for i, node in enumerate(busy_nodes[:self.max_node_count_detailed]):
                self.send_detailed_nodeinfo(sender, node.user.id)
        else:
            node = self.bot.nodes.get_by_short_name(args[0])

            if not node:
                response = f"Unknown command: !nodes busy '{args}' - valid args are 'detailed' or (node ID)"
                return self.reply(packet, response)

            self.send_detailed_nodeinfo(sender, node.user.id)

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
        self.reply_to(sender, response)

    def send_detailed_nodeinfo(self, sender: str, node_id: str):
        node = self.bot.nodes.get_by_id(node_id)

        if not node:
            return

        packets_today = self.bot.nodes.node_packets_today.get(node.user.id, 0)
        packet_breakdown_today = self.bot.nodes.node_packets_today_breakdown.get(node.user.id, {})

        # summarise the node user and packet metrics
        response = f"{node.user.long_name} ({node.user.short_name})\n"
        response += f"Last heard: {pretty_print_last_heard(node.last_heard)}\n"
        response += f"Pkts today: {packets_today}\n"

        # sort packets breakdown by count descending
        sorted_breakdown = sorted(packet_breakdown_today.items(), key=lambda x: x[1], reverse=True)
        for packet_type, count in sorted_breakdown:
            response += f"- {packet_type}: {count}\n"

        self.reply_to(sender, response)

    def show_help(self, packet: MeshPacket, args: list[str]) -> None:
        help_text = "!nodes: details about nodes this device has seen\n"
        help_text += "!nodes busy: summary of busiest nodes\n"
        help_text += "!nodes busy detailed: detailed info about busiest nodes\n"
        self.reply(packet, help_text)

    def get_command_for_logging(self, message: str) -> (str, list[str] | None, str | None):
        return self._gcfl_base_onesub_args(message)
