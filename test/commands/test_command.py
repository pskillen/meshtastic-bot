import unittest
from unittest.mock import MagicMock

from meshtastic.protobuf.mesh_pb2 import MeshPacket

from src.bot import MeshtasticBot
from src.commands.command import AbstractCommand, AbstractCommandWithSubcommands


class ConcreteCommand(AbstractCommand):
    def handle_packet(self, packet: MeshPacket) -> None:
        self.reply(packet, "Handled")


class ConcreteCommandWithSubcommands(AbstractCommandWithSubcommands):
    def handle_base_command(self, packet: MeshPacket, args: list[str]) -> None:
        self.reply(packet, "Base command handled")

    def show_help(self, packet: MeshPacket, args: list[str]) -> None:
        self.reply(packet, "Help shown")


class TestAbstractCommand(unittest.TestCase):
    def setUp(self):
        self.bot = MeshtasticBot(address="localhost")
        self.bot.interface = MagicMock()
        self.command = ConcreteCommand(bot=self.bot, base_command="test")

    def test_handle_packet(self):
        packet = {'decoded': {'text': '!test'}, 'fromId': 'test_sender'}
        self.command.handle_packet(packet)
        self.bot.interface.sendText.assert_called_once_with("Handled", destinationId='test_sender')

    def test_reply(self):
        packet = {'decoded': {'text': '!test'}, 'fromId': 'test_sender'}
        self.command.reply(packet, "Reply message")
        self.bot.interface.sendText.assert_called_once_with("Reply message", destinationId='test_sender')


class TestAbstractCommandWithSubcommands(unittest.TestCase):
    def setUp(self):
        self.bot = MeshtasticBot(address="localhost")
        self.bot.interface = MagicMock()
        self.command = ConcreteCommandWithSubcommands(bot=self.bot, base_command_str="test")

    def test_handle_base_command(self):
        packet = {'decoded': {'text': '!test'}, 'fromId': 'test_sender'}
        self.command.handle_packet(packet)
        self.bot.interface.sendText.assert_called_once_with("Base command handled", destinationId='test_sender')

    def test_show_help(self):
        packet = {'decoded': {'text': '!test help'}, 'fromId': 'test_sender'}
        self.command.handle_packet(packet)
        self.bot.interface.sendText.assert_called_once_with("Help shown", destinationId='test_sender')

    def test_unknown_subcommand(self):
        packet = {'decoded': {'text': '!test unknown'}, 'fromId': 'test_sender'}
        self.command.handle_packet(packet)
        self.bot.interface.sendText.assert_called_once_with("Unknown command 'unknown'", destinationId='test_sender')


if __name__ == '__main__':
    unittest.main()
