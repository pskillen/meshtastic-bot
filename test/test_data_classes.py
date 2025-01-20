import unittest

from src.data_classes import MeshNode


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
            'packetsToday': 10,
            'packetBreakdownToday': {'type1': 5, 'type2': 5}
        }

        self.mesh_node = MeshNode.from_dict(self.node_data)

    def test_to_dict(self):
        node_dict = self.mesh_node.to_dict()
        self.assertEqual(node_dict, self.node_data)

    def test_from_dict(self):
        node = MeshNode.from_dict(self.node_data)
        self.assertEqual(node.to_dict(), self.node_data)


if __name__ == '__main__':
    unittest.main()
