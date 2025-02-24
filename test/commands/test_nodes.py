import unittest

from src.commands.nodes import NodesCommand
from src.helpers import pretty_print_last_heard
from test.commands import CommandWSCTestCase
from test.test_setup_data import build_test_text_packet


class TestNodesCommand(CommandWSCTestCase):
    command: NodesCommand

    def setUp(self):
        super().setUp()
        self.command = NodesCommand(self.bot)

        self.online_count = len(self.bot.nodes.get_online_nodes())
        self.offline_count = len(self.bot.nodes.get_offline_nodes())

    def test_handle_base_command(self):
        packet = build_test_text_packet('!nodes', self.test_nodes[1].user.id, self.bot.my_id)
        self.command.handle_packet(packet)

        expected_response = f"{self.online_count} nodes online, {self.offline_count} offline.\nRecent nodes:\n"

        # nodes in response will be sorted by last_heard (desc)
        all_nodes = sorted(self.test_nodes, key=lambda x: x.last_heard, reverse=True)

        for node in all_nodes[:5]:
            friendly_time = pretty_print_last_heard(node.last_heard)
            expected_response += f"- {node.user.short_name} ({friendly_time})\n"
        self.mock_interface.sendText.assert_called_once_with(expected_response,
                                                             destinationId=self.test_nodes[1].user.id)

    def test_handle_busy_command(self):
        packet = build_test_text_packet('!nodes busy', self.test_nodes[1].user.id, self.bot.my_id)
        self.command.handle_packet(packet)

        # nodes in response will be sorted by packets_today (desc)
        sorted_nodes = sorted(self.bot.nodes.node_packets_today.items(), key=lambda x: x[1], reverse=True)

        expected_response = f"{self.online_count} nodes online.\nBusy nodes:\n"
        for node_id, packet_count in sorted_nodes[:5]:
            node = self.bot.nodes.get_by_id(node_id)
            expected_response += f"- {node.user.short_name} ({packet_count} pkts)\n"

        last_reset_time = self.bot.nodes.packet_counter_reset_time.strftime("%H:%M:%S")

        expected_response += f"(last reset at {last_reset_time})"

        self.mock_interface.sendText.assert_called_once_with(
            expected_response,
            destinationId=self.test_nodes[1].user.id)

    def test_handle_busy_detailed_command(self):
        packet = build_test_text_packet('!nodes busy detailed', self.test_nodes[1].user.id, self.bot.my_id)
        self.command.handle_packet(packet)

        self.mock_interface.sendText.assert_called()
        self.assertEqual(self.mock_interface.sendText.call_count, 3)

    def test_handle_busy_specific_node(self):
        target_node = self.test_nodes[1]  # 0 is my_id

        packet = build_test_text_packet(f'!nodes busy {target_node.user.short_name}', self.test_nodes[1].user.id,
                                        self.bot.my_id)
        self.command.handle_packet(packet)

        # Infer the expected response from the test data
        packets_today = self.bot.nodes.node_packets_today.get(target_node.user.id, 0)
        packet_breakdown_today = self.bot.nodes.node_packets_today_breakdown.get(target_node.user.id, {})

        expected_response = f"{target_node.user.long_name} ({target_node.user.short_name})\n"
        expected_response += f"Last heard: {pretty_print_last_heard(target_node.last_heard)}\n"
        expected_response += f"Pkts today: {packets_today}\n"

        sorted_breakdown = sorted(packet_breakdown_today.items(), key=lambda x: x[1], reverse=True)
        for packet_type, count in sorted_breakdown:
            expected_response += f"- {packet_type}: {count}\n"

        self.mock_interface.sendText.assert_called_once_with(
            expected_response,
            destinationId=self.test_nodes[1].user.id
        )


if __name__ == '__main__':
    unittest.main()
