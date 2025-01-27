import unittest

from meshtastic.protobuf.mesh_pb2 import MeshPacket

from src.commands.command import AbstractCommand
from src.loggers import UserCommandLogger


class MockCommand(AbstractCommand):
    def handle_packet(self, packet: MeshPacket):
        raise NotImplemented()

    def get_command_for_logging(self, message: str) -> str:
        return message.split()[0]


class TestUserCommandLogger(unittest.TestCase):

    def setUp(self):
        self.logger = UserCommandLogger()
        self.command = MockCommand()

    def test_log_command_new_sender(self):
        self.logger.log_command(self.command, 'user1', 'test_command')
        self.assertIn('user1', self.logger.command_stats)
        self.assertIn('test_command', self.logger.command_stats['user1'])
        self.assertEqual(self.logger.command_stats['user1']['test_command'], 1)

    def test_log_command_existing_sender(self):
        self.logger.log_command(self.command, 'user1', 'test_command')
        self.logger.log_command(self.command, 'user1', 'test_command')
        self.assertEqual(self.logger.command_stats['user1']['test_command'], 2)

    def test_log_unknown_request_new_sender(self):
        self.logger.log_unknown_request('user1', 'unknown_command')
        self.assertIn('user1', self.logger.unknown_command_stats)
        self.assertIn('unknown_command', self.logger.unknown_command_stats['user1'])
        self.assertEqual(self.logger.unknown_command_stats['user1']['unknown_command'], 1)

    def test_log_unknown_request_existing_sender(self):
        self.logger.log_unknown_request('user1', 'unknown_command')
        self.logger.log_unknown_request('user1', 'unknown_command')
        self.assertEqual(self.logger.unknown_command_stats['user1']['unknown_command'], 2)

    def test_to_dict(self):
        self.logger.log_command(self.command, 'user1', 'test_command')
        self.logger.log_unknown_request('user1', 'unknown_command')
        state_dict = self.logger.to_dict()
        self.assertIn('command_stats', state_dict)
        self.assertIn('unknown_command_stats', state_dict)
        self.assertEqual(state_dict['command_stats']['user1']['test_command'], 1)
        self.assertEqual(state_dict['unknown_command_stats']['user1']['unknown_command'], 1)

    def test_from_dict(self):
        state_dict = {
            'command_stats': {'user1': {'test_command': 1}},
            'unknown_command_stats': {'user1': {'unknown_command': 1}}
        }
        self.logger.from_dict(state_dict)
        self.assertIn('user1', self.logger.command_stats)
        self.assertIn('test_command', self.logger.command_stats['user1'])
        self.assertEqual(self.logger.command_stats['user1']['test_command'], 1)
        self.assertIn('user1', self.logger.unknown_command_stats)
        self.assertIn('unknown_command', self.logger.unknown_command_stats['user1'])
        self.assertEqual(self.logger.unknown_command_stats['user1']['unknown_command'], 1)


if __name__ == '__main__':
    unittest.main()
