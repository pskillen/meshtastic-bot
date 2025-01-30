from meshtastic.protobuf.mesh_pb2 import MeshPacket

from src.bot import MeshtasticBot
from src.commands.command import AbstractCommandWithSubcommands


class HelpCommand(AbstractCommandWithSubcommands):
    def __init__(self, bot: MeshtasticBot):
        super().__init__(bot, 'help')
        self.sub_commands['hello'] = self.handle_hello
        self.sub_commands['ping'] = self.handle_ping
        self.sub_commands['nodes'] = self.handle_nodes

    def handle_base_command(self, packet: MeshPacket, args: list[str]) -> None:
        response = "Valid commands are: !ping, !hello, !help, !nodes"
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
