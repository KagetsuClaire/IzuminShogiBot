# -*- coding: utf-8 -*-

import psycopg2
import psycopg2.extras
import random
import re
import tweepy
from datetime import datetime, date

from izumin import db        # 本番環境ではこちら
# from izumin import db_local  # ローカルではこちら
from izumin import key        # 本番環境ではこちら
# from izumin import key_local  # ローカルではこちら
from izumin import math


class Twitter:
    """
    Twitterに関する操作を行うクラス
    """

    def __init__(self):
        # ローカルでテストする際はkeyをコメントアウトし、key_localのコメントを外す。
        self._auth = tweepy.OAuthHandler(key.CONSUMER_KEY, key.CONSUMER_SECRET)
        self._auth.set_access_token(key.ACCESS_TOKEN, key.ACCESS_SECRET)
        # self._auth = tweepy.OAuthHandler(key_local.CONSUMER_KEY, key_local.CONSUMER_SECRET)
        # self._auth.set_access_token(key_local.ACCESS_TOKEN, key_local.ACCESS_SECRET)
        self._api = tweepy.API(self._auth)
        self._previous_reply_id = self._api.mentions_timeline(count=1)[0].id
        print("Set previous reply id: ", self._previous_reply_id)

    def get_user_timeline(self):
        """
        直近の自分のツイート最大20件を取得し、リスト形式にして返す。
        :return: 直近の自分のツイート最大20件のリスト
        """

        user_timeline_status = self._api.user_timeline()
        recently_tweet_num = len(user_timeline_status)  # 直近ツイート件数（基本は20件だが、ツイート数が20未満の場合はその数になる）

        # 直近のツイートをリスト形式にする。
        recently_tweet_list = []
        for i in range(0, recently_tweet_num):
            recently_tweet = user_timeline_status[i].text
            recently_tweet_list.append(recently_tweet)

        return recently_tweet_list

    def select_tweet_random(self):
        """
        引数で指定されたファイルに保存されているツイート候補からランダムで1つ選んで返す。
        :return: ランダムに選ばれたツイート文字列
        """

        tweet_time = datetime.now().strftime("%H:%M:%S")
        # ローカルでテストする際はdbをコメントアウトし、db_localのコメントを外す。
        connection = psycopg2.connect(dbname=db.DATABASE_NAME,
                                      user=db.DATABASE_USER,
                                      password=db.DATABASE_PASSWORD,
                                      host=db.DATABASE_HOST,
                                      port=db.DATABASE_PORT)
        # connection = psycopg2.connect(dbname=db_local.DATABASE_NAME,
        #                               user=db_local.DATABASE_USER,
        #                               password=db_local.DATABASE_PASSWORD,
        #                               host=db_local.DATABASE_HOST,
        #                               port=db_local.DATABASE_PORT)

        cur = connection.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute("SELECT tweet FROM regularly_tweet WHERE start_time <= %s AND end_time >= %s",
                    (tweet_time, tweet_time))
        tweet_list = list(cur)

        # 直近のツイート最大20件を取得する。
        recently_tweet_list = self.get_user_timeline()

        random.seed()
        is_tweet_decision = False  # 何をツイートするか決定したかどうかのフラグ
        tweet_candidate = ""
        while not is_tweet_decision:
            # tweet_listの中からランダムにツイートを選択する。
            tweet_candidate = random.choice(tweet_list)[0]

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

    @staticmethod
    def select_go_home_tweet_random():
        # ローカルでテストする際はdbをコメントアウトし、db_localのコメントを外す。
        connection = psycopg2.connect(dbname=db.DATABASE_NAME,
                                      user=db.DATABASE_USER,
                                      password=db.DATABASE_PASSWORD,
                                      host=db.DATABASE_HOST,
                                      port=db.DATABASE_PORT)
        # connection = psycopg2.connect(dbname=db_local.DATABASE_NAME,
        #                               user=db_local.DATABASE_USER,
        #                               password=db_local.DATABASE_PASSWORD,
        #                               host=db_local.DATABASE_HOST,
        #                               port=db_local.DATABASE_PORT)

        cur = connection.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute("SELECT tweet "
                    "FROM regularly_tweet "
                    "WHERE start_time = '20:00:00'")
        tweet_candidate = random.choice(list(cur))[0]
        return tweet_candidate

    def update(self, new_tweet, reply_id=None):
        """
        ツイートを投稿する。
        :param new_tweet: ツイート文字列
        :param reply_id: リプライ先のスクリーンネーム（リプライの場合のみ指定する）
        :return:
        """

        # ツイートする。
        try:
            self._api.update_status(status=new_tweet, in_reply_to_status_id=reply_id)
            if reply_id is None:
                print("Tweet succeeded")
            else:
                print("Reply succeeded")
        except tweepy.TweepError as e:
            print(e.reason)

    def reply_check(self):
        """
        リプライに反応する。
        :return:
        """

        # 前回からのリプライをすべて取得する。
        mentions_statuses = self._api.mentions_timeline(since_id=self._previous_reply_id)

        # リプライに1つずつ対応する。
        for mention in mentions_statuses:
            mention_id = mention.id  # リプライ先のツイートID
            mention_name = mention.author.screen_name  # リプライ相手のスクリーンネーム
            mention_text = mention.text.split(' ')
            self._previous_reply_id = mention_id  # 前回リプライのIDを更新

            print("Received reply, id: ", mention_id)
            print("Mention name: ", mention_name)
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
                            reply_text = self.make_number_reply("@" + mention_name + " ", num)
                            self.update(reply_text, reply_id=mention_id)
                            completed_reply = True
            else:
                if not completed_reply:
                    print("Not reply")

    @staticmethod
    def make_number_reply(screen_name, number):
        """
        引数で渡された数字を判定して適切なメッセージを返す。
        :param screen_name: Twitterのスクリーンネーム
        :param number: 判定する数字
        :return: リプライ文字列
        """

        reply = screen_name
        if len(str(number)) > 15:
            reply += "ごめんね。ちょっとわからないな。"
        elif math.is_perfect_number(number):
            reply += str(number) + "は完全数だね。すっごーい！"
        elif number is 57:
            reply += "ふふっ、" + str(number) + "はグロタンディーク素数ね。"
        elif math.is_prime(number):
            reply += str(number) + "は素数ね。"
        else:
            reply += str(number) + "は素数じゃないよ。"
        return reply

    @staticmethod
    def make_prime_message():
        """
        毎日0:00にツイートする、よるほー＆素数情報メッセージを作成して返す。
        :return: よるほーツイート
        """

        today = date.today()
        # 西暦を文字列にして格納
        year = str(today.year)

        # 月を文字列にして格納
        month = ""
        if len(str(today.month)) < 2:
            month = "0"
        month += str(today.month)

        # 日を文字列にして格納
        day = ""
        if len(str(today.day)) < 2:
            day = "0"
        day += str(today.day)
        today_number = int(year + month + day)  # 連結＆数値化

        status = "よるほー。大石泉が0時をお知らせするよ。今日の日付、\"" + str(today_number)
        if math.is_prime(today_number):
            # ローカルでテストする際はdbをコメントアウトし、db_localのコメントを外す。
            connection = psycopg2.connect(dbname=db.DATABASE_NAME,
                                          user=db.DATABASE_USER,
                                          password=db.DATABASE_PASSWORD,
                                          host=db.DATABASE_HOST,
                                          port=db.DATABASE_PORT)
            # connection = psycopg2.connect(dbname=db_local.DATABASE_NAME,
            #                               user=db_local.DATABASE_USER,
            #                               password=db_local.DATABASE_PASSWORD,
            #                               host=db_local.DATABASE_HOST,
            #                               port=db_local.DATABASE_PORT)
            cur = connection.cursor(cursor_factory=psycopg2.extras.DictCursor)
            # 前回の素数日を取り出す。
            cur.execute("SELECT max(number), max(tweet_date) FROM number_history WHERE kind = 'prime'")
            # 前回の素数日との差を計算する。
            # ※もっときれいな方法がありそう
            elapsed = str(today - cur.fetchone()[1]).split(' ')[0]
            status += "\"は" + elapsed + "日ぶりの素数ね。"
            cur.execute("INSERT INTO number_history (number, kind, tweet_date) "
                        "VALUES (%s, %s, %s)", (today_number, 'prime', today))
            connection.commit()
        else:
            status += "\"は素数じゃないわね。"
        return status


if __name__ == '__main__':
    twitter = Twitter()
    print(twitter.make_prime_message())
