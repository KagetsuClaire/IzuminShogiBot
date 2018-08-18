# -*- coding: utf-8 -*-

import time
from datetime import datetime

from izumin import twitter
from izumin import message

twitter = twitter.Twitter()
while True:
    # ツイートする。
    now = datetime.now()
    if now.hour % 4 == 0 and now.minute == 0:
        if now.hour == 0:  # 0時：よるほー＆素数メッセージ
            twitter.update(message.make_prime_message())
        elif now.hour == 4:  # 4時：スキップ
            pass
        elif now.hour == 20:  # 20時：帰宅ツイート
            twitter.update(message.select_go_home_random())
        else:  # それ以外：定期ツイート
            twitter.update(message.select_random(twitter.get_user_timeline_max20()))
    else:  # それ以外の時間はリプライが来ていないかチェックする。
        twitter.reply_check()

    # 一定時間スリープさせる。
    now = datetime.now()
    if now.hour % 4 == 3 and now.hour != 3 and now.minute == 59:
        # 定期ツイート時間まで1分以内なので時間調整
        time.sleep(60 - now.second)
    else:
        time.sleep(60)
