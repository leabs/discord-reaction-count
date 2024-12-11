# Discord Reaction Count

This repo defines a Discord bot that ranks and displays the top 25 messages with the most reactions in a server for a specified year (by default it checks the current year). The bot is written in Python and uses the discord.py library.

## Installation

1. Clone the repository
2. Change directories into the code repo and install the required packages using the following command:

```bash
pip install -r requirements.txt
```

3. Create a new Discord bot and add it to your server. You can follow the instructions [here](https://discordpy.readthedocs.io/en/stable/discord.html). You will need to do all steps including inviting the bot to your server.
4. Run the bot using the following command:

```bash
python bot.py
```

5. The bot is now running and you can use the command `!top_messages` in your server to see the top 25 messages with the most reactions.

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.
