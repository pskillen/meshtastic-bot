import importlib


class CommandFactory:
    commands = {
        "!ping": {
            "class": "src.commands.ping.PingCommand",
            "args": []
        },
        "!hello": {
            "class": "src.commands.hello.HelloCommand",
            "args": []
        },
        "!help": {
            "class": "src.commands.help.HelpCommand",
            "args": []
        },
        "!nodes": {
            "class": "src.commands.nodes.NodesCommand",
            "args": []
        },
        "!whoami": {
            "class": "src.commands.template.WhoAmI",
            "args": []
        },
        "!admin": {
            "class": "src.commands.admin.AdminCommand",
            "args": []
        },
    }

    @staticmethod
    def create_command(command_name, bot):
        command_info = CommandFactory.commands.get(command_name)
        if command_info:
            module_name, class_name = command_info["class"].rsplit('.', 1)
            module = importlib.import_module(module_name)
            command_class = getattr(module, class_name)
            args = [bot] + command_info["args"]
            return command_class(*args)
        return None
