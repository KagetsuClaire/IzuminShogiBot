# -*- coding: utf-8 -*-

import datetime
import time

from Twitter import tweet

while True:
    twitter = tweet.Twitter()
    now = datetime.datetime.now()
    if now.minute == 0 and now.hour % 4 == 0 and now.hour != 4:
        twitter.update(twitter.select_tweet_random())
    time.sleep(60)
else:
    print("Exit")
