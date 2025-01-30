import unittest
from unittest.mock import Mock, patch

from src.bot import MeshtasticBot
from src.commands.template import TemplateCommand


class TestTemplateCommand(unittest.TestCase):
    def setUp(self):
        self.bot = Mock(spec=MeshtasticBot)
        self.template = "Hello, {{ sender_name }}! You sent: {{ rx_message }}"
        self.command = TemplateCommand(self.bot, 'template', self.template)
        self.packet = {
            'decoded': {'text': '!template test message'},
            'fromId': 'test_sender',
            'hopStart': 5,
            'hopLimit': 3
        }

    @patch('src.commands.template.TemplateCommand.reply_to')
    def test_handle_packet(self, mock_reply_to):
        sender = Mock()
        sender.user.long_name = 'Test Sender'
        sender.user.short_name = 'Test'
        self.bot.nodes.get_by_id.return_value = sender
        self.bot.get_global_context.return_value = {}

        self.command.handle_packet(self.packet)

        expected_message = "Hello, Test Sender! You sent: !template test message"
        mock_reply_to.assert_called_once_with('test_sender', expected_message)

    @patch('src.commands.template.TemplateCommand.reply_to')
    def test_handle_packet_no_sender(self, mock_reply_to):
        self.bot.nodes.get_by_id.return_value = None
        self.bot.get_global_context.return_value = {}

        self.command.handle_packet(self.packet)

        expected_message = "Hello, test_sender! You sent: !template test message"
        mock_reply_to.assert_called_once_with('test_sender', expected_message)

    @patch('src.commands.template.TemplateCommand.reply_to')
    def test_handle_packet_with_global_context(self, mock_reply_to):
        sender = Mock()
        sender.user.long_name = 'Test Sender'
        sender.user.short_name = 'Test'
        self.bot.nodes.get_by_id.return_value = sender
        self.bot.get_global_context.return_value = {'global_var': 'global_value'}

        self.command.handle_packet(self.packet)

        expected_message = "Hello, Test Sender! You sent: !template test message"
        mock_reply_to.assert_called_once_with('test_sender', expected_message)


if __name__ == '__main__':
    unittest.main()
