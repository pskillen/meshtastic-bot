import logging
from meshtastic.protobuf.mesh_pb2 import MeshPacket

from src.commands.command import AbstractCommand


class PingCommand(AbstractCommand):
    def __init__(self, bot):
        super().__init__(bot, 'ping')

    def handle_packet(self, packet: MeshPacket) -> None:
        message = packet['decoded']['text']
        
        hop_start = packet.get('hopStart', 0)
        hop_limit = packet.get('hopLimit', 0)
        hops_away = hop_start - hop_limit

        # self.react_in_dm(packet, "🏓")

        # trim off the '!ping' command from the message
        additional = message[5:].strip()

        response = f"!pong"
        if additional:
            response = f"!pong: {additional}"

        response += f" (ping took {hops_away} hops)"
        
        self.reply_in_dm(packet, response)

    def get_command_for_logging(self, message: str) -> (str, list[str] | None, str | None):
        return self._gcfl_base_command_and_args(message)