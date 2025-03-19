import unittest
from unittest.mock import patch

from src.responders.message_reaction_responder import MessageReactionResponder
from test.responders import ResponderTestCase
from test.test_setup_data import build_test_text_packet


class TestMessageReactionResponder(ResponderTestCase):
    responder: MessageReactionResponder

    def setUp(self):
        super().setUp()
        self.responder = MessageReactionResponder(bot=self.bot, emoji="👍😊🎉")

    @patch('random.choice', return_value="👍")
    def test_handle_packet(self, mock_random_choice):
        sender_node = self.test_nodes[1]

        packet = build_test_text_packet('Hello', sender_node.user.id, self.bot.my_id, channel=1)
        self.responder.handle_packet(packet)

        self.assert_reaction_sent("👍", packet['id'], channel=1)

    def test_handle_packet_not_enrolled(self):
        sender_node = self.test_nodes[1]

        packet = build_test_text_packet('Hello', sender_node.user.id, self.bot.my_id, channel=1)
        self.bot.user_prefs_persistence.get_user_prefs.return_value = None
        self.responder.handle_packet(packet)

        self.bot.interface.sendReaction.assert_not_called()


if __name__ == '__main__':
    unittest.main()
