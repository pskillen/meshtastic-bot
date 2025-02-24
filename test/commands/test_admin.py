import unittest

from src.commands.admin import AdminCommand
from test.commands import CommandWSCTestCase
from test.test_setup_data import build_test_text_packet


class TestAdminCommand(CommandWSCTestCase):
    command: AdminCommand

    def setUp(self):
        super().setUp()
        self.command = AdminCommand(self.bot)

    def test_handle_packet_not_authorized(self):
        packet = build_test_text_packet('!admin', self.test_non_admin_nodes[0].user.id, self.bot.my_id)
        self.command.handle_packet(packet)
        self.mock_interface.sendText.assert_called_once_with(
            f"Sorry {self.test_non_admin_nodes[0].user.long_name}, you are not authorized to use this command",
            destinationId=self.test_non_admin_nodes[0].user.id
        )

    def test_handle_packet_authorized(self):
        packet = build_test_text_packet('!admin', self.test_admin_nodes[0].user.id, self.bot.my_id)
        self.command.handle_packet(packet)
        self.mock_interface.sendText.assert_called_once_with(
            "Invalid command format - expected !admin <command> <args>",
            destinationId=self.test_admin_nodes[0].user.id
        )

    def test_handle_base_command(self):
        packet = build_test_text_packet('!admin', self.test_admin_nodes[0].user.id, self.bot.my_id)
        self.command.handle_packet(packet)
        self.mock_interface.sendText.assert_called_once_with(
            "Invalid command format - expected !admin <command> <args>",
            destinationId=self.test_admin_nodes[0].user.id
        )

    def test_reset_packets(self):
        packet = build_test_text_packet('!admin reset packets', self.test_admin_nodes[0].user.id, self.bot.my_id)
        self.command.handle_packet(packet)

        # Check that the packet counters have been reset
        self.assertEqual(self.bot.nodes.node_packets_today, {})
        self.assertEqual(self.bot.nodes.node_packets_today_breakdown, {})

        self.mock_interface.sendText.assert_called_once_with(
            "Packet counter reset",
            destinationId=self.test_admin_nodes[0].user.id
        )

    def test_reset_packets_missing_argument(self):
        packet = build_test_text_packet('!admin reset', self.test_admin_nodes[0].user.id, self.bot.my_id)
        self.command.handle_packet(packet)
        self.mock_interface.sendText.assert_called_once_with(
            "reset: Missing argument - options are: ['packets']",
            destinationId=self.test_admin_nodes[0].user.id
        )

    def test_reset_packets_unknown_argument(self):
        packet = build_test_text_packet('!admin reset unknown', self.test_admin_nodes[0].user.id, self.bot.my_id)
        self.command.handle_packet(packet)
        self.mock_interface.sendText.assert_called_once_with(
            "reset: Unknown argument 'unknown' - options are: ['packets']",
            destinationId=self.test_admin_nodes[0].user.id
        )

    def test_show_users_user_not_found(self):
        packet = build_test_text_packet('!admin users !ffffff', self.test_admin_nodes[0].user.id, self.bot.my_id)
        self.command.handle_packet(packet)
        self.mock_interface.sendText.assert_called_once_with(
            "User '!ffffff' not found",
            destinationId=self.test_admin_nodes[0].user.id
        )

    def test_show_users_user_found(self):
        target_node = self.test_nodes[1]  # 0 is my_id

        packet = build_test_text_packet(f'!admin users {target_node.user.short_name}',
                                        self.test_admin_nodes[0].user.id, self.bot.my_id)
        self.command.handle_packet(packet)

        # Infer the expected response from the test data
        command_stats = self.bot.command_logger.command_stats.get(target_node.user.id, {})
        unknown_command_stats = self.bot.command_logger.unknown_command_stats.get(target_node.user.id, {})

        expected_response = f"{target_node.user.long_name} made {sum(command_stats.values())} requests and {sum(unknown_command_stats.values())} unknown\n"
        for cmd, count in command_stats.items():
            expected_response += f"- {cmd}: {count}\n"
        for cmd, count in unknown_command_stats.items():
            expected_response += f"- {cmd}: {count}\n"

        self.mock_interface.sendText.assert_called_once_with(
            expected_response,
            destinationId=self.test_admin_nodes[0].user.id
        )

    def test_show_users_all_users(self):
        packet = build_test_text_packet('!admin users', self.test_admin_nodes[0].user.id, self.bot.my_id)
        self.command.handle_packet(packet)

        # Infer the expected response from the test data
        expected_response = f"Users: {len(self.test_nodes)}\n"

        user_ids = set(self.bot.command_logger.command_stats.keys()).union(
            self.bot.command_logger.unknown_command_stats.keys())

        for node_id in user_ids:
            node = self.bot.nodes.get_by_id(node_id)
            request_count = sum(self.bot.command_logger.command_stats.get(node_id, {}).values()) \
                            + sum(self.bot.command_logger.unknown_command_stats.get(node_id, {}).values())
            expected_response += f"- {node.user.short_name}: {request_count} requests\n"

        self.mock_interface.sendText.assert_called_once_with(
            expected_response,
            destinationId=self.test_admin_nodes[0].user.id
        )

    def test_show_help(self):
        # Override base test because we need an admin node
        packet = build_test_text_packet('!admin help', self.test_admin_nodes[0].user.id, self.bot.my_id)
        self.assert_show_help_for_command(packet)


if __name__ == '__main__':
    unittest.main()
