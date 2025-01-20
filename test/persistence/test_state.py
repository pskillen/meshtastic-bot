import unittest
from unittest.mock import mock_open, patch
from datetime import datetime
from src.persistence.state import AppState, FileBasedStatePersistence

class TestFileBasedStatePersistence(unittest.TestCase):

    def setUp(self):
        self.file_path = 'test_state.json'
        self.persistence = FileBasedStatePersistence(self.file_path)
        self.state = AppState(packet_counter_reset_time=datetime(2023, 1, 1, 12, 0, 0))

    @patch('builtins.open', new_callable=mock_open)
    @patch('json.dump')
    def test_persist_state(self, mock_json_dump, mock_file):
        self.persistence.persist_state(self.state)
        mock_file.assert_called_once_with(self.file_path, 'w')
        mock_json_dump.assert_called_once_with(
            {'packet_counter_reset_time': '2023-01-01T12:00:00'}, mock_file()
        )

    @patch('builtins.open', new_callable=mock_open, read_data='{"packet_counter_reset_time": "2023-01-01T12:00:00"}')
    def test_load_state(self, mock_file):
        state = self.persistence.load_state()
        self.assertIsNotNone(state)
        self.assertEqual(state.packet_counter_reset_time, datetime(2023, 1, 1, 12, 0, 0))

    @patch('builtins.open', side_effect=FileNotFoundError)
    def test_load_state_file_not_found(self, mock_file):
        state = self.persistence.load_state()
        self.assertIsNone(state)

    @patch('builtins.open', new_callable=mock_open)
    @patch('json.load', side_effect=Exception)
    def test_load_state_json_decode_error(self, mock_json_load, mock_file):
        state = self.persistence.load_state()
        self.assertIsNone(state)

if __name__ == '__main__':
    unittest.main()
