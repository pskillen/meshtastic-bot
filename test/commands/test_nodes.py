import unittest
from datetime import datetime, timedelta
from unittest.mock import MagicMock

from src.bot import MeshtasticBot
from src.commands.nodes import NodesCommand


class TestNodesCommand(unittest.TestCase):
    def setUp(self):
        self.bot = MeshtasticBot(address="localhost")
        self.bot.interface = MagicMock()
        self.bot.nodes = MagicMock()
        self.command = NodesCommand(bot=self.bot)

        # Mocking nodes data
        self.node1 = MagicMock()
        self.node1.user.id = 'node1'
        self.node1.user.short_name = 'Node1'
        self.node1.user.long_name = 'Node 1'
        self.node1.last_heard = int((datetime.now() - timedelta(minutes=5)).timestamp())

        self.node2 = MagicMock()
        self.node2.user.id = 'node2'
        self.node2.user.short_name = 'Node2'
        self.node2.user.long_name = 'Node 2'
        self.node2.last_heard = int((datetime.now() - timedelta(minutes=10)).timestamp())

        self.bot.nodes.list.return_value = [self.node1, self.node2]
        self.bot.nodes.get_online_nodes.return_value = [self.node1]
        self.bot.nodes.get_offline_nodes.return_value = [self.node2]
        self.bot.nodes.node_packets_today = {
            'node1': 5,
            'node2': 3
        }
        self.bot.nodes.node_packets_today_breakdown = {
            'node1': {
                'cmd1': 2,
                'cmd2': 3,
            },
            'node2': {
                'cmd1': 1,
                'cmd2': 2,
            }
        }
        self.bot.nodes.packet_counter_reset_time.strftime.return_value = '12:00:00'

    def test_handle_base_command(self):
        packet = {'decoded': {'text': '!nodes'}, 'fromId': 'test_sender'}

        self.command.handle_packet(packet)

        expected_response = "1 nodes online, 1 offline.\nRecent nodes:\n"
        expected_response += "- Node1 (5m ago)\n"
        expected_response += "- Node2 (10m ago)\n"
        self.bot.interface.sendText.assert_called_once_with(expected_response, destinationId='test_sender')

    def test_handle_busy_command(self):
        packet = {'decoded': {'text': '!nodes busy'}, 'fromId': 'test_sender'}

        self.command.handle_packet(packet)

        expected_response = "1 nodes online.\nBusy nodes:\n"
        expected_response += "- Node1 (5 pkts)\n"
        expected_response += "- Node2 (3 pkts)\n"
        expected_response += "(last reset at 12:00:00)"
        self.bot.interface.sendText.assert_called_once_with(expected_response, destinationId='test_sender')

    def test_handle_busy_detailed_command(self):
        packet = {'decoded': {'text': '!nodes busy detailed'}, 'fromId': 'test_sender'}

        self.command.handle_packet(packet)

        self.bot.interface.sendText.assert_called()

    def test_show_help(self):
        packet = {'decoded': {'text': '!nodes help'}, 'fromId': 'test_sender'}
        self.command.handle_packet(packet)

        response = self.bot.interface.sendText.call_args[0][0]

        # summary line should be in the response
        want = f"!{self.command.base_command}: "
        self.assertIn(want, response)

        # each sub_command in command should appear in the response
        for sub_command in self.command.sub_commands:
            # we can skip the '!cmd help' subcommand
            if sub_command == 'help':
                continue
            # and the empty string subcommand
            if sub_command == '':
                continue

            want = f"!{self.command.base_command} {sub_command}: "
            self.assertIn(want, response)


if __name__ == '__main__':
    unittest.main()
