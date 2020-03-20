#!/usr/bin/env python3
from mastodon import Mastodon, StreamListener
from dateutil.tz import tzutc
from dateutil import parser
import datetime
import re
import csv

API_URL = "https://botsin.space"
regex = re.compile("([0-1]\d|[2][0-3]):[0-5]\d")
languages = {
	"it":["Ciao @"," ti ricorderò di andare a dormire alle ore "," è ora di andare a dormire! Buonanotte!"],
	"es":["Hola @"," te recordaré que te vayas a dormir a las "," es hora de ir a dormir, buenas noches!"],
	"fr":["Salut @"," je vais te rappeler d'aller dormir à "," il est temps de dormir! Bonne nuit!"],
	"pt":["Ola' @"," vou lembrá-lo a dormir as "," é hora de ir dormir! Boa noite!"],
	"de":["Hallo @"," ich werde Sie daran erinnern um Uhr "," es ist Zeit zu schlafen! Gute Nacht!"],
	"en":["Hello @"," I'll remind you to go to sleep at "," time to go to bed! Good night!"]
}

class goodListener(StreamListener):

	def on_notification(self,notification):
		try:
			account = notification["account"]["acct"]
			content = notification["status"]["content"]
			goodNight = regex.search(content)
			if content.find("dormire") != -1:
				lang = 'it'
			elif content.find("dormiria") != -1:
				lang = 'es'
			elif content.find("dormir") != -1:
				lang = 'fr'
			elif content.find("dormia") != -1:
				lang = 'pt'
			elif content.find("schlafen") != -1:
				lang = 'de'
			else:
				lang = 'en'
			greet = languages[lang][0]
			reminder = languages[lang][1]	
		except KeyError:
			return
		try:
			result = goodNight.group()
			with open("schedule.csv","a") as file:
				row = [result,account,lang]
				writer = csv.writer(file)
				writer.writerow(row)
			mastodon.toot(greet+account+reminder+result)
		except AttributeError:
			return

	def handle_heartbeat(self):
		with open("schedule.csv","r") as file:
			reader = csv.reader(file)
			sentToBed = []
			for line,row in enumerate(reader):
				if parser.parse(row[0]) < datetime.datetime.now():
					greet = languages[row[2]][0]
					goodnight = languages[row[2]][2]
					mastodon.toot(greet+row[1]+goodnight)
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
