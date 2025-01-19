import unittest
from unittest.mock import MagicMock, patch

from src.bot import MeshtasticBot


class TestMeshtasticBot(unittest.TestCase):
    def setUp(self):
        self.bot = MeshtasticBot(address="localhost")
        self.bot.interface = MagicMock()

    def test_parse_mesh_node(self):
        raw_data = {
            'num': 1129933592,
            'user': {
                'id': '!43596b18',
                'longName': 'PDY base (unattended)',
                'shortName': 'PDYb',
                'macaddr': 'SMpDWWsY',
                'hwModel': 'HELTEC_V3',
                'publicKey': 'JWs3gfXaE1XvUm9Z2MNiC1gcGvkiFLT1/69CDCtqsxQ='
            },
            'position': {
                'latitudeI': 558243766,
                'longitudeI': -41218138,
                'altitude': 41,
                'time': 1737237050,
                'locationSource': 'LOC_EXTERNAL',
                'latitude': 55.8243766,
                'longitude': -4.1218138
            },
            'lastHeard': 1737237050,
            'deviceMetrics': {
                'batteryLevel': 101,
                'voltage': 4.302,
                'channelUtilization': 2.915,
                'airUtilTx': 0.6213055,
                'uptimeSeconds': 372627
            },
            'isFavorite': True
        }

        mesh_node = self.bot.parse_mesh_node(raw_data)

        self.assertEqual(mesh_node.num, 1129933592)
        self.assertEqual(mesh_node.user.id, '!43596b18')
        self.assertEqual(mesh_node.user.long_name, 'PDY base (unattended)')
        self.assertEqual(mesh_node.position.latitude, 55.8243766)
        self.assertEqual(mesh_node.device_metrics.battery_level, 101)
        self.assertTrue(mesh_node.is_favorite)

    @patch('src.bot.pub')
    def test_connect(self, mock_pub):
        self.bot.connect()
        self.bot.interface.connect.assert_called_once()
        mock_pub.subscribe.assert_any_call(self.bot.on_receive_text, "meshtastic.receive.text")
        mock_pub.subscribe.assert_any_call(self.bot.on_receive_user, "meshtastic.receive.user")
        mock_pub.subscribe.assert_any_call(self.bot.on_node_updated, "meshtastic.node.updated")
        mock_pub.subscribe.assert_any_call(self.bot.on_connection, "meshtastic.connection.established")

    def test_disconnect(self):
        self.bot.disconnect()
        self.bot.interface.close.assert_called_once()


if __name__ == '__main__':
    unittest.main()
