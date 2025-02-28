import unittest
from unittest.mock import MagicMock

from src.commands.template import TemplateCommand
from src.data_classes import MeshNode
from src.persistence.user_prefs import UserPrefs
from test.commands import CommandTestCase
from test.test_setup_data import build_test_text_packet, meshtastic_hex_to_int


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

    def test_user_prefs_rendering(self):
        sender = self.test_nodes[1]
        packet = build_test_text_packet('!myuserprefs', sender.user.id, self.bot.my_id)

        custom_user_prefs = UserPrefs(sender.user.id)
        custom_user_prefs.respond_to_testing = True

        self.bot.user_prefs_persistence = MagicMock()
        self.bot.user_prefs_persistence.get_user_prefs.return_value = custom_user_prefs

        template = "{{ 'Respond to testing: ' ~ user_prefs.respond_to_testing }}"
        command = TemplateCommand(self.bot, 'myuserprefs', template)
        command.handle_packet(packet)

        expected_rendered_message = "Respond to testing: True"
        self.assert_message_sent(expected_rendered_message, sender)


if __name__ == '__main__':
    unittest.main()
