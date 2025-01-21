from abc import ABC, abstractmethod

from meshtastic.protobuf.mesh_pb2 import MeshPacket


class AbstractCommand(ABC):

    @abstractmethod
    def handle_packet(self, packet: MeshPacket):
        pass

    def get_command_for_logging(self, message: str) -> str:
        words = message.split()
        if len(words) < 2:
            return message
        return f"{words[0]} {words[1]}"
