# -*- coding: utf-8 -*-

from datetime import datetime
import time

from izumin import message
from izumin.twitter import Twitter


def main():
    twitter = Twitter()
    while True:
        # ツイート＆トゥートする。
        now = datetime.now()
        if now.hour % 4 == 0 and now.minute == 0:
            if now.hour == 0:  # 0時：よるほー＆素数メッセージ
                prime_message = message.make_prime_message()
                twitter.update(prime_message)
            elif now.hour == 4:  # 4時：スキップ
                pass
            elif now.hour == 20:  # 20時：帰宅メッセージ
                go_home_message = message.select_go_home_random()
                twitter.update(go_home_message)
            else:  # それ以外：定期メッセージ
                regularly_message = message.select_random(twitter.user_timeline_recently_max20())
                twitter.update(regularly_message)
        else:  # 上記以外の時間はリプライが来ていないかチェックする。
            twitter.check_reply()

        # 一定時間スリープさせる。
        now = datetime.now()
        if now.hour % 4 == 3 and now.hour != 3 and now.minute == 59:
            # 定期つぶやき時間まで1分以内なので時間調整
            time.sleep(60 - now.second)
        else:
            time.sleep(60)


if __name__ == "__main__":
    main()
