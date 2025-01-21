import abc
import json
import logging
from abc import ABC
from typing import List

from src.data_classes import MeshNode


class AbstractNodeInfoPersistence(ABC):
    @abc.abstractmethod
    def persist_node_info(self, nodes: List[MeshNode]):
        pass

    @abc.abstractmethod
    def load_node_info(self) -> List[MeshNode] | None:
        pass


class FileBasedNodeInfoPersistence(AbstractNodeInfoPersistence):
    file_path: str

    def __init__(self, file_path: str):
        self.file_path = file_path

    def persist_node_info(self, nodes: List[MeshNode]):
        try:
            node_objects = [node.to_dict() for node in nodes]
            with open(self.file_path, 'w') as f:
                json.dump(node_objects, f)
            logging.info(f"Successfully persisted {len(nodes)} nodes to {self.file_path}")
        except Exception:
            logging.error(f"Failed to persist node info", exc_info=True)

    def load_node_info(self) -> List[MeshNode] | None:
        try:
            with open(self.file_path, 'r') as f:
                node_list = json.load(f)
            nodes = [MeshNode.from_dict(node) for node in node_list]
            logging.info(f"Successfully loaded {len(nodes)} nodes from {self.file_path}")
            return nodes
        except FileNotFoundError:
            logging.warning(f"Node info file {self.file_path} not found")
            return None
        except Exception:
            logging.error(f"Failed to load node info file {self.file_path}", exc_info=True)
            return None
