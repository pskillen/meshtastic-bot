import logging

from meshtastic.protobuf.mesh_pb2 import MeshPacket

from src.bot import MeshtasticBot
from src.commands.command import AbstractCommand


class AdminCommand(AbstractCommand):
    def __init__(self, bot: MeshtasticBot):
        self.bot = bot
        self.sub_commands = {
            'reset': self.reset_packets,
            'users': self.show_users,
            'help': self.show_help
        }

    def handle_packet(self, packet: MeshPacket) -> None:
        message = packet['decoded']['text']
        sender = packet['fromId']

        if sender not in self.bot.admin_nodes:
            node = self.bot.nodes.get(sender)
            response = f"Sorry {node.user.long_name}, you are not authorized to use this command"
        else:
            words = message.split()
            if len(words) < 2:
                response = "Invalid command format - expected !admin <command> <args>"
            else:
                sub_command_name = words[1]
                args = words[2:] if len(words) > 2 else []

                sub_command = self.sub_commands.get(sub_command_name)
                if sub_command:
                    response = sub_command(args)
                else:
                    response = f"Unknown command '{sub_command_name}'"

        logging.debug(f"Sending response: '{response}'")
        self.bot.interface.sendText(response, destinationId=sender)

    def reset_packets(self, args: list[str]):
        if args and len(args) > 0 and args[0] == 'packets':
            self.bot.reset_packets_today()
            return 'Packet counter reset'

        return f"reset: Unknown argument '{args[0]}'" if len(args) > 0 else "reset: Missing argument"

    def show_users(self, args: list[str]):
        user_ids_valid = self.bot.command_logger.command_stats.keys()
        user_ids_invalid = self.bot.command_logger.unknown_command_stats.keys()
        user_ids = set(user_ids_valid).union(user_ids_invalid)

        # TODO: add '!admin users <user>' to show user history
        if len(args) > 0:
            return "Not implemented yet"

        response = f"Users: {len(user_ids)}\n"
        for user_id in user_ids:
            node = self.bot.nodes.get(user_id)
            user_name = node.user.short_name if node else f"Unknown user {user_id}"

            known_requests = self.bot.command_logger.command_stats.get(user_id)
            unknown_requests = self.bot.command_logger.unknown_command_stats.get(user_id)

            # known_requests is a dict of command -> count
            known_request_count = sum(known_requests.values()) if known_requests else 0
            unknown_request_count = unknown_requests if unknown_requests else 0
            total_requests = known_request_count + unknown_request_count

            response += f"- {user_name}: {total_requests} requests\n"

        return response

    def show_help(self, args: list[str]):
        help_text = "Available commands:\n"
        help_text += "reset packets - Reset the packet counter\n"
        help_text += "users (user) - Usage info or user history\n"
        help_text += "help - Show this help message\n"
        return help_text
