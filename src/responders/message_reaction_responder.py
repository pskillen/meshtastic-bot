import random

from meshtastic.protobuf.mesh_pb2 import MeshPacket

from src.bot import MeshtasticBot
from src.responders.responder import AbstractResponder


class MessageReactionResponder(AbstractResponder):
    emoji: str

    def __init__(self, bot: MeshtasticBot, emoji: str):
        super().__init__(bot)
        self.emoji = emoji

    def handle_packet(self, packet: MeshPacket) -> None:
        # Ensure the node is enrolled
        if not self._is_enrolled(packet['fromId']):
            return

        # pick an emoji to react with
        emoji = random.choice(self.emoji)

        # Respond to the message
        self.react_to(packet, emoji)

    def _is_enrolled(self, from_id: str) -> bool:
        # TODO: Implement this
        return from_id in self.bot.admin_nodes
