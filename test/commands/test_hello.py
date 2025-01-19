import unittest
from unittest.mock import MagicMock

from src.bot import MeshtasticBot
from src.commands.hello import HelloCommand


class TestHelloCommand(unittest.TestCase):
    def setUp(self):
        self.bot = MeshtasticBot(address="localhost")
        self.bot.interface = MagicMock()
        self.command = HelloCommand(bot=self.bot)

    def test_handle_packet(self):
        packet = {'fromId': 'test_sender'}
        expected_response = "Hello, test_sender! How can I help you? (tip: try !help)"

        self.command.handle_packet(packet)

        self.bot.interface.sendText.assert_called_once_with(expected_response, destinationId='test_sender')


if __name__ == '__main__':
    unittest.main()
