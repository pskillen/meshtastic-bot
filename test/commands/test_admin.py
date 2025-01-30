import unittest
from datetime import datetime, timedelta
from unittest.mock import Mock, MagicMock, patch

from src.bot import MeshtasticBot
from src.commands.admin import AdminCommand


class TestAdminCommand(unittest.TestCase):
    def setUp(self):
        self.bot = MeshtasticBot(address="localhost")
        self.bot.nodes = MagicMock()
        self.bot.admin_nodes = ['admin_node']
        self.command = AdminCommand(self.bot)
        self.packet = {'decoded': {'text': '!admin'}, 'fromId': 'test_sender'}

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
        self.bot.command_logger.command_stats = {
            'node1': {'cmd1': 2, 'cmd2': 3},
            'node2': {'cmd1': 1, 'cmd2': 2}
        }
        self.bot.command_logger.unknown_command_stats = {
            'node1': {'unknown-1': 1, 'unknown-2': 2},
            'node2': {'unknown-1': 2, 'unknown-3': 3},
        }

    @patch('src.commands.admin.AdminCommand.reply')
    def test_handle_packet_not_authorized(self, mock_reply):
        self.bot.admin_nodes = ['admin_node']
        self.command.handle_packet(self.packet)
        mock_reply.assert_called_once_with('test_sender', 'Sorry None, you are not authorized to use this command')

    @patch('src.commands.admin.AdminCommand.reply')
    def test_handle_packet_authorized(self, mock_reply):
        self.bot.admin_nodes = ['test_sender']
        self.command.handle_packet(self.packet)
        mock_reply.assert_not_called()

    @patch('src.commands.admin.AdminCommand.reply')
    def test_handle_base_command(self, mock_reply):
        self.command.handle_base_command(self.packet, [])
        mock_reply.assert_called_once_with(self.packet, 'Invalid command format - expected !admin <command> <args>')

    @patch('src.commands.admin.AdminCommand.reply')
    def test_reset_packets(self, mock_reply):
        self.command.reset_packets(self.packet, ['packets'])
        self.bot.nodes.reset_packets_today.assert_called_once()
        mock_reply.assert_called_once_with(self.packet, 'Packet counter reset')

    @patch('src.commands.admin.AdminCommand.reply')
    def test_reset_packets_missing_argument(self, mock_reply):
        self.command.reset_packets(self.packet, [])
        mock_reply.assert_called_once_with(self.packet, 'reset: Missing argument - options are: [\'packets\']')

    @patch('src.commands.admin.AdminCommand.reply')
    def test_reset_packets_unknown_argument(self, mock_reply):
        self.command.reset_packets(self.packet, ['unknown'])
        mock_reply.assert_called_once_with(self.packet,
                                           'reset: Unknown argument \'unknown\' - options are: [\'packets\']')

    @patch('src.commands.admin.AdminCommand.reply')
    def test_show_users_user_not_found(self, mock_reply):
        self.bot.get_node_by_short_name.return_value = None
        self.command.show_users(self.packet, ['unknown_user'])
        mock_reply.assert_called_once_with(self.packet, 'User \'unknown_user\' not found')

    @patch('src.commands.admin.AdminCommand.reply')
    def test_show_users_user_found(self, mock_reply):
        user = Mock()
        user.user.id = 'node1'
        user.user.long_name = 'Node 1'
        self.bot.get_node_by_short_name.return_value = user
        self.command.show_users(self.packet, ['Node1'])
        expected_response = 'Node 1 made 5 requests and 1 unknown\n- cmd1: 2\n- cmd2: 3\n'
        mock_reply.assert_called_once_with(self.packet, expected_response)

    @patch('src.commands.admin.AdminCommand.reply')
    def test_show_users_all_users(self, mock_reply):
        self.command.show_users(self.packet, [])
        expected_response = 'Users: 2\n- Node1: 6 requests\n- Node2: 3 requests\n'
        mock_reply.assert_called_once_with(self.packet, expected_response)

    @patch('src.commands.admin.AdminCommand.reply')
    def test_show_help(self, mock_reply):
        packet = {'decoded': {'text': '!admin help'}, 'fromId': 'test_sender'}
        self.command.handle_packet(packet)

        response = mock_reply.call_args[0][0]

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
