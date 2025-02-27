import logging
import time

from meshtastic.tcp_interface import TCPInterface


class AutoReconnectTcpInterface(TCPInterface):
    def sendHeartbeat(self):
        try:
            super().sendHeartbeat()
        except (OSError, BrokenPipeError) as e:
            logging.error(f"Heartbeat failed: {e}")
            self.reconnect()

    def reconnect(self):
        logging.info("Attempting to reconnect...")
        backoff_time = 5  # Initial back-off time in seconds
        max_backoff_time = 300  # Maximum back-off time in seconds (5 minutes)

        while True:
            try:
                self.close()
                self.connect()
                logging.info("Reconnected successfully")
                break
            except Exception as e:
                logging.error(f"Reconnection attempt failed: {e}")
                backoff_time = min(backoff_time * 1.5, max_backoff_time)  # Exponential back-off
                logging.info(f"Next reconnection attempt in {backoff_time} seconds")
                time.sleep(backoff_time)
