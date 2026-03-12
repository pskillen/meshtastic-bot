from meshtastic.protobuf.mesh_pb2 import MeshPacket

from src.bot import MeshtasticBot
from src.commands.command import AbstractCommand


class HelloCommand(AbstractCommand):
    def __init__(self, bot: MeshtasticBot):
        super().__init__(bot, 'hello')

    def handle_packet(self, packet: MeshPacket) -> None:
        sender_id = packet['fromId']
        sender = self.bot.node_db.get_by_id(sender_id)
        sender_name = sender.long_name if sender else sender_id

        response = f"Hello, {sender_name}! (tip: try !help). I'm a bot maintained by MTEK original PDY4 / https://github.com/pskillen/meshtastic-bot"
        self.reply_to(sender_id, response)

    def get_command_for_logging(self, message: str) -> (str, list[str] | None, str | None):
        return self._gcfl_just_base_command(message)
