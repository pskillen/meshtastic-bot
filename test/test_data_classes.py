import unittest
from datetime import datetime, timedelta

from src.data_classes import NodeInfoCollection, MeshNode


class TestMeshNode(unittest.TestCase):

    def setUp(self):
        self.node_data = {
            'num': 1,
            'user': {
                'id': 'user123',
                'longName': 'Test User',
                'shortName': 'TU',
                'macaddr': '00:11:22:33:44:55',
                'hwModel': 'ModelX',
                'publicKey': 'public_key_123'
            },
            'position': {
                'altitude': 100,
                'time': 1234567890,
                'locationSource': 'GPS',
                'latitude': 37.7749,
                'longitude': -122.4194
            },
            'lastHeard': 1234567890,
            'deviceMetrics': {
                'batteryLevel': 80,
                'voltage': 3.7,
                'channelUtilization': 0.5,
                'airUtilTx': 0.1,
                'uptimeSeconds': 3600
            },
            'isFavorite': True,
        }

        self.mesh_node = MeshNode.from_dict(self.node_data)

    def test_to_dict(self):
        node_dict = self.mesh_node.to_dict()
        self.assertEqual(node_dict, self.node_data)

    def test_from_dict(self):
        node = MeshNode.from_dict(self.node_data)
        self.assertEqual(node.to_dict(), self.node_data)

    def test_from_dict_2(self):
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

        mesh_node = MeshNode.from_dict(raw_data)

        self.assertEqual(mesh_node.num, 1129933592)
        self.assertEqual(mesh_node.user.id, '!43596b18')
        self.assertEqual(mesh_node.user.long_name, 'PDY base (unattended)')
        self.assertEqual(mesh_node.position.latitude, 55.8243766)
        self.assertEqual(mesh_node.device_metrics.battery_level, 101)
        self.assertTrue(mesh_node.is_favorite)


class TestNodeInfoCollection(unittest.TestCase):

    def setUp(self):
        self.collection = NodeInfoCollection()
        self.node_data = {
            'num': 1,
            'user': {
                'id': 'user123',
                'longName': 'Test User',
                'shortName': 'TU',
                'macaddr': '00:11:22:33:44:55',
                'hwModel': 'ModelX',
                'publicKey': 'public_key_123'
            },
            'position': {
                'altitude': 100,
                'time': 1234567890,
                'locationSource': 'GPS',
                'latitude': 37.7749,
                'longitude': -122.4194
            },
            'lastHeard': datetime.now().timestamp(),
            'deviceMetrics': {
                'batteryLevel': 80,
                'voltage': 3.7,
                'channelUtilization': 0.5,
                'airUtilTx': 0.1,
                'uptimeSeconds': 3600
            },
            'isFavorite': True
        }
        self.mesh_node = MeshNode.from_dict(self.node_data)
        self.collection.add_node(self.mesh_node)

    def test_add_node(self):
        self.assertIn('user123', self.collection.nodes)
        self.assertEqual(self.collection.nodes['user123'], self.mesh_node)

    def test_get_by_id(self):
        node = self.collection.get_by_id('user123')
        self.assertEqual(node, self.mesh_node)

    def test_get_by_short_name(self):
        node = self.collection.get_by_short_name('TU')
        self.assertEqual(node, self.mesh_node)

    def test_get_online_nodes(self):
        online_nodes = self.collection.get_online_nodes()
        self.assertIn('user123', online_nodes)

    def test_get_offline_nodes(self):
        self.mesh_node.last_heard = (datetime.now() - timedelta(hours=3)).timestamp()
        offline_nodes = self.collection.get_offline_nodes()
        self.assertIn('user123', offline_nodes)

    def test_increment_packets_today(self):
        self.collection.increment_packets_today('user123', 'type1')
        self.assertEqual(self.collection.node_packets_today['user123'], 1)
        self.assertEqual(self.collection.node_packets_today_breakdown['user123']['type1'], 1)

    def test_reset_packets_today(self):
        self.collection.increment_packets_today('user123', 'type1')
        self.collection.reset_packets_today()
        self.assertEqual(self.collection.node_packets_today, {})
        self.assertEqual(self.collection.node_packets_today_breakdown, {})

    def test_to_dict(self):
        state_dict = self.collection.to_dict()
        self.assertIn('nodes', state_dict)
        self.assertIn('packetCounterResetTime', state_dict)
        self.assertIn('nodePacketsToday', state_dict)
        self.assertIn('nodePacketsTodayBreakdown', state_dict)

    def test_from_dict(self):
        state_dict = self.collection.to_dict()
        new_collection = NodeInfoCollection()
        new_collection.from_dict(state_dict)
        self.assertEqual(new_collection.nodes['user123'].to_dict(), self.mesh_node.to_dict())


if __name__ == '__main__':
    unittest.main()
