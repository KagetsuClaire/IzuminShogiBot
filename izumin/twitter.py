# -*- coding: utf-8 -*-

import datetime
import math
import random
import re
import time
import tweepy
# from pprint import pprint  # デバッグ用
# from izumin import keys_local  # ローカルでテストする際はコメントを外す。
from izumin import keys
from izumin import math


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

    def update(self, new_tweet, reply_id=None):
        """new_tweetを投稿する。"""

        # ツイートする。
        try:
            self.api.update_status(status=new_tweet, in_reply_to_status_id=reply_id)
            if reply_id is None:
                print("Tweet succeeded")
            else:
                print("Reply succeeded")
        except tweepy.TweepError as e:
            print(e.reason)

    def reply_check(self):
        """リプライに反応する。"""

        # 前回からのリプライをすべて取得する。
        mentions_statuses = self.api.mentions_timeline(since_id=self.previous_reply_id)

        # リプライに1つずつ対応する。
        for mention in mentions_statuses:
            mention_id = mention.id  # リプライ先のツイートID
            mention_name = mention.author.screen_name  # リプライ相手のスクリーンネーム
            mention_text = mention.text.split(' ')
            self.previous_reply_id = mention_id  # 前回リプライのIDを更新

            print("Received reply, id: ", mention_id)
            print("Mention Name: ", mention_name)
            print("Message is 「", mention.text, "」")

            completed_reply = False
            for text in mention_text:  # 送られてきたリプライを空白区切りで処理する。
                if text[0] == "@":
                    pass
                else:  # 数字のみ取り出す
                    num_candidate_list = re.split("\D+", text)
                    for num_candidate in num_candidate_list:
                        if num_candidate.isdigit():  # 空文字列が入っている可能性があるためチェックする。
                            num = int(num_candidate)
                            reply_text = self.prime_reply("@" + mention_name + " ", num)
                            self.update(reply_text, reply_id=mention_id)
                            completed_reply = True
            else:
                if not completed_reply:
                    print("Not reply")

    @staticmethod
    def prime_reply(screen_name, prime_candidate):
        """素数判定メッセージを返す。"""

        if len(str(prime_candidate)) > 15:
            reply = screen_name + "ごめんね。ちょっとわからないわ。"
        elif prime_candidate is 57:
            reply = screen_name + "ふふっ、" + str(prime_candidate) + "はグロタンディーク素数ね。"
        elif math.is_prime(prime_candidate):
            reply = screen_name + str(prime_candidate) + "は素数ね。"
        else:
            reply = screen_name + str(prime_candidate) + "は素数じゃないよ。"
        return reply

    @staticmethod
    def prime_message():
        """毎日0:00にツイートするその日の素数情報メッセージ"""

        today = datetime.date.today()
        # 西暦を文字列にして格納
        today_str = str(today.year)

        # 月を文字列にして連結
        if (math.log10(today.month) + 1) < 2:
            today_str = today_str + "0"
        today_str = today_str + str(today.month)

        # 日を文字列にして連結
        if (math.log10(today.day) + 1) < 2:
            today_str = today_str + "0"
        today_str = today_str + str(today.day)
        today_number = int(today_str)  # 数値化

        status = "よるほー。大石泉が0時をお知らせするよ。\n今日の日付、\""
        if math.is_prime(today_number):
            status = status + str(today_number) + "\"は素数ね。"
        else:
            status = status + str(today_number) + "\"は素数じゃないわね。"
        return status


if __name__ == '__main__':
    twitter = Twitter()
    while True:
        twitter.reply_check()
        time.sleep(60)
