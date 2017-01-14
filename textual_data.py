import sys
from os import path

if getattr(sys, 'frozen', False):
	# frozen
	SCRIPT_FOLDER = path.dirname(sys.executable)
else:
	SCRIPT_FOLDER = path.dirname(path.realpath(__file__))

# A filename of a file containing Telegram bot token.
BOT_TOKEN_FILENAME = 'tokens/BOT_TOKEN'
with open(path.join(SCRIPT_FOLDER, BOT_TOKEN_FILENAME), 'r') as f:
	BOT_TOKEN = f.read().replace("\n", "")

USERS_DB_FILENAME = "users"
DATABASES_FOLDER_NAME = "databases"

URLS_FILENAME = "urls.txt"

START_MESSAGE = "Welcome! Type /help to get help."

HELP_MESSAGE = "Help coming soon..."

ABOUT_MESSAGE = """*RSS Bot*
_Created by:_ Highstaker a.k.a. OmniSable.
Get in touch with me on Telegram if you have questions, suggestions or bug reports (@Highstaker).
Source code can be found [here](https://github.com/Highstaker/telegram-bot).
Version: {0}
[My channel, where I post development notes and update news](https://telegram.me/highstakerdev).

This bot uses the [python-telegram-bot](https://github.com/leandrotoledo/python-telegram-bot) library.
"""

UNKNOWN_COMMAND_MESSAGE = "Unknown command"

SUBSCRIBED_MESSAGE = "You have subscribed!"
UNSUBSCRIBED_MESSAGE = "You have unsubscribed!"