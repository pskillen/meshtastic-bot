import unittest

from meshtastic.protobuf import portnums_pb2
from meshtastic.protobuf.mesh_pb2 import MeshPacket

from src.responders.responder import AbstractResponder
from test.responders import ResponderTestCase
from test.test_setup_data import build_test_text_packet, meshtastic_hex_to_int


class ConcreteResponder(AbstractResponder):
    def handle_packet(self, packet: MeshPacket) -> None:
        destination_id = packet['fromId']
        self.reply_to(destination_id, "Handled")


class TestAbstractResponder(ResponderTestCase):
    responder: ConcreteResponder

    def setUp(self):
        super().setUp()
        self.responder = ConcreteResponder(self.bot)

    def test_reply_in_channel(self):
        with self.assertRaises(NotImplementedError):
            packet = build_test_text_packet('!test', self.test_nodes[1].user.id, self.bot.my_id, channel=1)
            self.responder.reply_in_channel(packet, "Test message")

    def test_reply_to(self):
        self.responder.reply_to("test_destination", "Test message")
        self.mock_interface.sendText.assert_called_once_with(
            "Test message",
            destinationId="test_destination",
            wantAck=False)

    def test_react_to(self):
        packet = build_test_text_packet('!test',
                                        sender_id=self.test_nodes[1].user.id,
                                        to_id=self.bot.my_id,
                                        channel=1)

        self.responder.react_to(packet, "👍")
        self.mock_interface._sendPacket.assert_called_once()
        sent_packet = self.bot.interface._sendPacket.call_args[0][0]

        self.assertEqual(sent_packet.to, meshtastic_hex_to_int(self.test_nodes[1].user.id))
        self.assertEqual(sent_packet.channel, 1)
        self.assertEqual(sent_packet.decoded.portnum, portnums_pb2.PortNum.TEXT_MESSAGE_APP)
        self.assertEqual(sent_packet.decoded.payload, b'\xf0\x9f\x91\x8d')
        self.assertEqual(sent_packet.decoded.reply_id, packet['id'])
        self.assertTrue(sent_packet.decoded.emoji)
        self.assertFalse(sent_packet.want_ack)


if __name__ == '__main__':
    unittest.main()
