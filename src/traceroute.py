"""
Traceroute command handling: send traceroute requests and upload TRACEROUTE_APP responses.
"""

import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.bot import MeshtasticBot

logger = logging.getLogger(__name__)


def on_traceroute_command(bot: "MeshtasticBot", target_node_id: int, hop_limit: int = 5, channel_index: int = 0):
    """
    Send a traceroute request to the target node.

    Args:
        bot: The MeshtasticBot instance
        target_node_id: Target node ID (integer, e.g. 1623194643)
        hop_limit: Maximum hops for the traceroute (default 5)
        channel_index: Channel index (default 0)
    """
    if not bot.interface or not bot.init_complete:
        logger.warning("Traceroute: bot not connected, skipping")
        return

    try:
        bot.interface.sendTraceRoute(target_node_id, hop_limit, channelIndex=channel_index)
        logger.info(f"Traceroute: sent to target={target_node_id}")
    except Exception as e:
        logger.error(f"Traceroute: failed to send to {target_node_id}: {e}")


def setup_traceroute_handler(bot: "MeshtasticBot"):
    """
    Subscribe to TRACEROUTE_APP packets and upload them to storage APIs.

    Call this once when the bot is initialized. TRACEROUTE_APP packets
    received via meshtastic.receive are already passed to storage_apis in
    bot.on_receive, so no extra subscription is needed for upload.

    This function exists for any traceroute-specific setup (e.g. filtering
    or logging). The main packet flow is: receive -> on_receive -> storage_apis.
    """
    # TRACEROUTE_APP packets are handled by bot.on_receive which forwards
    # all packets to storage_apis. No additional subscription needed.
    # We could add a dedicated handler here if we needed traceroute-specific
    # logic (e.g. only upload TR packets, or different handling).
    pass
