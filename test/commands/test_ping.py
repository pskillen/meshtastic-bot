import unittest
from unittest.mock import MagicMock

from src.bot import MeshtasticBot
from src.commands.ping import PingCommand


class TestPingCommand(unittest.TestCase):
    def setUp(self):
        self.bot = MeshtasticBot(address="localhost")
        self.bot.interface = MagicMock()
        self.command = PingCommand(bot=self.bot)

    def test_handle_packet_no_additional_message(self):
        packet = {'decoded': {'text': '!ping'}, 'fromId': 'test_sender', 'hopStart': 3, 'hopLimit': 3}
        expected_response = "!pong (ping took 0 hops)"

        self.command.handle_packet(packet)

        self.bot.interface.sendText.assert_called_once_with(expected_response, destinationId='test_sender')

    def test_handle_packet_with_additional_message(self):
        packet = {'decoded': {'text': '!ping extra message'}, 'fromId': 'test_sender', 'hopStart': 3, 'hopLimit': 3}
        expected_response = "!pong: extra message (ping took 0 hops)"

        self.command.handle_packet(packet)

        self.bot.interface.sendText.assert_called_once_with(expected_response, destinationId='test_sender')

    def test_handle_packet_with_hop_count(self):
        packet = {'decoded': {'text': '!ping'}, 'fromId': 'test_sender', 'hopStart': 3, 'hopLimit': 2}
        expected_response = "!pong (ping took 1 hops)"

        self.command.handle_packet(packet)

        self.bot.interface.sendText.assert_called_once_with(expected_response, destinationId='test_sender')


if __name__ == '__main__':
    unittest.main()
