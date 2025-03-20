import base64
import logging
from typing import Union

import requests
from meshtastic.protobuf.mesh_pb2 import MeshPacket

from src.api.BaseAPIWrapper import BaseAPIWrapper
from src.api.serializers import MeshNodeSerializer
from src.data_classes import MeshNode


class StorageAPIWrapper(BaseAPIWrapper):

    @classmethod
    def _sanitise_raw_packet(cls, data):
        if isinstance(data, dict):
            # We never want these pesky raw fields
            if 'raw' in data:
                data.pop('raw')

            return {key: cls._sanitise_raw_packet(value) for key, value in data.items()}
        elif isinstance(data, list):
            return [cls._sanitise_raw_packet(item) for item in data]
        elif isinstance(data, bytes):
            return base64.b64encode(data).decode('utf-8')
        else:
            return data

    def store_raw_packet(self, packet: dict):
        """
        Store a raw packet in the storage API
        """
        # Convert bytes to Base64-encoded strings recursively
        raw_packet: MeshPacket = packet.get('raw')
        packet = StorageAPIWrapper._sanitise_raw_packet(packet)

        # Some fields are not present in the packet if they're a nullish value, so we need to get them from the raw packet
        if raw_packet:
            if 'channel' not in packet:
                packet['channel'] = raw_packet.channel

        logging.debug(f"Storing packet: {packet}")
        response = self._post("/api/raw-packet/", json=packet)
        logging.debug(f"Response: {response.json()}")

        return response.json()

    def list_nodes(self) -> list[MeshNode]:
        """
        Get a list of all nodes stored in the storage API. This list generally does not include position or metrics data.
        """
        response = self._get("/api/nodes/")
        response_json = response.json()

        return [MeshNodeSerializer.from_api_dict(node_data) for node_data in response_json]

    def store_node(self, node: MeshNode):
        """
        Create a or update a node in the storage API

        If the node contains position or metrics data, it will be stored as well
        """

        node_data = MeshNodeSerializer.to_api_dict(node)

        response = self._post("/api/nodes/", json=node_data)
        return response.json()

    def get_node_by_id(self, node_id: Union[int, str], include_positions=0, include_metrics=0) -> MeshNode | None:
        """
        Get a node by the int or hex representation of its ID

        @param node_id: The ID of the node to get
        @param include_positions: How many positions history items to include in the response
        @param include_metrics: How many device metrics history items to include in the response
        """
        response = self._get(f"/api/nodes/{node_id}?positions={include_positions}&metrics={include_metrics}")
        response_json = response.json()

        if response_json:
            return MeshNodeSerializer.from_api_dict(response_json)
        else:
            return None
