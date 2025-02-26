import unittest
from abc import ABC
from unittest.mock import Mock

from src.bot import MeshtasticBot
from src.data_classes import MeshNode
from src.responders.responder import AbstractResponder
from test.test_setup_data import get_test_bot


class ResponderTestCase(unittest.TestCase, ABC):
    responder: AbstractResponder

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
