# -*- coding: utf-8 -*-

import datetime
import time

from Twitter import tweet

while True:
    now = datetime.datetime.now()
    # UTC 19:00 == 日本時間4:00
    if now.minute == 0 and now.hour % 4 == 3 and now.hour != 19:
        tweet.random_update()
    time.sleep(60)
else:
    print("Exit")
