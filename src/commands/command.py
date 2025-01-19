from abc import ABC, abstractmethod

from meshtastic.protobuf.mesh_pb2 import MeshPacket


class AbstractCommand(ABC):

    @abstractmethod
    def handle_packet(self, packet: MeshPacket):
        pass
