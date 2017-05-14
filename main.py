# -*- coding: utf-8 -*-

import datetime
import time

from Twitter import tweet

twitter = tweet.Twitter()
while True:
    now = datetime.datetime.now()
    if now.minute == 0 and now.hour % 4 == 0 and now.hour != 4:
        twitter.update(twitter.select_tweet_random())
    else:
        twitter.reply_check()
    time.sleep(60)
else:
    print("Exit")
