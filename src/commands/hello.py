import logging

from meshtastic.protobuf.mesh_pb2 import MeshPacket

from src.bot import MeshtasticBot
from src.commands.command import AbstractCommand


class HelloCommand(AbstractCommand):
    def __init__(self, bot: MeshtasticBot):
        self.bot = bot

    def handle_packet(self, packet: MeshPacket) -> None:
        sender_id = packet['fromId']
        sender = self.bot.nodes.get_by_id(sender_id)
        sender_name = sender.user.long_name if sender else sender_id

        response = f"Hello, {sender_name}! How can I help you? (tip: try !help)"
        logging.debug(f"Sending response: '{response}'")

        self.bot.interface.sendText(response, destinationId=sender_id)
