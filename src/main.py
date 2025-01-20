import logging
import os
import sys

from dotenv import load_dotenv

from src.bot import MeshtasticBot
from src.persistence.node_info import FileBasedNodeInfoPersistence
from src.persistence.state import FileBasedStatePersistence

# Load environment variables from .env file
load_dotenv()

# Get the IP address and admin nodes from environment variables
MESHTASTIC_IP = os.getenv("MESHTASTIC_IP")
ADMIN_NODES = os.getenv("ADMIN_NODES").split(',')

# Configure logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - [%(levelname)s] %(module)s.%(funcName)s - %(message)s',
                    stream=sys.stdout)

# Set the log level for specific modules
logging.getLogger('tcp_interface').setLevel(logging.WARNING)
logging.getLogger('stream_interface').setLevel(logging.WARNING)
logging.getLogger('mesh_interface').setLevel(logging.WARNING)


def main():
    # Connect to the Meshtastic node over WiFi
    bot = MeshtasticBot(MESHTASTIC_IP)
    bot.admin_nodes = ADMIN_NODES
    bot.node_persistence = FileBasedNodeInfoPersistence('nodes.json')
    bot.state_persistence = FileBasedStatePersistence('state.json')

    try:
        bot.load_persisted_data()
        bot.connect()
        bot.start_scheduler()

    except Exception as e:
        logging.error(f"Error: {e}")
    finally:
        bot.disconnect()
        bot.persist_all_data()


if __name__ == "__main__":
    main()
