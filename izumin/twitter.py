# -*- coding: utf-8 -*-

import importlib
import re
import tweepy

from izumin import config, message

if config.IS_PRODUCTION_ENVIRONMENT:
    key = importlib.import_module("izumin.key")
else:
    key = importlib.import_module("izumin.key_local")


class Twitter:
    """
    Twitterを操作するクラス
    """

    def __init__(self):
        self._auth = tweepy.OAuthHandler(key.CONSUMER_KEY, key.CONSUMER_SECRET)
        self._auth.set_access_token(key.ACCESS_TOKEN, key.ACCESS_SECRET)
        self._api = tweepy.API(self._auth)
        self._previous_reply_id = self._api.mentions_timeline(count=1)[0].id
        print("Set previous reply id: ", self._previous_reply_id)

    def get_user_timeline_max20(self):
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
                            reply_text = message.make_number_reply("@" + mention_name + " ", num)
                            self.update(reply_text, reply_id=mention_id)
                            completed_reply = True
            else:
                if not completed_reply:
                    print("Not reply")


if __name__ == '__main__':
    twitter = Twitter()
    print(message.select_random(twitter.get_user_timeline_max20()))
