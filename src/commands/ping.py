from meshtastic.protobuf.mesh_pb2 import MeshPacket

from src.bot import MeshtasticBot
from src.commands.command import AbstractCommand


class PingCommand(AbstractCommand):
    def __init__(self, bot: MeshtasticBot):
        self.bot = bot

    def handle_packet(self, packet: MeshPacket) -> None:
        message = packet['decoded']['text']
        sender = packet['fromId']
        hops_away = packet['hopStart'] - packet['hopLimit']

        # trim off the '!ping' command from the message
        additional = message[5:].strip()

        response = f"!pong"
        if additional:
            response = f"!pong: {additional}"

        response += f" (ping took {hops_away} hops)"

        print(f"Sending response: '{response}'")

        self.bot.interface.sendText(response, destinationId=sender)
