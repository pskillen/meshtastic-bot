import unittest
from datetime import datetime
from unittest.mock import MagicMock, patch, mock_open

from src.bot import MeshtasticBot
from src.data_classes import NodeInfoCollection, MeshNode
from src.loggers import UserCommandLogger
from src.persistence.state import FileBasedStatePersistence


class TestFileBasedStatePersistence(unittest.TestCase):

    def setUp(self):
        self.file_path = 'test_state.json'
        self.persistence = FileBasedStatePersistence(self.file_path)
        self.bot = MagicMock(spec=MeshtasticBot)

        # Initialize UserCommandLogger with some data
        self.bot.command_logger = UserCommandLogger()
        self.bot.command_logger.log_command('user1', 'test_command')
        self.bot.command_logger.log_unknown_request('user1', 'unknown_command')

        # Initialize NodeInfoCollection with some data
        self.bot.nodes = NodeInfoCollection()
        node_data = {
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
        mesh_node = MeshNode.from_dict(node_data)
        self.bot.nodes.add_node(mesh_node)

    @patch('builtins.open', new_callable=mock_open)
    @patch('json.dump')
    def test_persist_state(self, mock_json_dump, mock_file_open):
        self.persistence.persist_state(self.bot)
        mock_file_open.assert_called_once_with(self.file_path, 'w')
        mock_json_dump.assert_called_once()

        # Extract the actual data passed to json.dump
        persisted_data = mock_json_dump.call_args[0][0]

        # Verify NodeInfoCollection data
        self.assertIn('node_data', persisted_data)
        self.assertIn('nodes', persisted_data['node_data'])
        self.assertIn('user123', persisted_data['node_data']['nodes'])
        self.assertEqual(persisted_data['node_data']['nodes']['user123']['user']['longName'], 'Test User')

        # Verify UserCommandLogger data
        self.assertIn('command_data', persisted_data)
        self.assertIn('user1', persisted_data['command_data']['command_stats'])
        self.assertEqual(persisted_data['command_data']['command_stats']['user1']['test_command'], 1)
        self.assertIn('user1', persisted_data['command_data']['unknown_command_stats'])
        self.assertEqual(persisted_data['command_data']['unknown_command_stats']['user1']['unknown_command'], 1)

    @patch('builtins.open', new_callable=mock_open, read_data='{"nodes": {}, "commands": {}}')
    @patch('json.load')
    def test_load_state(self, mock_json_load, mock_file_open):
        mock_json_load.return_value = {"node_data": {}, "command_data": {}}
        self.persistence.load_state(self.bot)
        mock_file_open.assert_called_once_with(self.file_path, 'r')
        mock_json_load.assert_called_once_with(mock_file_open())
        self.bot.nodes.from_dict.assert_called_once_with({})
        self.bot.command_logger.from_dict.assert_called_once_with({})

    @patch('builtins.open', side_effect=FileNotFoundError)
    def test_load_state_file_not_found(self, mock_file_open):
        with self.assertLogs(level='WARNING') as log:
            self.persistence.load_state(self.bot)
            self.assertIn(f"State file {self.file_path} not found", log.output[0])

    @patch('builtins.open', new_callable=mock_open)
    @patch('json.load', side_effect=Exception('Test Exception'))
    def test_load_state_exception(self, mock_json_load, mock_file_open):
        with self.assertLogs(level='ERROR') as log:
            self.persistence.load_state(self.bot)
            self.assertIn(f"Failed to load state file {self.file_path}", log.output[0])


if __name__ == '__main__':
    unittest.main()
