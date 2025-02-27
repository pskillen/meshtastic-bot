import logging
import os
import sys

from dotenv import load_dotenv

from src.bot import MeshtasticBot
from src.persistence.state import FileBasedStatePersistence
from src.persistence.user_prefs import SqliteUserPrefsPersistence

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
    state_persistence = FileBasedStatePersistence('all_state.json')

    # Connect to the Meshtastic node over WiFi
    bot = MeshtasticBot(MESHTASTIC_IP)
    bot.admin_nodes = ADMIN_NODES
    bot.user_prefs_persistence = SqliteUserPrefsPersistence('user_prefs.db')

    try:
        state_persistence.load_state(bot)
        bot.connect()
        bot.start_scheduler()

    except Exception as e:
        logging.error(f"Error: {e}")
    finally:
        bot.disconnect()
        state_persistence.persist_state(bot)


if __name__ == "__main__":
    main()
