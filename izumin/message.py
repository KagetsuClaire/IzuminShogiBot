# -*- coding: utf-8 -*-

from datetime import date, datetime
import importlib
import psycopg2
import psycopg2.extras
import random

from izumin import config, math

if config.IS_PRODUCTION_ENVIRONMENT:
    db = importlib.import_module("izumin.db")
else:
    db = importlib.import_module("izumin.db_local")


def select_random(exclude_message_list):
    """
    データベースに保存されているメッセージ候補からランダムで1つ選んで返す。
    引数でメッセージをリスト形式で渡すと候補から外す。
    :param exclude_message_list: 除外するメッセージのリスト
    :return: ランダムに選ばれたメッセージ文字列
    """
    post_time = datetime.now().strftime("%H:%M:%S")
    connection = psycopg2.connect(dbname=db.DATABASE_NAME,
                                  user=db.DATABASE_USER,
                                  password=db.DATABASE_PASSWORD,
                                  host=db.DATABASE_HOST,
                                  port=db.DATABASE_PORT)

    cur = connection.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute("SELECT post_message FROM regularly_post WHERE start_time <= %s AND end_time >= %s",
                (post_time, post_time))
    message_list = list(cur)

    random.seed()
    is_post_decision = False  # 何を投稿するか決定したかどうかのフラグ
    message_candidate = ""
    while not is_post_decision:
        # message_listの中からランダムにメッセージを選択する。
        message_candidate = random.choice(message_list)[0]

        # 除外するメッセージのリストに含まれていないか確認する。
        for i in range(0, len(exclude_message_list)):
            if exclude_message_list[i] == message_candidate:
                break  # 選び直す。
        else:
            is_post_decision = True

    return message_candidate


def select_go_home_random():
    """
    データベースに保存されている帰宅メッセージ候補からランダムで1つ選んで返す。
    :return: ランダムに選ばれたメッセージ文字列
    """
    connection = psycopg2.connect(dbname=db.DATABASE_NAME,
                                  user=db.DATABASE_USER,
                                  password=db.DATABASE_PASSWORD,
                                  host=db.DATABASE_HOST,
                                  port=db.DATABASE_PORT)

    cur = connection.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute("SELECT post_message "
                "FROM regularly_post "
                "WHERE start_time = '20:00:00'")
    tweet_candidate = random.choice(list(cur))[0]
    return tweet_candidate


def make_prime_message():
    """
    毎日0:00に投稿する、よるほー＆素数情報メッセージを作成して返す。
    :return: よるほーメッセージ
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
        connection = psycopg2.connect(dbname=db.DATABASE_NAME,
                                      user=db.DATABASE_USER,
                                      password=db.DATABASE_PASSWORD,
                                      host=db.DATABASE_HOST,
                                      port=db.DATABASE_PORT)
        cur = connection.cursor(cursor_factory=psycopg2.extras.DictCursor)
        # 前回の素数日を取り出す。
        cur.execute("SELECT max(number), max(post_date) FROM number_history WHERE kind = 'prime'")
        # 前回の素数日との差を計算する。
        # ※もっときれいな方法がありそう
        elapsed = str(today - cur.fetchone()[1]).split(' ')[0]
        status += "\"は" + elapsed + "日ぶりの素数ね。"
        cur.execute("INSERT INTO number_history (number, kind, post_date) "
                    "VALUES (%s, %s, %s)", (today_number, 'prime', today))
        connection.commit()
    else:
        status += "\"は素数じゃないわね。"
    return status


def make_number_reply(screen_name, number):
    """
    引数で渡された数字を判定してメッセージを返す。
    :param screen_name: SNSのスクリーンネーム
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


if __name__ == '__main__':
    print(select_random([]))
