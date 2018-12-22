# -*- coding: utf-8 -*-

import importlib
from math import sqrt
import psycopg2
import psycopg2.extras

from izumin import config

if config.IS_PRODUCTION_ENVIRONMENT:
    db = importlib.import_module("izumin.db")
else:
    db = importlib.import_module("izumin.db_local")


def is_prime(x):
    """
    引数が素数であればTrue、そうでなければFalseを返す。
    :param x: 素数判定を行う数値
    :return: 引数xが素数であるか
    """
    if x < 2:  # 2未満は素数ではない。
        return False
    if x == 2 or x == 3 or x == 5:  # 2,3,5は素数である。
        return True
    if x % 2 == 0 or x % 3 == 0 or x % 5 == 0:  # 2,3,5で割り切れるということは素数ではない。
        return False

    # 試し割り
    prime = 7
    step = 4
    while prime <= sqrt(x):
        if x % prime == 0:
            return False
        prime += step
        step = 6 - step

    return True


def is_perfect_number(x):
    """
    引数が完全数であればTrue、そうでなければFalseを返す。
    :param x: 完全数判定を行う数値
    :return: 引数xが完全数であるか
    """
    connection = psycopg2.connect(dbname=db.DATABASE_NAME,
                                  user=db.DATABASE_USER,
                                  password=db.DATABASE_PASSWORD,
                                  host=db.DATABASE_HOST,
                                  port=db.DATABASE_PORT)

    cur = connection.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute("SELECT number FROM perfect_number")
    for row in cur:
        if x == row["number"]:
            return True
    else:
        return False


if __name__ == '__main__':
    if is_perfect_number(28):
        print("True")
    else:
        print("False")

