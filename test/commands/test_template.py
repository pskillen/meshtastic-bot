import unittest

from src.commands.template import TemplateCommand
from src.data_classes import MeshNode
from test.commands import CommandTestCase
from test.test_setup_data import build_test_text_packet


class TestTemplateCommand(CommandTestCase):
    command: TemplateCommand

    def setUp(self):
        super().setUp()
        self.template = "Hello, {{ sender_name }}! You sent: {{ rx_message }}"
        self.command = TemplateCommand(self.bot, 'template', self.template)

    def test_handle_packet(self):
        sender = self.test_nodes[1]
        packet = build_test_text_packet('!template test message', sender.user.id, self.bot.my_id)
        packet['hopStart'] = 5
        packet['hopLimit'] = 3

        self.command.handle_packet(packet)

        expected_message = f"Hello, {sender.user.long_name}! You sent: !template test message"
        self.assert_message_sent(expected_message, sender)

    def test_handle_packet_no_sender(self):
        sender = MeshNode()
        sender.user = MeshNode.User()
        sender.user.id = '1234567890'

        packet = build_test_text_packet('!template test message', sender.user.id, self.bot.my_id)
        packet['hopStart'] = 5
        packet['hopLimit'] = 3

        self.command.handle_packet(packet)

        expected_message = f"Hello, {sender.user.id}! You sent: !template test message"
        self.assert_message_sent(expected_message, sender)


if __name__ == '__main__':
    unittest.main()
