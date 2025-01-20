import logging

from jinja2 import Template
from meshtastic.protobuf.mesh_pb2 import MeshPacket

from src.bot import MeshtasticBot
from src.commands.command import AbstractCommand


class TemplateCommand(AbstractCommand):
    bot: MeshtasticBot
    keyword: str
    template: str

    def __init__(self, bot: MeshtasticBot, keyword: str, template: str):
        self.bot = bot
        self.keyword = keyword
        self.template = template

    def handle_packet(self, packet: MeshPacket) -> None:
        message = packet['decoded']['text']
        sender_id = packet['fromId']
        hops_away = packet['hopStart'] - packet['hopLimit']

        if not message.startswith(f"!{self.keyword}"):
            return

        # Render the template with the context variables
        template = Template(self.template)
        local_context = {
            'rx_message': message.strip(),
            'keyword': f"!{self.keyword}",
            'args': message[len(self.keyword) + 1:].strip(),
            'sender': self.bot.nodes[sender_id],
            'sender_id': sender_id,
            'sender_name': self.bot.nodes[sender_id].user.long_name,
            'sender_long_name': self.bot.nodes[sender_id].user.long_name,
            'sender_short_name': self.bot.nodes[sender_id].user.short_name,
            'hops_away': hops_away,
        }
        global_context = self.bot.get_global_context()
        context = {**local_context, **global_context}
        rendered_message = template.render(context)

        logging.debug(f"Sending response: '{rendered_message}'")

        self.bot.interface.sendText(rendered_message, destinationId=sender_id)
