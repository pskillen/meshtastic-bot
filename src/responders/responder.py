from abc import ABC, abstractmethod

from meshtastic.protobuf.mesh_pb2 import MeshPacket

from src.base_feature import AbstractBaseFeature


class AbstractResponder(AbstractBaseFeature, ABC):

    @abstractmethod
    def handle_packet(self, packet: MeshPacket) -> bool:
        """
        Handle a packet received from the mesh network
        :param packet:
        :return: True if the packet was handled, False otherwise
        """
        pass
