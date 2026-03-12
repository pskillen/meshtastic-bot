import logging
from meshtastic.protobuf.mesh_pb2 import MeshPacket

from src.commands.command import AbstractCommand


class TracerouteCommand(AbstractCommand):
    def __init__(self, bot):
        super().__init__(bot, 'tr')

    def handle_packet(self, packet: MeshPacket) -> None:
        hop_start = packet.get('hopStart', 0)
        hop_limit = packet.get('hopLimit', 0)
        hops_away = hop_start - hop_limit
        
        snr = packet.get('rxSnr', 0.0)
        
        sender_id = packet['fromId']
        sender = self.bot.node_db.get_by_id(sender_id)
        sender_name = sender.long_name if sender else sender_id

        if hops_away == 0:
            response = f"{sender_name} you are Zero Hops from me. No traceroute required!"
            self.reply_in_dm(packet, response)
            return

        response = f"{sender_name} you are {hops_away} hops away (Signal: {snr} dB). Starting full traceroute..."
        self.reply_in_dm(packet, response)
        
        # Initiate actual traceroute
        self.bot.pending_traces[sender_id] = sender_id
        try:
            logging.info(f"Initiating traceroute to {sender_id}")
            # hopLimit=7 is standard max
            self.bot.interface.sendTraceRoute(sender_id, hopLimit=7)
        except Exception as e:
            logging.error(f"Failed to send traceroute to {sender_id}: {e}")
            self.reply_in_dm(packet, f"Error starting traceroute: {e}")

    def get_command_for_logging(self, message: str) -> (str, list[str] | None, str | None):
        return self._gcfl_just_base_command(message)
