class UserCommandLogger:
    command_stats: dict[str, dict[str, int]]
    unknown_command_stats: dict[str, dict[str, int]]

    def __init__(self):
        self.command_stats = {}
        self.unknown_command_stats = {}

    def log_command(self, sender: str, command_text: str):
        if sender in self.command_stats:
            sender_stats = self.command_stats[sender]
        else:
            sender_stats = {}
            self.command_stats[sender] = sender_stats

        if command_text in sender_stats:
            sender_stats[command_text] += 1
        else:
            sender_stats[command_text] = 1

    def log_unknown_request(self, sender: str, message: str):
        words = message.split()

        if sender in self.unknown_command_stats:
            sender_stats = self.unknown_command_stats[sender]
        else:
            sender_stats = {}
            self.unknown_command_stats[sender] = sender_stats

        command_name = words[0]

        if command_name in sender_stats:
            sender_stats[command_name] += 1
        else:
            sender_stats[command_name] = 1

    def to_dict(self):
        return {
            'command_stats': self.command_stats,
            'unknown_command_stats': self.unknown_command_stats
        }

    def from_dict(self, data: dict):
        self.command_stats = data.get('command_stats', {})
        self.unknown_command_stats = data.get('unknown_command_stats', {})
