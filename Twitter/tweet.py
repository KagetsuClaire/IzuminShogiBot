# -*- coding: utf-8 -*-

from requests_oauthlib import OAuth1Session
import random
import json
from Twitter import keys


# ツイートクラス
class Twitter:
    statuses_url = "https://api.twitter.com/1.1/statuses"
    user_timeline_endpoint = "/user_timeline.json"
    mentions_timeline_endpoint = "/mentions_timeline.json"
    update_endpoint = "/update.json"
    tweet_file = "Contents/tweet_list.txt"

    def __init__(self):
        self.oauth_session = OAuth1Session(keys.CONSUMER_KEY,
                                           keys.CONSUMER_SECRET,
                                           keys.ACCESS_TOKEN,
                                           keys.ACCESS_SECRET)

    def random_update(self):
        # tweet_list.txtを開く。
        f = open(self.tweet_file, 'r', encoding="utf_8_sig")
        tweet_file_data = f.read()
        f.close()

        # ファイルから必要なデータのみ取り出す。
        tweet_list_including_garbage = tweet_file_data.split(',')
        tweet_list = list(filter(lambda s: s != '' and s != '\n', tweet_list_including_garbage))

        random.seed()
        is_tweet_decision = False  # 何をツイートするか決定したかどうかのフラグ
        while not is_tweet_decision:
            # tweet_listの中からランダムにツイートを選択する。
            tweet_candidate = random.choice(tweet_list)

            # 直近のツイート最大20件を取得し……
            get_response = self.oauth_session.get(self.statuses_url + self.user_timeline_endpoint + "?count=20")
            tweet_json = get_response.json()

            # 同じ内容のツイートをしていないか、確認する。
            i = 0
            recently_tweet_num = len(tweet_json)
            while i < recently_tweet_num:
                recently_tweet = json.dumps(tweet_json[i]["text"], ensure_ascii=False)
                if recently_tweet[1:len(recently_tweet) - 1] == tweet_candidate:
                    # 直近のツイートに今回のツイート候補が入っていたら選び直す。
                    break
                i = i + 1
            else:
                is_tweet_decision = True
        else:
            new_status = {'status': tweet_candidate}

        # ツイートする。
        post_response = self.oauth_session.post(self.statuses_url + self.update_endpoint, data=new_status)

        # ツイートが正しく送信されたか。
        if post_response.status_code == 200:
            print("OK")
        else:
            print("Status Code", post_response.status_code)
            post_json = post_response.json()
            print("Error  Code", post_json["errors"][0]["code"], ":", post_json["errors"][0]["message"])

    def reply(self):
        pass

random_update = Twitter().random_update
