from meshtastic.protobuf.mesh_pb2 import MeshPacket

from src.bot import MeshtasticBot
from src.commands.command import AbstractCommandWithSubcommands


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

            known_requests = self.bot.command_logger.command_stats.get(req_user.user.id)
            unknown_requests = self.bot.command_logger.unknown_command_stats.get(req_user.user.id)

            known_count = sum(known_requests.values()) if known_requests else 0
            unknown_count = sum(unknown_requests.values()) if unknown_requests else 0
            unknown_string = f" and {unknown_count} unknown" if unknown_count > 0 else ""

            response = f"{req_user.user.long_name} made {known_count} requests{unknown_string}\n"
            for command, count in known_requests.items():
                response += f"- {command}: {count}\n"

            if unknown_count > 0:
                for command, count in unknown_requests.items():
                    response += f"- {command}: {count}\n"

            return self.reply(packet, response)

        # otherwise, respond to '!admin users' with a list of all users
        user_ids_valid = self.bot.command_logger.command_stats.keys()
        user_ids_invalid = self.bot.command_logger.unknown_command_stats.keys()
        user_ids = set(user_ids_valid).union(user_ids_invalid)

        response = f"Users: {len(user_ids)}\n"
        for user_id in user_ids:
            node = self.bot.nodes.get_by_id(user_id)
            user_name = node.user.short_name if node else f"Unknown user {user_id}"

            known_requests = self.bot.command_logger.command_stats.get(user_id)
            unknown_requests = self.bot.command_logger.unknown_command_stats.get(user_id)

            # known_requests is a dict of command -> count
            known_request_count = sum(known_requests.values()) if known_requests else 0
            unknown_request_count = sum(unknown_requests.values()) if unknown_requests else 0
            total_requests = known_request_count + unknown_request_count

            response += f"- {user_name}: {total_requests} requests\n"

        return self.reply(packet, response)

    def show_help(self, packet: MeshPacket, args: list[str]) -> None:
        help_text = "!admin: admin commands\n"
        help_text += "!admin reset packets: reset the packet counter\n"
        help_text += "!admin users (user): usage info or user history\n"
        self.reply(packet, help_text)

    def get_command_for_logging(self, message: str) -> (str, list[str] | None, str | None):
        return self._gcfl_base_onesub_args(message)
