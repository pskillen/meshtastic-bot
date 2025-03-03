import logging
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

from src.bot import MeshtasticBot
from src.persistence.commands_logger import SqliteCommandLogger
from src.persistence.state import FileBasedStatePersistence
from src.persistence.user_prefs import SqliteUserPrefsPersistence

# Load environment variables from .env file
load_dotenv()

# Get the IP address and admin nodes from environment variables
MESHTASTIC_IP = os.getenv("MESHTASTIC_IP")
ADMIN_NODES = os.getenv("ADMIN_NODES").split(',')
DATA_DIR = os.getenv("DATA_DIR", "data")

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
    state_file = data_dir / 'all_state.json'
    user_prefs_file = data_dir / 'user_prefs.sqlite'
    command_log_file = data_dir / 'user_cmds.sqlite'

    # Create a state persistence object
    state_persistence = FileBasedStatePersistence(str(state_file))

    # Connect to the Meshtastic node over WiFi
    bot = MeshtasticBot(MESHTASTIC_IP)
    bot.admin_nodes = ADMIN_NODES
    bot.user_prefs_persistence = SqliteUserPrefsPersistence(str(user_prefs_file))
    bot.command_logger = SqliteCommandLogger(str(command_log_file))

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
