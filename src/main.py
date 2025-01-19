import time

from src.bot import MeshtasticBot

# Replace with the IP address of your Meshtastic node
MESHTASTIC_IP = "192.168.178.47"


def main():
    # Connect to the Meshtastic node over WiFi
    bot = MeshtasticBot(MESHTASTIC_IP)

    try:
        bot.connect()
        bot.start_scheduler()
        bot.disconnect()

    except Exception as e:
        print(f"Error: {e}")
    finally:
        if 'interface' in locals():
            interface.close()


if __name__ == "__main__":
    main()
