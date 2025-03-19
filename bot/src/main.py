import logging
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

from src.api.StorageAPI import StorageAPIWrapper
from src.bot import MeshtasticBot
from src.persistence.commands_logger import SqliteCommandLogger
from src.persistence.node_info import InMemoryNodeInfoStore
from src.persistence.node_db import SqliteNodeDB
from src.persistence.user_prefs import SqliteUserPrefsPersistence

# Load environment variables from .env file
load_dotenv()

# Get the IP address and admin nodes from environment variables
MESHTASTIC_IP = os.getenv("MESHTASTIC_IP")
ADMIN_NODES = os.getenv("ADMIN_NODES").split(',')
DATA_DIR = os.getenv("DATA_DIR", "data")
STORAGE_API_ROOT = os.getenv("STORAGE_API_ROOT")
STORAGE_API_TOKEN = os.getenv("STORAGE_API_TOKEN", None)

# Configure logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - [%(levelname)s] %(module)s.%(funcName)s - %(message)s',
                    stream=sys.stdout)

# Set the log level for specific modules
logging.getLogger('tcp_interface').setLevel(logging.WARNING)
logging.getLogger('stream_interface').setLevel(logging.WARNING)
logging.getLogger('mesh_interface').setLevel(logging.WARNING)


def main():
    # Ensure data dir exists
    data_dir = os.path.join(Path(__file__).parent.parent, DATA_DIR)
    os.makedirs(data_dir, exist_ok=True)
    data_dir = Path(data_dir)
    user_prefs_file = data_dir / 'user_prefs.sqlite'
    command_log_file = data_dir / 'user_cmds.sqlite'
    node_db_file = data_dir / 'node_db.sqlite'
    node_info_file = data_dir / 'node_info.json'

    # Connect to the Meshtastic node over WiFi
    bot = MeshtasticBot(MESHTASTIC_IP)
    bot.admin_nodes = ADMIN_NODES
    bot.user_prefs_persistence = SqliteUserPrefsPersistence(str(user_prefs_file))
    bot.command_logger = SqliteCommandLogger(str(command_log_file))
    bot.node_db = SqliteNodeDB(str(node_db_file))
    node_info = InMemoryNodeInfoStore()
    bot.node_info = node_info
    if STORAGE_API_ROOT:
        bot.storage_api = StorageAPIWrapper(STORAGE_API_ROOT, STORAGE_API_TOKEN)

    try:
        node_info.load_from_file(str(node_info_file))
        bot.connect()
        bot.start_scheduler()

    except Exception as e:
        logging.error(f"Error: {e}")
    finally:
        bot.disconnect()
        node_info.persist_to_file(str(node_info_file))


if __name__ == "__main__":
    main()
