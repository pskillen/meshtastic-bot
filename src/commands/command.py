import logging
from abc import ABC, abstractmethod

from meshtastic.protobuf.mesh_pb2 import MeshPacket

from src.bot import MeshtasticBot


class AbstractCommand(ABC):
    bot: MeshtasticBot
    base_command: str

    def __init__(self, bot: MeshtasticBot, base_command: str):
        self.bot = bot
        self.base_command = base_command

    @abstractmethod
    def handle_packet(self, packet: MeshPacket) -> None:
        pass

    def reply(self, packet: MeshPacket, message: str) -> None:
        destination_id = packet['fromId']
        self.reply_to(destination_id, message)

    def reply_to(self, destination_id: str, message: str) -> None:
        logging.debug(f"Sending response: '{message}'")
        self.bot.interface.sendText(message, destinationId=destination_id)

    def get_command_for_logging(self, message: str) -> str:
        words = message.split()
        if len(words) < 2:
            return message
        return f"{words[0]} {words[1]}"


class AbstractCommandWithSubcommands(AbstractCommand, ABC):
    sub_commands: dict[str, callable]

    def __init__(self, bot: MeshtasticBot, base_command_str):
        super().__init__(bot, base_command_str)
        self.sub_commands = {
            '': self.handle_base_command,
            'help': self.show_help,
        }

    def handle_packet(self, packet: MeshPacket) -> None:
        message = packet['decoded']['text']

        words = message.split()
        if len(words) < 2:
            sub_command_name = ''
            args = None
        else:
            sub_command_name = words[1].lstrip('!')
            args = words[2:] if len(words) > 2 else []

        sub_command = self.sub_commands.get(sub_command_name)
        if sub_command:
            sub_command(packet, args)
        else:
            response = f"Unknown command '{sub_command_name}'"
            self.reply(packet, response)

    @abstractmethod
    def handle_base_command(self, packet: MeshPacket, args: list[str]) -> None:
        pass

    @abstractmethod
    def show_help(self, packet: MeshPacket, args: list[str]) -> None:
        pass
