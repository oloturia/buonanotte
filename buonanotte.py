#!/usr/bin/env python3
from mastodon import Mastodon, StreamListener
from dateutil.tz import tzutc
from dateutil import parser
import datetime
import re
import csv

API_URL = "https://botsin.space"
regex = re.compile("([0-1]\d|[2][0-3]):[0-5]\d")


class goodListener(StreamListener):

	def on_notification(self,notification):
		print("Notification received")
		account = notification["account"]["acct"]
		content = notification["status"]["content"]
		goodNight = regex.search(content)
		try:
			result = goodNight.group()
			with open("schedule.csv","a") as file:
				row = [result,account]
				writer = csv.writer(file)
				writer.writerow(row)
			mastodon.toot("Ciao @"+account+", ti ricordero' di andare a dormire alle ore "+result)
		except AttributeError:
			mastodon.toot("Ciao @"+account+", non ho capito a che ora vorresti andare a dormire")

	def handle_heartbeat(self):
		with open("schedule.csv","r") as file:
			reader = csv.reader(file)
			sentToBed = []
			for line,row in enumerate(reader):
				if parser.parse(row[0]) < datetime.datetime.now():
					mastodon.toot("Ciao @"+row[1]+" e' ora di andare a dormire! Buonanotte!")
					sentToBed.append(line)
		if (len(sentToBed) > 0):
			with open("schedule.csv","r") as file:
				lines = file.readlines()
			with open("schedule.csv","w") as file:
				for line,row in enumerate(lines):
					if not (line in sentToBed):
						file.write(row)


if __name__ == "__main__":
	with open("token") as f:
		createapp = f.readlines()
	createapp = [x.strip() for x in createapp]
	TOKEN = createapp[0]
	mastodon = Mastodon(access_token = TOKEN, api_base_url = API_URL)
	listener = goodListener()
	mastodon.stream_user(listener)
