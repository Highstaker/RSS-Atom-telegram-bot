import functools

from telegram.ext import CommandHandler, MessageHandler, Filters
from telegram.error import BadRequest

from telegram import ParseMode
from userparams import UserParams
from textual_data import *
from VERSION import VERSION_NUMBER

class UserCommandHandler(object):
	"""docstring for UserCommandHandler"""
	def __init__(self, dispatcher):
		super(UserCommandHandler, self).__init__()
		self.dispatcher = dispatcher

		self.userparams = UserParams(USERS_DB_FILENAME)

		self._addHandlers()

	def _addHandlers(self):
		self.dispatcher.add_handler(CommandHandler('start', self.command_start))
		self.dispatcher.add_handler(CommandHandler('help', self.command_help))
		self.dispatcher.add_handler(CommandHandler('about', self.command_about))
		self.dispatcher.add_handler(CommandHandler('subscribe', self.command_subscribe))
		self.dispatcher.add_handler(CommandHandler('unsubscribe', self.command_unsubscribe))

		# non-command message
		# self.dispatcher.add_handler(MessageHandler([Filters.text], self.messageMethod))

		# unknown commands
		self.dispatcher.add_handler(MessageHandler(Filters.command, self.unknown_command))

		self.dispatcher.add_error_handler(self.error_handler)

	def _command_method(func):
		"""Decorator for functions that are invoked on commands. Ensures that the user is initialized."""

		@functools.wraps(func)
		def wrapper(self, bot, update, *args, **kwargs):
			chat_id = update.message.chat_id

			# Initialize user, if not present in DB
			self.userparams.initializeUser(chat_id=chat_id)

			# filter functions that don't need ticks, or else there will be two ticks on every non-slash command
			# because it also counts messageMethod
			# if func.__name__ not in ("messageMethod"):
				# write a tick to user activity log
				# self.activity_logger.tick(chat_id)

			# noinspection PyCallingNonCallable
			func(self, bot, update, *args, **kwargs)

		return wrapper

	##########
	# COMMAND METHODS
	##########

	# noinspection PyArgumentList
	@_command_method
	def command_start(self, bot, update):
		self.sendMessage(bot, update, START_MESSAGE)

	# noinspection PyArgumentList
	@_command_method
	def command_help(self, bot, update):
		msg = HELP_MESSAGE
		self.sendMessage(bot, update, msg)

	# noinspection PyArgumentList
	@_command_method
	def command_subscribe(self, bot, update):
		self.userparams.subscribe(update.message.chat_id)
		msg = SUBSCRIBED_MESSAGE
		self.sendMessage(bot, update, msg)

	# noinspection PyArgumentList
	@_command_method
	def command_unsubscribe(self, bot, update):
		self.userparams.unsubscribe(update.message.chat_id)
		msg = UNSUBSCRIBED_MESSAGE
		self.sendMessage(bot, update, msg)

	# noinspection PyArgumentList
	@_command_method
	def command_about(self, bot, update):
		msg = ABOUT_MESSAGE.format(".".join([str(i) for i in VERSION_NUMBER]))
		self.sendMessage(bot, update, msg, disable_web_page_preview=False)

	# noinspection PyArgumentList
	@_command_method
	def unknown_command(self, bot, update):
		self.sendMessage(bot, update, UNKNOWN_COMMAND_MESSAGE)

	def error_handler(self, bot, update, error):
		print("[ERROR]", error)

	def sendMessage(self, bot, update_or_chatid, message, disable_web_page_preview=True):
		def breakLongMessage(msg, max_chars_per_message=3500):
			"""
			Breaks a message that is too long.
			:param max_chars_per_message: maximum amount of characters per message.
			The official maximum is 4096.
			Changing this is not recommended.
			:param msg: message to be split
			:return: a list of message pieces
			"""

			# let's split the message by newlines first
			message_split = msg.split("\n")

			# the result will be stored here
			broken = []

			# splitting routine
			while message_split:
				result = message_split.pop(0) + "\n"
				if len(result) > max_chars_per_message:
					# The chunk is huge. Split it not caring for newlines.
					broken += [result[i:i + max_chars_per_message].strip("\n\t\r ")
							   for i in range(0, len(result), max_chars_per_message)]
				else:
					# It's a smaller chunk, append others until their sum is bigger than maximum
					while len(result) <= max_chars_per_message:
						if not message_split:
							# if the original ran out
							break
						# check if the next chunk makes the merged chunk it too big
						if len(result) + len(message_split[0]) <= max_chars_per_message:
							# nope. append chunk
							result += message_split.pop(0) + "\n"
						else:
							# yes, it does. Stop on this.
							break
					broken += [result.strip("\n\t\r ")]

			return broken

		try:
			chat_id = update_or_chatid.message.chat_id
		except AttributeError:
			chat_id = update_or_chatid

		for m in breakLongMessage(message):
			try:
				bot.sendMessage(chat_id=chat_id, text=m,
								parse_mode=ParseMode.HTML,
								disable_web_page_preview=disable_web_page_preview,
								)
			except BadRequest:
				bot.sendMessage(chat_id=chat_id, text=m,
								disable_web_page_preview=disable_web_page_preview,
								)

