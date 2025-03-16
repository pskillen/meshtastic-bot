import unittest

from meshtastic.protobuf.mesh_pb2 import MeshPacket

from src.commands.command import AbstractCommand, AbstractCommandWithSubcommands
from test.commands import CommandTestCase, CommandWSCTestCase
from test.test_setup_data import build_test_text_packet


class ConcreteCommand(AbstractCommand):
    def handle_packet(self, packet: MeshPacket) -> None:
        self.reply(packet, "Handled")

    def get_command_for_logging(self, message: str) -> (str, list[str] | None, str | None):
        return self._gcfl_base_command_and_args(message)


class ConcreteCommandWithSubcommands(AbstractCommandWithSubcommands):
    def handle_base_command(self, packet: MeshPacket, args: list[str]) -> None:
        self.reply(packet, "Base command handled")

    def show_help(self, packet: MeshPacket, args: list[str]) -> None:
        self.reply(packet, "Help shown")

    def get_command_for_logging(self, message: str) -> (str, list[str] | None, str | None):
        return self._gcfl_base_onesub_args(message)


class TestAbstractCommand(CommandTestCase):
    command: ConcreteCommand

    def setUp(self):
        super().setUp()
        self.command = ConcreteCommand(bot=self.bot, base_command="test")

    def test_handle_packet(self):
        packet = build_test_text_packet('!test', self.test_nodes[1].user.id, self.bot.my_id)
        self.command.handle_packet(packet)

        self.assert_message_sent("Handled", self.test_nodes[1])

    def test_reply(self):
        packet = build_test_text_packet('!test', self.test_nodes[1].user.id, self.bot.my_id)
        self.command.reply(packet, "Reply message")

        self.assert_message_sent("Reply message", self.test_nodes[1])


class TestAbstractCommandWithSubcommands(CommandWSCTestCase):
    command: ConcreteCommandWithSubcommands

    def setUp(self):
        super().setUp()
        self.command = ConcreteCommandWithSubcommands(bot=self.bot, base_command_str="test")

    def test_handle_base_command(self):
        packet = build_test_text_packet('!test', self.test_nodes[1].user.id, self.bot.my_id)
        self.command.handle_packet(packet)

        self.assert_message_sent("Base command handled", self.test_nodes[1])

    def test_show_help(self):
        packet = build_test_text_packet('!test help', self.test_nodes[1].user.id, self.bot.my_id)
        self.command.handle_packet(packet)

        self.assert_message_sent("Help shown", self.test_nodes[1])

    def test_unknown_subcommand(self):
        packet = build_test_text_packet('!test unknown', self.test_nodes[1].user.id, self.bot.my_id)
        self.command.handle_packet(packet)

        self.assert_message_sent("Unknown command 'unknown'", self.test_nodes[1])


if __name__ == '__main__':
    unittest.main()
