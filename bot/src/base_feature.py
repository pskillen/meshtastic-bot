import logging
from abc import ABC

from meshtastic.protobuf.mesh_pb2 import MeshPacket

from src.bot import MeshtasticBot


class AbstractBaseFeature(ABC):
    """
    This class represents base functionality for commands, responders, etc
    """
    bot: MeshtasticBot

    def __init__(self, bot: MeshtasticBot):
        self.bot = bot

    def reply_in_channel(self, packet: MeshPacket, message: str, want_ack=False) -> None:
        """
        Reply to a message in the same channel
        """
        channel = packet['channel'] if 'channel' in packet else 0
        self.message_in_channel(channel, message, want_ack)

    def message_in_channel(self, channel: int, message: str, want_ack=False) -> None:
        """
        Send a message in a channel
        """
        logging.debug(f"Sending message: '{message}'")
        self.bot.interface.sendText(message, channelIndex=channel, wantAck=want_ack)

    def reply_in_dm(self, packet: MeshPacket, message: str, want_ack=False) -> None:
        """
        Reply in a direct message to a user
        """
        destination_id = packet['fromId']
        self.message_in_dm(destination_id, message, want_ack)

    def message_in_dm(self, destination_id: str, message: str, want_ack=False) -> None:
        """
        Reply in a direct message to a user
        """
        logging.debug(f"Sending DM: '{message}'")
        self.bot.interface.sendText(message, destinationId=destination_id, wantAck=want_ack)

    def react_in_channel(self, packet: MeshPacket, emoji: str) -> None:
        """
        Send a reaction emoji to a message
        """
        logging.debug(f"Reacting to message with emoji: '{emoji}'")

        reply_id = packet['id']
        channel = packet['channel'] if 'channel' in packet else 0

        self.bot.interface.sendReaction(emoji, messageId=reply_id, channelIndex=channel)

    def react_in_dm(self, packet: MeshPacket, emoji: str) -> None:
        """
        Send a reaction emoji to a message
        """
        logging.debug(f"Reacting to message with emoji: '{emoji}'")

        reply_id = packet['id']
        sender = packet['fromId']

        self.bot.interface.sendReaction(emoji, messageId=reply_id, destinationId=sender)
