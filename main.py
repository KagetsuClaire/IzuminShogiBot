# -*- coding: utf-8 -*-

import datetime
import time

from Twitter import tweet

twitter = tweet.Twitter()
while True:
    # ツイートする。
    now = datetime.datetime.now()
    if now.hour % 4 == 0 and now.minute == 0:
        if now.hour == 0:  # 0時
            twitter.update(twitter.prime_message())
        elif now.hour != 4:  # 0,4時以外
            twitter.update(twitter.select_tweet_random())
        else:  # 4時はスキップ
            pass
    else:  # それ以外の時間はリプライが来ていないかチェックする。
        twitter.reply_check()

    # 一定時間スリープさせる。
    now = datetime.datetime.now()
    if now.hour % 4 == 3 and now.hour != 3 and now.minute == 59:
        # 定期ツイート時間まで1分以内なので時間調整
        time.sleep(60 - now.second)
    else:
        time.sleep(60)
else:
    print("Exit")
