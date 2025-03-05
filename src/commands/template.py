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

        sender = self.bot.node_db.get_by_id(sender_id)

        # Render the template with the context variables
        template = Template(self.template)
        local_context = {
            'rx_message': message.strip(),
            'base_command': f"!{self.base_command}",
            'args': message[len(self.base_command) + 1:].strip(),
            'sender': sender,
            'sender_id': sender_id,
            'sender_name': sender.long_name if sender else sender_id,
            'sender_long_name': sender.long_name if sender else sender_id,
            'sender_short_name': sender.short_name if sender else sender_id,
            'hops_away': hops_away,
            'user_prefs': self.get_user_prefs(sender_id)
        }
        global_context = self.bot.get_global_context()
        context = {**local_context, **global_context}
        rendered_message = template.render(context)

        self.reply_to(sender_id, rendered_message)

    def get_user_prefs(self, sender_id: str):
        if not self.bot.user_prefs_persistence:
            return None
        return self.bot.user_prefs_persistence.get_user_prefs(sender_id)

    def get_command_for_logging(self, message: str) -> (str, list[str] | None, str | None):
        return self._gcfl_base_command_and_args(message)


class WhoAmI(TemplateCommand):
    def __init__(self, bot: MeshtasticBot):
        template = "Hi {{ sender_id }}. You are {{ sender_long_name }} [{{ sender_short_name }}]."
        template += " You are {{ hops_away }} hops away from me. Send !prefs for your user prefs."
        super().__init__(bot, "whoami", template)


class UserPrefsCommand(TemplateCommand):
    def __init__(self, bot: MeshtasticBot):
        template = ("Your user prefs are below. Change with !enroll or !leave:\n"
                    "Reply to 'testing': {{ 'yes' if user_prefs.respond_to_testing.value else 'no' }}\n")
        super().__init__(bot, "prefs", template)
