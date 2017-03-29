# -*- coding: UTF-8 -*-
# from __future__ import unicode_literals
import re
import sys
import csv
# import codecs
reload(sys)
sys.setdefaultencoding('utf-8')

emoji_pattern = re.compile(
    u"(\ud83d[\ude00-\ude4f])|"  # emoticons
    u"(\ud83c[\udf00-\uffff])|"  # symbols & pictographs (1 of 2)
    u"(\ud83d[\u0000-\uddff])|"  # symbols & pictographs (2 of 2)
    u"(\ud83d[\ude80-\udeff])|"  # transport & map symbols
    u"(\ud83c[\udde0-\uddff])"  # flags (iOS)
    "+", flags=re.UNICODE)

new_file = open("processed_tweets.csv", "wb")

entire_text = []
with open('user_tweets.csv','rb') as f:
  reader = csv.reader(f)
  for a, b, line in reader:
    content =  re.sub(r'http\S+', '', line, flags=re.MULTILINE) # remove links
    content = content.decode('utf-8')
    # print content[:200]
    #\\U0001f(.*?)(?=[A-Za-z0-9_-])
    # text = u"hello 😔 🔥 🌱 world".encode('unicode-escape')
    # print text
    # print re.sub(emoji_pattern, "", text)
    content = re.sub(emoji_pattern, "", content) # no emoji
    # content = content.replace("??", "").replace("?", "")
    # print content[:200]
    # content = content.decode('unicode-escape')
    # new_file.write(content)
    entire_text.append([a, b, content])
    # content = re.sub("[…]? http\S+", "", content) # remove links

writer = csv.writer(new_file)
writer.writerows(entire_text)
new_file.close()


