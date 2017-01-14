import logging

from argparse import ArgumentParser

from telegram.ext import Updater

from textual_data import BOT_TOKEN
from command_handler import UserCommandHandler
from rss_grabber import RSSGrabber

logging.basicConfig(format=u'[%(asctime)s] %(filename)s[LINE:%(lineno)d]# %(levelname)-8s  %(message)s',
					level=logging.WARNING)

class RSSParserBot(object):
	"""docstring for MultitranBot"""

	def __init__(self, token, update_mode="polling", server_IP="127.0.0.1", webhook_port=443, certificate_path="/tmp"):
		super(RSSParserBot, self).__init__()
		self.token = token
		self.update_mode = update_mode
		self.webhook_port = webhook_port
		self.server_IP = server_IP
		self.certificate_path = certificate_path

		self.updater = Updater(token=token)
		self.dispatcher = dispatcher = self.updater.dispatcher

		self.command_handler = UserCommandHandler(dispatcher)

	def run(self):
		rss = RSSGrabber(self.updater.bot, self.command_handler)
		rss.start_jobs()

		if self.update_mode=="polling":
			print("start polling")#debug
			self.updater.start_polling()
			# self.updater.idle()
		elif "webhook" in self.update_mode:
			self.updater.start_webhook(listen='127.0.0.1',
									   port=self.webhook_port, url_path=self.token)

			self.updater.bot.setWebhook(webhook_url='https://{0}:443/{1}'.format(self.server_IP,
																				 self.token,
																				 self.webhook_port),
										certificate=open(self.certificate_path,'rb'),
			)

			self.updater.idle()



def main():
	parser = ArgumentParser()
	parser.add_argument("-m","--mode",help='A mechanism of update getting of this bot. Defaults to "polling".\
										   Set to "webhook_nginx" to use webhooks with nginx',
						default="polling")
	parser.add_argument("-c","--cert",help="Path to certificate for webhook secure connection.", default='/tmp/cert.pem')
	parser.add_argument("--server-ip", help="IP address of this server. Needed to establish a webhook. \
											Defaults to localhost", default='127.0.0.1')
	parser.add_argument("-p", "--port", help="Port number for webhook connection. Defaults to 443.",
						type=int, default=443)


	# parse the arguments. They can be accessed in form args.argument
	args = parser.parse_args()

	bot = RSSParserBot(BOT_TOKEN, update_mode=args.mode, server_IP=args.server_ip,
					   webhook_port=args.port, certificate_path=args.cert)
	bot.run()


if __name__ == '__main__':
	main()
