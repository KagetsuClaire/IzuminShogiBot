# -*- coding: utf-8 -*-

import json
import random
import tweepy
# from Twitter import keys_local  # ローカルでテストする際はコメントを外す。
from Twitter import keys


class Twitter:
    """Twitterクラス"""

    def __init__(self):
        # ローカルでテストする際はkeysをコメントアウトし、keys_localのコメントを外す。
        self.auth = tweepy.OAuthHandler(keys.CONSUMER_KEY, keys.CONSUMER_SECRET)
        self.auth.set_access_token(keys.ACCESS_TOKEN, keys.ACCESS_SECRET)
        # self.auth = tweepy.OAuthHandler(keys_local.CONSUMER_KEY, keys_local.CONSUMER_SECRET)
        # self.auth.set_access_token(keys_local.ACCESS_TOKEN, keys_local.ACCESS_SECRET)
        self.api = tweepy.API(self.auth)

    # ツイートリストの中からランダムで1つ選んで返す。
    def select_tweet_random(self):
        # main.pyからimportされた場合とコマンドラインから直接実行された場合で、
        # ツイートリストの相対パスが違うのでここで設定する。
        if __name__ == '__main__':
            tweet_file = "../Contents/tweet_list.txt"
        else:
            tweet_file = "Contents/tweet_list.txt"

        # tweet_list.txtを読み込む。
        f = open(tweet_file, 'r', encoding="utf_8_sig")
        tweet_file_data = f.read()
        f.close()

        # ファイルから必要なデータのみ取り出す。
        tweet_list_including_garbage = tweet_file_data.split('"')
        tweet_list = list(filter(lambda s: s != '' and s != '\n', tweet_list_including_garbage))

        # 直近のツイート最大20件を取得する。
        get_response = self.oauth_session.get(self.statuses_url + self.user_timeline_endpoint + "?count=20")
        tweet_json = get_response.json()
        recently_tweet_num = len(tweet_json)  # 直近ツイート件数（基本は20件だが、ツイート数が20未満の場合はその数になる）

        # 直近のツイートをリスト形式にする。
        recently_tweet_list = []
        i = 0
        while i < recently_tweet_num:
            recently_tweet = json.dumps(tweet_json[i]["text"], ensure_ascii=False)
            recently_tweet_list.append(recently_tweet[1:len(recently_tweet) - 1])
            i = i + 1

        random.seed()
        is_tweet_decision = False  # 何をツイートするか決定したかどうかのフラグ
        while not is_tweet_decision:
            # tweet_listの中からランダムにツイートを選択する。
            tweet_candidate = random.choice(tweet_list)

            # 同じ内容のツイートをしていないか、確認する。
            i = 0
            while i < recently_tweet_num:
                if recently_tweet_list[i] == tweet_candidate:
                    # 直近のツイートに今回のツイート候補が入っていたら選び直す。
                    break
                i = i + 1
            else:
                is_tweet_decision = True

        return tweet_candidate

    # new_tweetを投稿する。
    def update(self, new_tweet):
        # ツイートする。
        try:
            self.api.update_status(new_tweet)
            print("Tweet succeeded")
        except tweepy.TweepError as e:
            print(e.reason)

    def reply(self):
        pass

if __name__ == '__main__':
    Twitter().update("tweepy test.")

