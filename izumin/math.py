# -*- coding: utf-8 -*-

import psycopg2
import psycopg2.extras
from math import sqrt

from izumin import db
# from izumin import db_local  # ローカルでテストする際はコメントを外す。


def is_prime(x):
    """引数が素数であるか判定する。"""

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
    """引数が完全数であるか判定する。"""

    # ローカルでテストする際はdbをコメントアウトし、db_localのコメントを外す。
    connection = psycopg2.connect(database=db.DATABASE_NAME,
                                  user=db.DATABASE_USER,
                                  password=db.DATABASE_PASSWORD,
                                  host=db.DATABASE_HOST,
                                  port=db.DATABASE_PORT)
    # connection = psycopg2.connect(database=db_local.DATABASE_NAME,
    #                               user=db_local.DATABASE_USER,
    #                               password=db_local.DATABASE_PASSWORD,
    #                               host=db_local.DATABASE_HOST,
    #                               port=db_local.DATABASE_PORT)

    dict_cur = connection.cursor(cursor_factory=psycopg2.extras.DictCursor)
    dict_cur.execute("SELECT number FROM perfect_number")
    for row in dict_cur:
        if x == row["number"]:
            return True
    else:
        return False


if __name__ == '__main__':
    if is_perfect_number(28):
        print("True")
    else:
        print("False")

