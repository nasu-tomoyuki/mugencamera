# -*- coding:utf-8 -*-

from PIL import Image

def get_average_hash(image):
    # 白黒化
    image = image.convert('L')
    # 縦横比を短い方に揃える (正方形にする)
    l = min(image.size[0], image.size[1])
    image = image.resize((l, l))
    # 8x8 にする
    image.thumbnail((8, 8), Image.ANTIALIAS)

    # 平均輝度を算出
    sum_pixels = 0
    data = image.getdata()
    for d in data:
        sum_pixels += d
    average = (int)(sum_pixels / 64.0)

    # ハッシュ化
    hash = 0
    one = 1
    for d in data:
        if d > average:
            hash |= one
        one = one << 1

    return hash

def get_hamming_distance(hash1, hash2):
    distance = 0
    for i in range(64):
        k = 1 << i
        if ( hash1 & k ) != ( hash2 & k ):
            distance += 1
    return distance

