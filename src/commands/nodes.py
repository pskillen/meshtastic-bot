from meshtastic.protobuf.mesh_pb2 import MeshPacket

from src.bot import MeshtasticBot
from src.commands.command import AbstractCommand


class NodesCommand(AbstractCommand):
    def __init__(self, bot: MeshtasticBot):
        self.bot = bot

    def handle_packet(self, packet: MeshPacket) -> None:
        sender = packet['fromId']

        nodes = self.bot.nodes
        online_nodes = self.bot.get_online_nodes()
        offline_nodes = self.bot.get_offline_nodes()

        # get nodes sorted by number of packets received
        busy_nodes = sorted(nodes.values(), key=lambda node: node.packets_today, reverse=True)

        response = f"Nodes: {len(nodes)} ({len(online_nodes)} online, {len(offline_nodes)} offline). "

        # Add up to 5 nodes with the most packets received today
        response += "\n\nBusy nodes:\n"
        for i, node in enumerate(busy_nodes[:5]):
            response += f"- {node.user.short_name} ({node.packets_today} packets)\n"

        print(f"Sending response: '{response}'")

        self.bot.interface.sendText(response, destinationId=sender)
