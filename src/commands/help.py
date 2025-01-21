import logging

from meshtastic.protobuf.mesh_pb2 import MeshPacket

from src.bot import MeshtasticBot
from src.commands.command import AbstractCommand


class HelpCommand(AbstractCommand):
    def __init__(self, bot: MeshtasticBot):
        self.bot = bot

    def handle_packet(self, packet: MeshPacket) -> None:
        message = packet['decoded']['text']
        sender = packet['fromId']

        # trim off the '!help' command from the message
        additional = message[5:].strip().lstrip('!')

        if not additional:
            response = "Valid commands are: !ping, !hello, !help, !nodes"
        elif additional == "hello":
            response = "!hello - Responds with a greeting"
        elif additional == "ping":
            response = "!ping (+ optional correlation message) - Responds with a pong"
        elif additional == "nodes":
            response = "!nodes - Responds with details about the nodes this device has seen"
        elif additional == "help":
            response = "!help - Shows this help message"
        else:
            response = f"Unknown command: {additional}"

        self.respond(response, sender)

    def respond(self, message: str, destination_id: int) -> None:
        logging.debug(f"Sending response: '{message}'")
        self.bot.interface.sendText(message, destinationId=destination_id)
