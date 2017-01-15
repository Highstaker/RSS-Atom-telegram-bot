import time

import feedparser

from telegram.ext import Job, JobQueue
from telegram.error import RetryAfter

from textual_data import URLS_FILENAME


class RSSGrabber(object):
	"""docstring for RSSGrabber"""
	def __init__(self, bot, command_handler):
		super(RSSGrabber, self).__init__()

		self._get_urls()

		self.bot = bot
		self.job_queue = JobQueue(bot)

		self.command_handler = command_handler

		self.latest_post_time = 0


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
					while True:
						try:
							self.command_handler.sendMessage(bot, update_or_chatid=chat_id, message=post)
							time.sleep(1.0)
							break
						except RetryAfter as e:
							# this stupid flood control
							print(str(e))
							time.sleep(1.0)

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
					text = "<b>" + entry['title'] + "</b>" + "\n"
					text += entry['content'][0]['value']
					text = text.replace("<br />", "\n").replace("&nbsp;", " ").replace("&quot;", '"').replace("&amp;", "&")
					# adding formatted time of posting
					text = "<i>" + time.strftime('%Y-%m-%d %H:%M', entry['published_parsed']) + "</i>" + "\n"+ text
					posts.append(text)
		print("Posts", posts)#debug

		if not self.latest_post_time:
			# if it is the first time, don't send content, just update the latest time
			self.latest_post_time = maximum_unix_time
			return []

		self.latest_post_time = max(maximum_unix_time, self.latest_post_time)
		return posts
