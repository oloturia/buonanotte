#!/usr/bin/python3
from mastodon import Mastodon, StreamListener
from dateutil.tz import tzutc
from dateutil import parser
import datetime
import re
import csv

API_URL = "https://botsin.space"
regex_h = re.compile("\d+(?=\s(ore|ora|heu|Stu|stu|hor|hou))")
regex_m = re.compile("\d+(?=\s(min|Min))")
languages = {
    "it":["Ciao @"," ti ricorderò di andare a dormre fra "," è ora di andare a dormire! Buonanotte!"],
    "es":["Hola @"," te recordaré que te vayas a dormi en "," es hora de ir a dormir, buenas noches!"],
    "fr":["Salut @"," je vais te rappeler d'aller dormir en "," il est temps de dormir! Bonne nuit!"],
    "pt":["Ola' @"," vou lembrá-lo a dormir em "," é hora de ir dormir! Boa noite!"],
    "de":["Hallo @"," ich werde Sie daran erinnern in "," es ist Zeit zu schlafen! Gute Nacht!"],
    "en":["Hello @"," I'll remind you to go to sleep in "," time to go to bed! Good night!"]
}

class goodListener(StreamListener):

    def on_notification(self,notification):
        try:
            account = notification["account"]["acct"]
            content = notification["status"]["content"]

            goodNight_hours = regex_h.search(content)
            goodNight_minutes = regex_m.search(content)
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

        result = ""
        try:
            hours_delay = int(goodNight_hours.group())
            result += goodNight_hours.group()+"h "
        except AttributeError:
            hours_delay = 0
            
        try:
            minutes_delay = int(goodNight_minutes.group())
            result += goodNight_minutes.group()+"m"
        except AttributeError:
            minutes_delay = 0

        if hours_delay == minutes_delay == 0:
            mastodon.status_post("Can't find a valid time")

        datesleep = (datetime.datetime.now()+datetime.timedelta(hours=hours_delay,minutes=minutes_delay)).strftime("%Y/%m/%d %H:%M")
        with open("/mnt/nas/tmp/schedule.csv","a") as file:
            row = [datesleep,account,lang]
            writer = csv.writer(file)
            writer.writerow(row)
        mastodon.status_post(greet+account+reminder+result,visibility="direct")
        return

    def handle_heartbeat(self):
        with open("/mnt/nas/tmp/schedule.csv","r") as file:
            reader = csv.reader(file)
            sentToBed = []
            for line,row in enumerate(reader):
                if (parser.parse(row[0]) < datetime.datetime.now()):
                    greet = languages[row[2]][0]
                    goodnight = languages[row[2]][2]
                    mastodon.status_post(greet+row[1]+goodnight,visibility="direct")
                    sentToBed.append(line)
        if (len(sentToBed) > 0):
            with open("/mnt/nas/tmp/schedule.csv","r") as file:
                lines = file.readlines()
            with open("/mnt/nas/tmp/schedule.csv","w") as file:
                for line,row in enumerate(lines):
                    if not (line in sentToBed):
                        file.write(row)


if __name__ == "__main__":
    with open("/home/goodnight/Documents/buonanotte/token") as f:
        createapp = f.readlines()
    createapp = [x.strip() for x in createapp]
    TOKEN = createapp[0]
    mastodon = Mastodon(access_token = TOKEN, api_base_url = API_URL)
    listener = goodListener()
    mastodon.stream_user(listener)
