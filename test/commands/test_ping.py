import unittest

from src.commands.ping import PingCommand
from test.commands import CommandTestCase
from test.test_setup_data import build_test_text_packet


class TestPingCommand(CommandTestCase):
    command: PingCommand

    def setUp(self):
        super().setUp()
        self.command = PingCommand(bot=self.bot)

    def test_handle_packet_no_additional_message(self):
        packet = build_test_text_packet('!ping', self.test_nodes[1].user.id, self.bot.my_id)
        packet['hopStart'] = 3
        packet['hopLimit'] = 3
        expected_response = "!pong (ping took 0 hops)"

        self.command.handle_packet(packet)

        self.assert_message_sent(expected_response, self.test_nodes[1])

    def test_handle_packet_with_additional_message(self):
        packet = build_test_text_packet('!ping extra message', self.test_nodes[1].user.id, self.bot.my_id)
        packet['hopStart'] = 3
        packet['hopLimit'] = 3
        expected_response = "!pong: extra message (ping took 0 hops)"

        self.command.handle_packet(packet)

        self.assert_message_sent(expected_response, self.test_nodes[1])

    def test_handle_packet_with_hop_count(self):
        packet = build_test_text_packet('!ping', self.test_nodes[1].user.id, self.bot.my_id)
        packet['hopStart'] = 3
        packet['hopLimit'] = 2
        expected_response = "!pong (ping took 1 hops)"

        self.command.handle_packet(packet)

        self.assert_message_sent(expected_response, self.test_nodes[1])


if __name__ == '__main__':
    unittest.main()
