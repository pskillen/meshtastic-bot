import json
import os
import unittest

from src.data_classes import MeshNode
from src.persistence.node_info import FileBasedNodeInfoPersistence


class TestFileBasedNodeInfoPersistence(unittest.TestCase):

    def setUp(self):
        self.file_path = 'test_nodes.json'
        self.persistence = FileBasedNodeInfoPersistence(self.file_path)
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

    def tearDown(self):
        if os.path.exists(self.file_path):
            os.remove(self.file_path)

    def test_persist_node_info(self):
        self.persistence.persist_node_info([self.mesh_node])
        with open(self.file_path, 'r') as f:
            data = json.load(f)
        self.assertEqual(data, [self.node_data])

    def test_load_node_info(self):
        with open(self.file_path, 'w') as f:
            json.dump([self.node_data], f)
        nodes = self.persistence.load_node_info()
        self.assertEqual(len(nodes), 1)
        self.assertEqual(nodes[0].to_dict(), self.node_data)


if __name__ == '__main__':
    unittest.main()
