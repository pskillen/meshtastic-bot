import datetime

from meshtastic.protobuf.mesh_pb2 import MeshPacket

from src.bot import MeshtasticBot
from src.commands.command import AbstractCommandWithSubcommands
from src.data_classes import MeshNode


class AdminCommand(AbstractCommandWithSubcommands):
    def __init__(self, bot: MeshtasticBot):
        super().__init__(bot, 'admin')
        self.sub_commands['reset'] = self.reset_packets
        self.sub_commands['users'] = self.show_users

    def handle_packet(self, packet: MeshPacket) -> None:
        sender = packet['fromId']

        # Only allow admin nodes to use this command
        if sender not in self.bot.admin_nodes:
            node = self.bot.nodes.get_by_id(sender)
            response = f"Sorry {node.user.long_name}, you are not authorized to use this command"
            self.reply_to(sender, response)
        else:
            super().handle_packet(packet)

    def handle_base_command(self, packet: MeshPacket, args: list[str]) -> None:
        response = "Invalid command format - expected !admin <command> <args>"
        self.reply(packet, response)

    def reset_packets(self, packet: MeshPacket, args: list[str]) -> None:
        available_options = ['packets']

        if not args or len(args) == 0:
            response = f"reset: Missing argument - options are: {available_options}"
        elif args[0] == 'packets':
            self.bot.nodes.reset_packets_today()
            response = 'Packet counter reset'
        else:
            response = f"reset: Unknown argument '{args[0]}' - options are: {available_options}"

        self.reply(packet, response)

    def show_users(self, packet: MeshPacket, args: list[str]) -> None:
        # respond to '!admin users <user>' to show user history
        if len(args) > 0:
            req_user_name = args[0]
            req_user = self.bot.get_node_by_short_name(req_user_name)
            if not req_user:
                response = f"User '{req_user_name}' not found"
                return self.reply(packet, response)
            return self._show_user(packet, req_user)

        # otherwise, respond to '!admin users' with a list of all users
        return self._show_users(packet)

    def _show_user(self, packet: MeshPacket, req_user: MeshNode):
        # get command history for the user since midnight 7 days ago
        since = datetime.datetime.now() - datetime.timedelta(days=7)
        since = since.replace(hour=0, minute=0, second=0, microsecond=0)

        command_history = self.bot.command_logger.get_command_history(
            since=since, sender_id=req_user.user.id)
        unknown_command_history = self.bot.command_logger.get_unknown_command_history(
            since=since, sender_id=req_user.user.id)
        responder_history = self.bot.command_logger.get_responder_history(
            since=since, sender_id=req_user.user.id)

        command_counts = command_history['base_command'].value_counts().to_dict()
        responder_counts = responder_history['responder_class'].value_counts().to_dict()

        known_count = sum(command_counts.values())
        unknown_count = unknown_command_history.shape[0]
        responder_count = sum(responder_counts.values())

        response = f"{req_user.user.long_name} - {known_count} cmds, {responder_count} responders, {unknown_count} unknown cmds\n"
        response += f"Since {since.strftime('%Y-%m-%d %H:%M:%S')}"
        self.reply(packet, response)

        if known_count > 0:
            response = f"Commands:\n"
            for command, count in command_counts.items():
                response += f"- {command}: {count}\n"
            self.reply(packet, response)

        if unknown_count > 0:
            response = "Unknown Commands:\n"
            for _, row in unknown_command_history.iterrows():
                response += f"- {row['message']}\n"
            self.reply(packet, response)

        if responder_count > 0:
            response = f"Responders:\n"
            for responder, count in responder_counts.items():
                response += f"- {responder}: {count}\n"
            self.reply(packet, response)

    def _show_users(self, packet: MeshPacket):
        # get command history since midnight 7 days ago
        since = datetime.datetime.now() - datetime.timedelta(days=7)
        since = since.replace(hour=0, minute=0, second=0, microsecond=0)

        command_history = self.bot.command_logger.get_command_history(since=since)
        unknown_command_history = self.bot.command_logger.get_unknown_command_history(since=since)
        responder_history = self.bot.command_logger.get_responder_history(since=since)

        user_ids = (set(command_history['sender_id'])
                    .union(set(unknown_command_history['sender_id']))
                    .union(set(responder_history['sender_id'])))

        # sort user_ids by sum of known, unknown, and responder commands. finally, sort by user_id
        user_ids = sorted(user_ids, key=lambda user_id: (
            command_history[command_history['sender_id'] == user_id].shape[0]
            + unknown_command_history[unknown_command_history['sender_id'] == user_id].shape[0]
            + responder_history[responder_history['sender_id'] == user_id].shape[0],
            user_id
        ))

        response = f"Users: {len(user_ids)}\n"
        for user_id in user_ids:
            node = self.bot.nodes.get_by_id(user_id)
            user_name = node.user.short_name if node else f"Unknown user {user_id}"

            known_requests = command_history[command_history['sender_id'] == user_id]
            unknown_requests = unknown_command_history[unknown_command_history['sender_id'] == user_id]
            responder_requests = responder_history[responder_history['sender_id'] == user_id]

            known_request_count = known_requests.shape[0]
            unknown_request_count = unknown_requests.shape[0]
            responder_request_count = responder_requests.shape[0]
            # total_requests = known_request_count + unknown_request_count + responder_request_count

            response += f"- {user_name}: {known_request_count} cmds, {unknown_request_count} unk, {responder_request_count} resp\n"

        return self.reply(packet, response)

    def show_help(self, packet: MeshPacket, args: list[str]) -> None:
        help_text = "!admin: admin commands\n"
        help_text += "!admin reset packets: reset the packet counter\n"
        help_text += "!admin users (user): usage info or user history\n"
        self.reply(packet, help_text)

    def get_command_for_logging(self, message: str) -> (str, list[str] | None, str | None):
        return self._gcfl_base_onesub_args(message)
