import importlib


class CommandFactory:
    commands = {
        "!ping": "src.commands.ping.PingCommand",
        "!hello": "src.commands.hello.HelloCommand",
        "!help": "src.commands.help.HelpCommand",
    }

    @staticmethod
    def create_command(command_name, bot):

        command_path = CommandFactory.commands.get(command_name)
        if command_path:
            module_name, class_name = command_path.rsplit('.', 1)
            module = importlib.import_module(module_name)
            command_class = getattr(module, class_name)
            return command_class(bot)
        return None
