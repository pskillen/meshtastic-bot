import inspect
from abc import ABC, abstractmethod

from meshtastic.protobuf.mesh_pb2 import MeshPacket
from typing_extensions import deprecated

from src.base_feature import AbstractBaseFeature
from src.bot import MeshtasticBot


class AbstractCommand(AbstractBaseFeature, ABC):
    base_command: str

    def __init__(self, bot: MeshtasticBot, base_command: str):
        super().__init__(bot)
        self.base_command = base_command

    @abstractmethod
    def handle_packet(self, packet: MeshPacket) -> None:
        pass

    @deprecated("use reply_in_dm instead")
    def reply(self, packet: MeshPacket, message: str, want_ack=False) -> None:
        """
        Reply to a message in the same channel
        This is a deprecated method, use reply_in_channel instead
        """
        self.reply_in_dm(packet, message, want_ack)

    @deprecated("use message_in_dm instead")
    def reply_to(self, destination_id: str, message: str, want_ack=False) -> None:
        """
        Reply in a direct message to a user
        This is a deprecated method, use reply_in_dm instead
        """
        self.message_in_dm(destination_id, message, want_ack)

    @abstractmethod
    def get_command_for_logging(self, message: str) -> (str, list[str] | None, str | None):
        """
        Extract the command, subcommands and arguments from a message
        :param message:
        :return: Tuple of command name, subcommands, and any arguments
        """
        pass

    def _gcfl_just_base_command(self, _: str) -> (str, list[str] | None, str | None):
        cmd = self.base_command
        return cmd, None, None

    def _gcfl_base_command_and_args(self, message: str) -> (str, list[str] | None, str | None):
        cmd = self.base_command
        if len(message) > len(self.base_command) + 1:
            args = message[len(self.base_command) + 1:].strip()
        else:
            args = None

        return cmd, None, args

    def _gcfl_base_onesub_args(self, message: str) -> (str, list[str] | None, str | None):
        tokens = message.split()
        cmd = self.base_command
        subcommand = [tokens[1]] if len(tokens) > 1 else None
        args = ' '.join(tokens[2:]) if len(tokens) > 2 else None
        return cmd, subcommand, args


class AbstractCommandWithSubcommands(AbstractCommand, ABC):
    sub_commands: dict[str, callable]

    def __init__(self, bot: MeshtasticBot,
                 base_command_str: str,
                 error_on_invalid_subcommand=True):
        super().__init__(bot, base_command_str)
        self.sub_commands = {
            '': self.handle_base_command,
            'help': self.show_help,
        }
        self.error_on_invalid_subcommand = error_on_invalid_subcommand

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
            # Check the number of positional arguments the sub_command takes
            num_args = len(inspect.signature(sub_command).parameters)

            if num_args == 2:
                sub_command(packet, args)
            elif num_args == 3:
                sub_command(packet, args, sub_command_name)
            else:
                raise ValueError(f"Subcommand '{sub_command_name}' has an unexpected number of arguments")
        else:
            if self.error_on_invalid_subcommand:
                response = f"Unknown command '{sub_command_name}'"
                self.reply(packet, response)
            else:
                return self.show_help(packet, args)

    @abstractmethod
    def handle_base_command(self, packet: MeshPacket, args: list[str]) -> None:
        pass

    @abstractmethod
    def show_help(self, packet: MeshPacket, args: list[str]) -> None:
        pass
