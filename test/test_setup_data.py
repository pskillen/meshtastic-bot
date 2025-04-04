import random
from datetime import datetime, timedelta, timezone
from unittest.mock import Mock

from meshtastic.protobuf.mesh_pb2 import MeshPacket

from src.data_classes import MeshNode
from src.persistence.node_db import InMemoryNodeDB
from src.persistence.node_info import InMemoryNodeInfoStore


def meshtastic_id_to_hex(meshtastic_id: int) -> str:
    """
    Convert a Meshtastic ID (integer form) to hex representation (!abcdef12)
    """
    return f"!{meshtastic_id:08x}"


def meshtastic_hex_to_int(node_id: str) -> int:
    """
    Convert a Meshtastic ID (hex representation) to integer form
    """
    return int(node_id[1:], 16)


def generate_random_snr():
    return random.uniform(-20, 20)


def generate_random_rssi():
    return random.uniform(-100, 0)


def generate_random_packet_id():
    return random.randint(0, 2 ** 32 - 1)  # 32-bit unsigned int


_packet_types = [
    'TEXT_MESSAGE_APP',
    'POSITION_APP',
    'TRACKER_APP',
    'PRIVATE_APP',
    'BROADCAST_APP',
]


def generate_random_packet_type() -> str:
    return random.choice(_packet_types)


def random_node_id():
    return random.randint(0, 2 ** 32 - 1)  # 32-bit unsigned int


def random_node_id_hex():
    return meshtastic_id_to_hex(random_node_id())


def make_node():
    node = MeshNode()
    node.user = MeshNode.User()
    node.user.id = random_node_id_hex()
    node.user.short_name = node.user.id[-4:]
    node.user.long_name = 'Node ' + node.user.id
    return node


def get_test_bot(node_count=2, admin_node_count=1):
    """
    Create a test bot with mocked nodes data
    :return: the bot, a list of non-admin nodes, and a list of admin nodes
    """
    from src.bot import MeshtasticBot

    # Mocking nodes data
    nodes: list[MeshNode] = [make_node() for _ in range(node_count)]
    admin_nodes: list[MeshNode] = [make_node() for _ in range(admin_node_count)]
    all_nodes = nodes + admin_nodes

    bot = MeshtasticBot(address="localhost")
    bot.admin_nodes = [node.user.id for node in admin_nodes]

    # In-memory concrete implementations of various subcomponents
    bot.node_db = InMemoryNodeDB()
    bot.node_info = InMemoryNodeInfoStore()

    # Mocking various subcomponents
    bot.interface = Mock()
    bot.command_logger = Mock()
    bot.user_prefs_persistence = Mock()

    # nodes[0] is always my_id
    bot.my_id = nodes[0].user.id

    for node in all_nodes:
        last_heard_mins_ago = random.randint(0, 180)
        last_heard = datetime.now(timezone.utc) - timedelta(minutes=last_heard_mins_ago)

        # NodeDB
        bot.node_db.store_node(node)

        # NodeInfo - packets
        for _ in range(random.randint(1, 10)):
            bot.node_info.node_packet_received(node.user.id, generate_random_packet_type())

        # Finally, pick a last_heard time
        bot.node_info.update_last_heard(node.user.id, last_heard)

    return bot, nodes, admin_nodes


def build_test_text_packet(msg: str,
                           sender_id: str = random_node_id_hex(), to_id: str = random_node_id_hex(),
                           max_hops=6, hops_left=3,
                           channel: int = None) -> MeshPacket:
    # NB: lifted from a real Meshtastic packet - can be considered a "golden" packet
    packet = {
        "from": meshtastic_hex_to_int(sender_id),
        "to": meshtastic_hex_to_int(to_id),
        "decoded": {
            "bitfield": 0,
            "payload": msg,
            "portnum": "TEXT_MESSAGE_APP",
            "text": msg
        },
        "id": generate_random_packet_id(),
        'rxTime': int(datetime.now(timezone.utc).timestamp()),
        "rxSnr": generate_random_snr(),
        "hopLimit": hops_left,
        "wantAck": True,
        "rxRssi": generate_random_rssi(),
        "hopStart": max_hops,
        "publicKey": "2PiOufrKoX2r8eSusfWfqvHtxESbwlhMVyKSwZq+2UU=",
        "pkiEncrypted": True,
        "fromId": sender_id,
        "toId": to_id,
    }
    if channel:
        packet['channel'] = channel

    return packet
