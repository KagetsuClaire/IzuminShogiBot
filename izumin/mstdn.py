# -*- coding: utf-8 -*-

import importlib
import re

from mastodon import Mastodon

from izumin import config, message

if config.IS_PRODUCTION_ENVIRONMENT:
    key = importlib.import_module("izumin.mstdn_key")
else:
    key = importlib.import_module("izumin.mstdn_key_local")


class Mstdn:
    """
    Mastodonアカウントを操作するクラス
    """

    def __init__(self):
        self._mastodon = Mastodon(
            client_id=key.CLIENT_ID,
            client_secret=key.CLIENT_SECRET,
            access_token=key.ACCESS_TOKEN,
            api_base_url="https://imastodon.net"
        )
        # ホームタイムラインの一番新しいトゥートを最後にチェックしたトゥートということにする。
        # これ以降のトゥートはリプライチェックされる。
        self._last_checked_id = self._mastodon.timeline_home(limit=1)[0]['id']
        print(f"[Mastodon] Set last checked id: {self._last_checked_id}")

    def user_timeline_recently_max20(self):
        """
        直近の自分のトゥート最大20件を取得し、リスト形式にして返す。
        :return: 直近の自分のトゥート最大20件のリスト
        """
        pass

    def update(self, new_toot, reply_id=None):
        """
        トゥートを投稿する。
        :param new_toot: トゥート文字列
        :param reply_id: リプライ先のスクリーンネーム（リプライの場合のみ指定する）
        :return:
        """
        try:
            self._mastodon.status_post(status=new_toot, in_reply_to_id=reply_id, visibility="unlisted")
            if reply_id is None:
                print("[Mastodon] Toot succeeded.")
            else:
                print("[Mastodon] Reply succeeded.")
        except ValueError as e:
            print(e)

    def check_reply(self):
        """
        リプライに反応する。
        :return:
        """

        conv = re.compile(r"<[^>]*?>")

        # 前回チェック以降のホームタイムラインのトゥートをすべて取得する。
        home_timeline_list = self._mastodon.timeline_home(since_id=self._last_checked_id)

        # リプライであれば対応する。
        for toot in home_timeline_list:
            self._last_checked_id = toot['id']
            for mention in toot['mentions']:
                if mention['username'] == 'izumin_shogi':
                    mention_id = toot['id']
                    mention_name = toot['account']['username']
                    mention_text = conv.sub("", toot['content'])
                    mention_text_arr = mention_text.split(' ')

                    print(f"[Mastodon] Received reply, id: {mention_id}")
                    print(f"[Mastodon] Mention name: {mention_name}")
                    print(f"[Mastodon] Message is \"{mention_text}\"")

                    completed_reply = False
                    for text in mention_text_arr:
                        if text[0] == "@":
                            pass
                        else:  # 数字のみ取り出す
                            num_candidate_list = re.split(r"\D+", text)
                            for num_candidate in num_candidate_list:
                                if num_candidate.isdigit():  # 空文字列が入っている可能性があるためチェックする。
                                    num = int(num_candidate)
                                    reply_text = message.make_number_reply(f"@{mention_name}", num)
                                    self.update(reply_text, reply_id=mention_id)
                                    completed_reply = True
                    else:
                        if not completed_reply:
                            print("[Mastodon] Not reply")


if __name__ == '__main__':
    mastodon = Mstdn()
    mastodon.check_reply()
