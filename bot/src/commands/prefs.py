from meshtastic.protobuf.mesh_pb2 import MeshPacket

from src.bot import MeshtasticBot
from src.commands.command import AbstractCommandWithSubcommands
from src.persistence.user_prefs import UserPrefs


class PrefsCommandHandler(AbstractCommandWithSubcommands):

    def __init__(self, bot: MeshtasticBot):
        super().__init__(bot, 'prefs', error_on_invalid_subcommand=False)
        self.sub_commands['testing'] = self.set_boolean_pref

    def handle_base_command(self, packet: MeshPacket, args: list[str]) -> None:
        sender_id = packet['fromId']
        user_prefs = self.bot.user_prefs_persistence.get_user_prefs(sender_id)

        if user_prefs is None:
            user_prefs = UserPrefs(sender_id)

        response = (f"Your preferences:\n"
                    f"Respond to 'testing': {'enabled' if user_prefs.respond_to_testing.value else 'disabled'}\n"
                    )

        self.reply(packet, response)

    def set_boolean_pref(self, packet: MeshPacket, args: list[str], sub_command_name: str) -> None:
        # verify args are specified
        if len(args) == 0:
            return self.show_help(packet, args)

        pref_name = sub_command_name

        # verify mode is valid
        value_str = args[0].lower()
        if value_str not in ['enable', 'disable']:
            response = f"Invalid mode for '{sub_command_name}'. Please specify 'enable' or 'disable'."
            return self.reply(packet, response)
        value_bool = value_str == 'enable'

        sender_id = packet['fromId']
        user_prefs = self.bot.user_prefs_persistence.get_user_prefs(sender_id)

        if user_prefs is None:
            user_prefs = UserPrefs(sender_id)

        if pref_name == 'testing':
            user_prefs.respond_to_testing.value = value_bool
            response = (f"You've {'enabled' if user_prefs.respond_to_testing.value else 'disabled'} "
                        f"bot responses to 'test' or 'testing' in public channels.")
        else:
            # Oops, this shouldn't happen, but it's a server error so don't complain to the user
            return

        # Store prefs and send reply
        self.bot.user_prefs_persistence.persist_user_prefs(sender_id, user_prefs)
        self.reply(packet, response)

    def show_help(self, packet: MeshPacket, args: list[str]) -> None:
        response = (f"!prefs: configure bot settings related to your node:\n"
                    f"!prefs testing enable/disable: bot will like your msg if you say 'test' or 'testing'\n"
                    )
        self.reply(packet, response)

    def get_command_for_logging(self, message: str) -> (str, list[str] | None, str | None):
        return self._gcfl_base_command_and_args(message)
