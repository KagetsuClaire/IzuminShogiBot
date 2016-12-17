# -*- coding: utf-8 -*-

import datetime
import time

from Twitter import tweet

while True:
    now = datetime.datetime.now()
    if now.minute == 0 and now.hour % 4 == 0 and now.hour != 4:
        tweet.random_update()
    time.sleep(60)
else:
    print("Exit")
