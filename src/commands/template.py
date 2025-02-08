from jinja2 import Template
from meshtastic.protobuf.mesh_pb2 import MeshPacket

from src.bot import MeshtasticBot
from src.commands.command import AbstractCommand


class TemplateCommand(AbstractCommand):
    template: str

    def __init__(self, bot: MeshtasticBot, base_command: str, template: str):
        super().__init__(bot, base_command)
        self.template = template

    def handle_packet(self, packet: MeshPacket) -> None:
        message = packet['decoded']['text']
        sender_id = packet['fromId']
        hops_away = packet['hopStart'] - packet['hopLimit']

        if not message.startswith(f"!{self.base_command}"):
            return

        sender = self.bot.nodes.get_by_id(sender_id)

        # Render the template with the context variables
        template = Template(self.template)
        local_context = {
            'rx_message': message.strip(),
            'base_command': f"!{self.base_command}",
            'args': message[len(self.base_command) + 1:].strip(),
            'sender': sender,
            'sender_id': sender_id,
            'sender_name': sender.user.long_name,
            'sender_long_name': sender.user.long_name,
            'sender_short_name': sender.user.short_name,
            'hops_away': hops_away,
        }
        global_context = self.bot.get_global_context()
        context = {**local_context, **global_context}
        rendered_message = template.render(context)

        self.reply_to(sender_id, rendered_message)


class WhoAmI(TemplateCommand):
    def __init__(self, bot: MeshtasticBot):
        template = "Hi {{ sender_id }}. You are {{ sender_long_name }} [{{ sender_short_name }}]."
        template += " You are {{ hops_away }} hops away from me."
        super().__init__(bot, "whoami", template)
