from meshtastic.protobuf.mesh_pb2 import MeshPacket

from src.bot import MeshtasticBot
from src.commands.command import AbstractCommand


class HelloCommand(AbstractCommand):
    def __init__(self, bot: MeshtasticBot):
        self.bot = bot

    def handle_packet(self, packet: MeshPacket) -> None:
        sender = packet['fromId']
        sender_name = self.bot.nodes[sender].user.long_name

        response = f"Hello, {sender_name}! How can I help you? (tip: try !help)"
        print(f"Sending response: '{response}'")

        self.bot.interface.sendText(response, destinationId=sender)
