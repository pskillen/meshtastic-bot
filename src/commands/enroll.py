from meshtastic.protobuf.mesh_pb2 import MeshPacket

from src.bot import MeshtasticBot
from src.commands.command import AbstractCommandWithSubcommands
from src.persistence.user_prefs import UserPrefs


class EnrollCommandHandler(AbstractCommandWithSubcommands):

    def __init__(self, bot: MeshtasticBot, base_command: str):
        super().__init__(bot, base_command)
        self.sub_commands['testing'] = self.enroll_testing

    def handle_base_command(self, packet: MeshPacket, args: list[str]) -> None:
        self.show_help(packet, [])

    def show_help(self, packet: MeshPacket, args: list[str]) -> None:
        response = (f"!enroll: (or !leave) bot responds to you in public channels:\n"
                    f"!enroll testing: bot will like your msg if you say 'test' or 'testing'\n")
        self.reply(packet, response)

    def enroll_testing(self, packet: MeshPacket, args: list[str]) -> None:
        sender_id = packet['fromId']
        user_prefs = self.bot.user_prefs_persistence.get_user_prefs(sender_id)

        if user_prefs is None:
            user_prefs = UserPrefs(sender_id)

        # if 'enroll' mode set True, else set False
        user_prefs.respond_to_testing.value = self.base_command == 'enroll'

        self.bot.user_prefs_persistence.persist_user_prefs(sender_id, user_prefs)

        response = (f"You've been {'enrolled' if user_prefs.respond_to_testing.value else 'unenrolled'} "
                    f"from responses to 'test' or 'testing' in public channels.")
        self.reply(packet, response)
