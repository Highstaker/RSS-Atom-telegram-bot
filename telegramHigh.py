#!/usr/bin/python3 -u
# -*- coding: utf-8 -*-

import logging
import telegram
import socket
from os import path
import sys

#if a connection is lost and getUpdates takes too long, an error is raised
socket.setdefaulttimeout(30)

logging.basicConfig(format = u'[%(asctime)s] %(filename)s[LINE:%(lineno)d]# %(levelname)-8s  %(message)s', 
	level = logging.WARNING)

#A filename of a file containing a token.
TOKEN_FILENAME = 'token'
with open(path.join(path.dirname(path.realpath(__file__)), TOKEN_FILENAME),'r') as f:
	BOT_TOKEN = f.read().replace("\n","")

############
##PARAMETERS
############

MAX_CHARS_PER_MESSAGE=2048

########
########CLASSES
########

class telegramHigh():

	LAST_UPDATE_ID = None

	"""telegramHigh"""
	def __init__(self):
		super(telegramHigh, self).__init__()
		
		self.bot = telegram.Bot(BOT_TOKEN)

	def breakLongMessage(self,msg):		
		'''
		Breaks a message that is too long.
		'''
		result_split = msg.split("\n")

		broken = []

		while result_split:
			result = ""
			while True:
				if result_split:
					result += result_split.pop(0)+"\n"
					print("result",result)
				else:
					break
				if len(result) > MAX_CHARS_PER_MESSAGE:
					break

			if result:
				n_parts = int( len(result)/MAX_CHARS_PER_MESSAGE +1 )

				for i in range(n_parts):
					broken += [result[i*len(result)//n_parts:(i+1)*len(result)//n_parts]]

		return broken

	def sendMessage(self,chat_id,message,key_markup="SAME",preview=True,markdown=True):
		logging.warning("Replying to " + str(chat_id) + ": " + message)
		fulltext = self.breakLongMessage(message)
		# print("fulltext",fulltext)#debug
		for text in fulltext:
			#iterating over parts of a long split message
			while True:
				try:
					if text:
						self.bot.sendChatAction(chat_id,telegram.ChatAction.TYPING)
						self.bot.sendMessage(chat_id=chat_id,
							text=text,
							parse_mode='Markdown' if markdown else None,
							disable_web_page_preview=(not preview),
							reply_markup=(telegram.ReplyKeyboardMarkup(key_markup) if key_markup != "SAME" else None) if key_markup else telegram.ReplyKeyboardHide()
							)
				except Exception as e:
					if "Message is too long" in str(e):
						self.sendMessage(chat_id=chat_id
							,text="Error: Message is too long!"
							)
						break
					if ("urlopen error" in str(e)) or ("timed out" in str(e)):
						logging.error("Could not send message. Retrying! Error: " + str(e))
						sleep(3)
						continue
					else:
						logging.error("Could not send message. Error: " + str(e))
				break

	def sendPic(self,chat_id,pic,caption=None):
		while True:
			try:
				logging.debug("Picture: " + str(pic))
				self.bot.sendChatAction(chat_id,telegram.ChatAction.UPLOAD_PHOTO)
				#set file read cursor to the beginning. This ensures that if a file needs to be re-read (may happen due to exception), it is read from the beginning.
				pic.seek(0)
				self.bot.sendPhoto(chat_id=chat_id,photo=pic,caption=caption)
			except Exception as e:
				logging.error("Could not send picture. Retrying! Error: " + str(e))
				continue
			break

	def getUpdates(self):
		'''
		Gets updates. Retries if it fails.
		'''
		#if getting updates fails - retry
		while True:
			try:
				updates = self.bot.getUpdates(offset=self.LAST_UPDATE_ID)
			except Exception as e:
				logging.error("Could not read updates. Retrying! Error: " + str(sys.exc_info()[-1].tb_lineno) + ": " + str(e))
				continue
			break
		return updates

	def echo(self,processingFunction):

		bot= self.bot

		updates = self.getUpdates()

		#main message processing routine
		for update in updates:
			logging.warning("Received message: " + str(update.message.chat_id) + " " + update.message.from_user.username + " " + update.message.text)

			processingFunction(update=update)

			# Updates global offset to get the new updates
			self.LAST_UPDATE_ID = update.update_id + 1