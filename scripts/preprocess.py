# -*- coding: UTF-8 -*-
import re
import sys
import csv

#u use utf8 by default
reload(sys)
sys.setdefaultencoding('utf-8')

emoji_pattern = re.compile(
    u"(\ud83d[\ude00-\ude4f])|"  # emoticons
    u"(\ud83c[\udf00-\uffff])|"  # symbols & pictographs (1 of 2)
    u"(\ud83d[\u0000-\uddff])|"  # symbols & pictographs (2 of 2)
    u"(\ud83d[\ude80-\udeff])|"  # transport & map symbols
    u"(\ud83c[\udde0-\uddff])"  # flags (iOS)
    "+", flags=re.UNICODE)

processed_file = open("processed_tweets.csv", "wb")

entire_text = []
with open('user_tweets.csv','rb') as f:
  reader = csv.reader(f)
  for a, b, line in reader:
    content =  re.sub(r'http\S+', '', line, flags=re.MULTILINE) # remove links
    content = content.decode('utf-8')
    content = re.sub(emoji_pattern, "", content) # remove emojis
    entire_text.append([a, b, content])

writer = csv.writer(processed_file)
writer.writerows(entire_text)
processed_file.close()


