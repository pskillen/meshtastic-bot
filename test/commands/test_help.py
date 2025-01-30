import unittest
from unittest.mock import MagicMock

from src.bot import MeshtasticBot
from src.commands.help import HelpCommand


class TestHelpCommand(unittest.TestCase):
    def setUp(self):
        self.bot = MeshtasticBot(address="localhost")
        self.bot.interface = MagicMock()
        self.command = HelpCommand(bot=self.bot)

    def test_handle_packet_no_additional_message(self):
        packet = {'decoded': {'text': '!help'}, 'fromId': 'test_sender'}
        expected_response = "Valid commands are: !ping, !hello, !help, !nodes"

        self.command.handle_packet(packet)

        self.bot.interface.sendText.assert_called_once_with(expected_response, destinationId='test_sender')

    def test_handle_packet_hello_command(self):
        packet = {'decoded': {'text': '!help hello'}, 'fromId': 'test_sender'}
        expected_response = "!hello: responds with a greeting"

        self.command.handle_packet(packet)

        self.bot.interface.sendText.assert_called_once_with(expected_response, destinationId='test_sender')

    def test_handle_packet_ping_command(self):
        packet = {'decoded': {'text': '!help ping'}, 'fromId': 'test_sender'}
        expected_response = "!ping (+ optional correlation message): responds with a pong"

        self.command.handle_packet(packet)

        self.bot.interface.sendText.assert_called_once_with(expected_response, destinationId='test_sender')

    def test_handle_packet_help_command(self):
        packet = {'decoded': {'text': '!help help'}, 'fromId': 'test_sender'}
        expected_response = "!help: show this help message"

        self.command.handle_packet(packet)

        self.bot.interface.sendText.assert_called_once_with(expected_response, destinationId='test_sender')

    def test_handle_packet_unknown_command(self):
        packet = {'decoded': {'text': '!help unknown'}, 'fromId': 'test_sender'}
        expected_response = "Unknown command 'unknown'"

        self.command.handle_packet(packet)

        self.bot.interface.sendText.assert_called_once_with(expected_response, destinationId='test_sender')

    def test_handle_packet_ping_with_and_without_exclamation(self):
        packet_with_exclamation = {'decoded': {'text': '!help !ping'}, 'fromId': 'test_sender'}
        packet_without_exclamation = {'decoded': {'text': '!help ping'}, 'fromId': 'test_sender'}
        expected_response = "!ping (+ optional correlation message): responds with a pong"

        self.command.handle_packet(packet_with_exclamation)
        self.bot.interface.sendText.assert_called_with(expected_response, destinationId='test_sender')

        self.command.handle_packet(packet_without_exclamation)
        self.bot.interface.sendText.assert_called_with(expected_response, destinationId='test_sender')


if __name__ == '__main__':
    unittest.main()
