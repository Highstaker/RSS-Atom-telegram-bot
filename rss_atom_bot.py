#!/usr/bin/python3 -u
# -*- coding: utf-8 -*-

VERSION_NUMBER = (0,1,0)

import telegramHigh

#################
##PARAMETERS#####
#################

#################
#####CLASSES#####
#################


class BotRoutine(object):
	"""docstring for BotRoutine"""
	def __init__(self):
		super(BotRoutine, self).__init__()

		self.t=telegramHigh.telegramHigh()

	def start(self):
		while True:
			self.t.echo(self.processingFunction)

	def processingFunction(self,update):
		t=self.t
		Message = update.message
		chat_id = Message.chat_id
		from_user = Message.from_user
		message = Message.text

		t.sendMessage(chat_id=chat_id,
			message=message*1000
			)


def main():
	bot = BotRoutine()

	bot.start()

if __name__ == '__main__':
	main()