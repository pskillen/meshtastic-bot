import unittest
from abc import ABC
from unittest.mock import Mock

from meshtastic.protobuf.mesh_pb2 import MeshPacket

from src.bot import MeshtasticBot
from src.commands.command import AbstractCommand, AbstractCommandWithSubcommands
from src.data_classes import MeshNode
from test.test_setup_data import get_test_bot, build_test_text_packet


class CommandTestCase(unittest.TestCase, ABC):
    command: AbstractCommand

    bot: MeshtasticBot
    mock_interface: Mock
    test_admin_nodes: list[MeshNode] = []
    test_non_admin_nodes: list[MeshNode] = []
    test_nodes: list[MeshNode] = []

    def setUp(self):
        self.bot, self.test_non_admin_nodes, self.test_admin_nodes = get_test_bot()
        self.test_nodes = self.test_non_admin_nodes + self.test_admin_nodes
        self.mock_interface = self.bot.interface = Mock()

    def assert_message_sent(self, expected_response: str, to: MeshNode, want_ack: bool = False):
        self.mock_interface.sendText.assert_called_once_with(
            expected_response,
            destinationId=to.user.id,
            wantAck=want_ack
        )


class CommandWSCTestCase(CommandTestCase):
    command: AbstractCommandWithSubcommands

    def assert_show_help_for_command(self, packet: MeshPacket):
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

            want = f"!{self.command.base_command} {sub_command} "
            self.assertIn(want, response)

    def test_show_help(self):
        if self.__class__.__name__ == 'CommandWSCTestCase':
            return
        base_cmd = self.command.base_command
        packet = build_test_text_packet(f'!{base_cmd} help', self.test_nodes[1].user.id, self.bot.my_id)
        self.assert_show_help_for_command(packet)
