import abc
import json
import logging
from abc import ABC
from datetime import datetime


class AppState:
    packet_counter_reset_time: datetime

    def __init__(self, packet_counter_reset_time: datetime,
                 command_stats: dict,
                 unknown_command_stats: dict):
        self.packet_counter_reset_time = packet_counter_reset_time
        self.command_stats = command_stats
        self.unknown_command_stats = unknown_command_stats


class AbstractStatePersistence(ABC):
    @abc.abstractmethod
    def persist_state(self, state: AppState):
        pass

    @abc.abstractmethod
    def load_state(self) -> AppState | None:
        pass


class FileBasedStatePersistence(AbstractStatePersistence):
    def __init__(self, file_path: str):
        self.file_path = file_path

    def persist_state(self, state: AppState):
        state_data = {
            'packet_counter_reset_time': state.packet_counter_reset_time.isoformat(),
            'command_stats': state.command_stats,
            'unknown_command_stats': state.unknown_command_stats,
        }
        try:
            with open(self.file_path, 'w') as f:
                json.dump(state_data, f)
        except Exception:
            logging.error(f"Failed to persist state info", exc_info=True)

    def load_state(self) -> AppState | None:
        try:
            with open(self.file_path, 'r') as file:
                state_data = json.load(file)

            packet_counter_reset_time = datetime.fromisoformat(state_data['packet_counter_reset_time']) \
                if 'packet_counter_reset_time' in state_data else datetime.now()
            command_stats = state_data['command_stats'] \
                if 'command_stats' in state_data else {}
            unknown_command_stats = state_data['unknown_command_stats'] \
                if 'unknown_command_stats' in state_data else {}

            logging.info(f"Successfully loaded state from {self.file_path}")
            return AppState(packet_counter_reset_time, command_stats, unknown_command_stats)
        except FileNotFoundError:
            logging.warning(f"State file {self.file_path} not found")
            return None
        except Exception:
            logging.error(f"Failed to load state file {self.file_path}", exc_info=True)
            return None
