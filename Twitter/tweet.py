# -*- coding: utf-8 -*-

import random
import tweepy
import time
import math
# from pprint import pprint  # デバッグ用
# from Twitter import keys_local  # ローカルでテストする際はコメントを外す。
from Twitter import keys
from Twitter import prime


class Twitter:
    """Twitterクラス"""

    def __init__(self):
        # ローカルでテストする際はkeysをコメントアウトし、keys_localのコメントを外す。
        self.auth = tweepy.OAuthHandler(keys.CONSUMER_KEY, keys.CONSUMER_SECRET)
        self.auth.set_access_token(keys.ACCESS_TOKEN, keys.ACCESS_SECRET)
        # self.auth = tweepy.OAuthHandler(keys_local.CONSUMER_KEY, keys_local.CONSUMER_SECRET)
        # self.auth.set_access_token(keys_local.ACCESS_TOKEN, keys_local.ACCESS_SECRET)
        self.api = tweepy.API(self.auth)
        self.previous_reply_id = self.api.mentions_timeline(count=1)[0].id
        print("Set previous reply id: ", self.previous_reply_id)

    def user_timeline(self):
        """直近の自分のツイート最大20件を取得し、リスト形式で返す。"""

        user_timeline_status = self.api.user_timeline()
        recently_tweet_num = len(user_timeline_status)  # 直近ツイート件数（基本は20件だが、ツイート数が20未満の場合はその数になる）

        # 直近のツイートをリスト形式にする。
        recently_tweet_list = []
        i = 0
        while i < recently_tweet_num:
            recently_tweet = user_timeline_status[i].text
            recently_tweet_list.append(recently_tweet)
            i = i + 1

        return recently_tweet_list

    def select_tweet_random(self):
        """ツイートリストの中からランダムで1つ選んで返す。"""

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
        recently_tweet_list = self.user_timeline()

        random.seed()
        is_tweet_decision = False  # 何をツイートするか決定したかどうかのフラグ
        while not is_tweet_decision:
            # tweet_listの中からランダムにツイートを選択する。
            tweet_candidate = random.choice(tweet_list)

            # 同じ内容のツイートをしていないか、確認する。
            i = 0
            recently_tweet_num = len(recently_tweet_list)
            while i < recently_tweet_num:
                if recently_tweet_list[i] == tweet_candidate:
                    # 直近のツイートに今回のツイート候補が入っていたら選び直す。
                    break
                i = i + 1
            else:
                is_tweet_decision = True

        return tweet_candidate

    def update(self, new_tweet):
        """new_tweetを投稿する。"""

        # ツイートする。
        try:
            self.api.update_status(new_tweet)
            print("Tweet succeeded")
        except tweepy.TweepError as e:
            print(e.reason)

    def reply_check(self):
        """リプライに反応する。"""

        print("Start reply check")
        # 前回からのリプライをすべて取得する。
        mentions_statuses = self.api.mentions_timeline(since_id=self.previous_reply_id)

        # リプライに1つずつ対応する。
        for mention in mentions_statuses:
            mention_id = mention.id  # リプライ先のツイートID
            mention_name = mention.author.screen_name  # リプライ相手のスクリーンネーム
            mention_text = mention.text.split(' ')
            self.previous_reply_id = mention_id  # 前回リプライのIDを更新

            print("Received reply, id: ", mention_id)
            print("mention name: ", mention_name)
            print("message is 「", mention.text, "」")

            if mention_text[1].isdigit():
                num = int(mention_text[1])  # [0]にはスクリーンネームが入っているはず
                reply_text = "@" + mention_name + " " + mention_text[1]
                if (math.log10(num) + 1) > 15:
                    self.api.update_status(status="@" + mention_name + " ごめんね。ちょっとわかんないや。",
                                           in_reply_to_status_id=mention_id)
                elif prime.is_prime(num):
                    self.api.update_status(status=reply_text + "は素数ね。",
                                           in_reply_to_status_id=mention_id)
                else:
                    self.api.update_status(status=reply_text + "は素数じゃないよ。",
                                           in_reply_to_status_id=mention_id)
        print("End reply check")

if __name__ == '__main__':
    twitter = Twitter()
    while True:
        twitter.reply_check()
        time.sleep(10)
    # twitter.update(twitter.select_tweet_random())
