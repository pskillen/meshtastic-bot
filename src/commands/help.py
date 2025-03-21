from meshtastic.protobuf.mesh_pb2 import MeshPacket

from src.bot import MeshtasticBot
from src.commands.command import AbstractCommandWithSubcommands


class HelpCommand(AbstractCommandWithSubcommands):
    def __init__(self, bot: MeshtasticBot):
        super().__init__(bot, 'help')
        self.sub_commands['hello'] = self.handle_hello
        self.sub_commands['ping'] = self.handle_ping
        self.sub_commands['nodes'] = self.handle_nodes
        self.sub_commands['whoami'] = self.handle_whoami
        self.sub_commands['prefs'] = self.handle_prefs
        # self.sub_commands['enroll'] = self.handle_enroll
        # self.sub_commands['leave'] = self.handle_leave

    def handle_base_command(self, packet: MeshPacket, args: list[str]) -> None:
        subcmds = self.sub_commands.keys()
        subcmds = filter(None, subcmds)  # remove empty strings
        subcmds = [f"!{cmd}" for cmd in subcmds]

        response = f"Valid commands are: {', '.join(subcmds)}"
        self.reply(packet, response)

    def handle_hello(self, packet: MeshPacket, args: list[str]) -> None:
        response = "!hello: responds with a greeting"
        self.reply(packet, response)

    def handle_ping(self, packet: MeshPacket, args: list[str]) -> None:
        response = "!ping (+ optional correlation message): responds with a pong"
        self.reply(packet, response)

    def handle_nodes(self, packet: MeshPacket, args: list[str]) -> None:
        response = "!nodes: details about the nodes this device has seen"
        self.reply(packet, response)

    def show_help(self, packet: MeshPacket, args: list[str]) -> None:
        response = "!help: show this help message"
        self.reply(packet, response)

    def handle_whoami(self, packet: MeshPacket, args: list[str]) -> None:
        response = "!whoami: show details about yourself"
        self.reply(packet, response)

    def handle_prefs(self, packet: MeshPacket, args: list[str]) -> None:
        response = "!prefs: show and update your user preferences"
        self.reply(packet, response)

    def handle_enroll(self, packet: MeshPacket, args: list[str]) -> None:
        response = "!enroll: bot will respond to certain messages from you on public channels"
        self.reply(packet, response)

    def handle_leave(self, packet: MeshPacket, args: list[str]) -> None:
        response = "!leave: bot will not respond to you on public channels"
        self.reply(packet, response)

    def get_command_for_logging(self, message: str) -> (str, list[str] | None, str | None):
        return self._gcfl_base_command_and_args(message)
