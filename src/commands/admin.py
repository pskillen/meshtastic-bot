from meshtastic.protobuf.mesh_pb2 import MeshPacket

from src.bot import MeshtasticBot
from src.commands.command import AbstractCommand


class AdminCommand(AbstractCommand):
    def __init__(self, bot: MeshtasticBot):
        self.bot = bot
        self.commands = {
            'reset': self.reset_packets,
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
                command_name = words[1]
                args = words[2:] if len(words) > 2 else []

                command = self.commands.get(command_name)
                if command:
                    response = command(args)
                else:
                    response = f"Unknown command '{command_name}'"

        print(f"Sending response: '{response}'")
        self.bot.interface.sendText(response, destinationId=sender)

    def reset_packets(self, args: list[str]):
        if args and len(args) > 0 and args[0] == 'packets':
            self.bot.reset_packets_today()
            return 'Packet counter reset'
        
        return f"reset: Unknown argument '{args[0]}'" if len(args) > 0 else "reset: Missing argument"

    def show_help(self, args: list[str]):
        help_text = "Available commands:\n"
        help_text += "reset packets - Reset the packet counter\n"
        help_text += "help - Show this help message\n"
        return help_text
