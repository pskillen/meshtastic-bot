# Meshtastic Bot

Meshtastic Bot is a Python-based bot designed to interact with Meshtastic devices. It listens for messages, processes
commands, and responds with appropriate actions.

## Features

- Handles commands via private messages
- Supports responders on public channels
- Stores various statistics about the network

## Installation (BOT)

1. Clone the repository:
    ```sh
    git clone https://github.com/yourusername/meshtastic-bot.git
    cd meshtastic-bot/bot
    ```

2. Install the required Python packages:
    ```sh
    pip install -r requirements.txt
    ```

3. If installing on a Raspberry Pi you may need to install the following packages:
    ```sh
    sudo apt-get install libopenblas-dev
    ```

## Usage

1. Copy .env.example to .env and fill in the required values.

2. Run the bot:
    ```sh
    python -m src.main
    ```

## Commands

Commands are instructions which a user can send to the bot. The bot will parse the message and execute the appropriate
command handler.

### Supported Commands

| Command   | Handler        | Description                                    |
|-----------|----------------|------------------------------------------------|
| `!help`   | `HelpCommand`  | Displays a list of available commands          |
| `!hello`  | `HelloCommand` | Displays information about the bot             |
| `!ping`   | `PingCommand`  | Responds with "Pong!"                          |
| `!nodes`  | `NodesCommand` | Displays a list of connected nodes, stats, etc |     
| `!whoami` | `WhoAmI`       | Displays information about the sender          |

### Adding Commands

Commands are configured via the [CommandFactory](src/commands/command_factory.py) class.
The [TemplateCommand](src/commands/template_command.py) class provides a template for creating new commands.

Example:

```python
# src/commands/factory.py

class CommandFactory:
   commands = {
      "!hi": {
         "class": "src.commands.template.CustomCommand",
         "args": []
      },
      
      # ... other commands ...
   }
```


```python
# src/commands/custom_command.py

from src.commands.template import TemplateCommand

class CustomCommand(TemplateCommand):
   def __init__(self, bot: MeshtasticBot):
      template = "Hi {{ sender_id }}"
      super().__init__(bot, "hi", template)
```


## Responders

The bot uses responders to handle messages on public channels.

### Adding Responders

You can add custom responders by creating new classes
that inherit from `AbstractResponder` and implementing the required methods.

Example:

```python
from src.responders.responder import AbstractResponder


class CustomResponder(AbstractResponder):
   def handle_packet(self, packet):
      # Custom handling logic
      pass
```

## Contributing

Contributions are welcome! Please fork the repository and submit a pull request.

## License

This project is licensed under the MIT License.
