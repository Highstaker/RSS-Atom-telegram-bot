import time

import feedparser

from telegram.ext import Updater, CommandHandler, Job, JobQueue

from textual_data import URLS_FILENAME


class RSSGrabber(object):
	"""docstring for RSSGrabber"""
	def __init__(self, bot, command_handler):
		super(RSSGrabber, self).__init__()

		self._get_urls()

		self.bot = bot
		self.job_queue = JobQueue(bot)

		self.command_handler = command_handler

		self.latest_post_time = time.time()


	def _get_urls(self):
		with open(URLS_FILENAME,'r') as f:
			self.urls = tuple(i for i in f.read().split("\n") if i)

	def start_jobs(self):
		job = Job(self.send_rss_posts, interval=60,)
		self.job_queue.put(job)
		self.job_queue.start()

	def send_rss_posts(self, bot, job):
		subbed_users = self.command_handler.userparams.getSubscribedUsers()
		if subbed_users:
			posts = self.get_posts()

			for chat_id in subbed_users:
				for post in posts:
					self.command_handler.sendMessage(bot, update_or_chatid=chat_id, message=post)
					time.sleep(5.0)

	def get_posts(self):
		# local variable to temporarily storage maximum time
		# the posts will be compared against `self.latest_post` to determine whether to send them or not
		posts = []
		maximum_unix_time = 0
		for url in self.urls:
			parse = feedparser.parse(url)
			entries = parse['entries']
			for entry in entries:
				published_unix = time.mktime(entry['published_parsed'])
				maximum_unix_time = max(maximum_unix_time, published_unix)
				if published_unix > self.latest_post_time:
					text = entry['content'][0]['value']
					text = text.replace("<br />", "\n").replace("<b>", "").replace("</b>", "")
					# adding formatted time of posting
					text = time.strftime('%Y-%m-%d %H:%M', entry['published_parsed']) + "\n"+ text
					posts.append(text)
		print("Posts", posts)#debug

		self.latest_post_time = maximum_unix_time
		return posts