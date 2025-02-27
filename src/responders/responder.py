import logging
from abc import ABC, abstractmethod

from meshtastic.protobuf import portnums_pb2
from meshtastic.protobuf.mesh_pb2 import MeshPacket

from src.bot import MeshtasticBot


class AbstractResponder(ABC):
    bot: MeshtasticBot

    def __init__(self, bot: MeshtasticBot):
        self.bot = bot

    @abstractmethod
    def handle_packet(self, packet: MeshPacket) -> None:
        pass

    def reply_in_channel(self, packet: MeshPacket, message: str, want_ack=False) -> None:
        logging.debug(f"Sending response: '{message}' in channel {packet['channel']}")
        raise NotImplementedError()

    def reply_to(self, destination_id: str, message: str, want_ack=False) -> None:
        logging.debug(f"Sending response: '{message}'")
        self.bot.interface.sendText(message, destinationId=destination_id, wantAck=want_ack)

    def react_to(self, packet: MeshPacket, emoji: str) -> None:
        logging.debug(f"Reacting to message with emoji: '{emoji}'")

        reply_id = packet['id']
        sender = packet['from']
        channel = packet['channel'] if 'channel' in packet else 0

        # Encode the emoji string to its corresponding byte sequence
        emoji_bytes = emoji.encode('utf-8')

        # Construct the packet
        packet = MeshPacket()
        packet.to = sender
        packet.channel = channel
        packet.decoded.portnum = portnums_pb2.PortNum.TEXT_MESSAGE_APP
        packet.decoded.payload = emoji_bytes
        # packet.decoded.text = emoji
        packet.decoded.reply_id = reply_id
        packet.decoded.emoji = True
        packet.want_ack = False

        # Send the packet
        self.bot.interface._sendPacket(packet)
