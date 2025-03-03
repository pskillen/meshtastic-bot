import logging
import time
from typing import Optional, Callable

from meshtastic.tcp_interface import TCPInterface


class AutoReconnectTcpInterface(TCPInterface):
    def __init__(self, *args, error_handler: Optional[Callable[[Exception], None]] = None, **kwargs):
        super().__init__(*args, **kwargs)
        self.error_handler = error_handler

    def sendHeartbeat(self):
        try:
            super().sendHeartbeat()
        except (OSError, BrokenPipeError) as e:
            logging.error(f"Heartbeat failed: {e}")
            self.reconnect()

    def reconnect(self):
        logging.info("Attempting to reconnect...")
        try:
            self.close()
        except Exception as e:
            logging.warning(
                f"Failed to close connection. "
                f"This might not be an issue since we've already disconnected: {e}")

        try:
            self.connect()
            logging.info("Reconnected successfully")
        except Exception as e:
            logging.error(f"Reconnection attempt failed: {e}")
            if self.error_handler:
                self.error_handler(e)
