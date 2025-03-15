import unittest

from src.commands.hello import HelloCommand
from test.commands import CommandTestCase
from test.test_setup_data import build_test_text_packet


class TestHelloCommand(CommandTestCase):
    command: HelloCommand

    def setUp(self):
        super().setUp()
        self.command = HelloCommand(bot=self.bot)

    def test_handle_packet(self):
        sender_node = self.test_nodes[1]

        packet = build_test_text_packet('!hello', sender_node.user.id, self.bot.my_id)
        expected_response = f"Hello, {sender_node.user.long_name}! How can I help you? (tip: try !help). I'm a bot maintained by PDY4 / pskillen@gmail.com"

        self.command.handle_packet(packet)

        self.assert_message_sent(expected_response, sender_node)


if __name__ == '__main__':
    unittest.main()
