# -*- coding: utf-8 -*-

from math import sqrt


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

if __name__ == '__main__':
    pass

