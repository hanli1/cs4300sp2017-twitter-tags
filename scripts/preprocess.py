# -*- coding: UTF-8 -*-
from __future__ import print_function  # Only needed for Python 2
import re


with open("user_tweets.csv", 'r+') as f:
  content = f.read()
  emoji_pattern = re.compile(
    u"(\ud83d[\ude00-\ude4f])|"  # emoticons
    u"(\ud83c[\udf00-\uffff])|"  # symbols & pictographs (1 of 2)
    u"(\ud83d[\u0000-\uddff])|"  # symbols & pictographs (2 of 2)
    u"(\ud83d[\ude80-\udeff])|"  # transport & map symbols
    u"(\ud83c[\udde0-\uddff])"  # flags (iOS)
    "+", flags=re.UNICODE)

  content = re.sub(emoji_pattern, "", content) # no emoji
  content = re.sub("[…]? http\S+", "", content) # remove links
  f.seek(0)
  f.write(content)
  f.truncate()



