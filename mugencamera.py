# -*- coding:utf-8 -*-
u""" 無限カメラ 無限に監視できます
"""

import time
import picamera

from google_oauth2 import GoogleOAuth2
from photo_stocker import PhotoStocker
import camera as mc
import average_hash
from config import *


USAGE = u"""{f}

Usage:
    {f} [-d | --tmpdir <tmp_dir>] [--vflip] [--hflip]
    {f} -h | --help

Options:
    -d --tmpdir <tmp_dir>    temporary directory
    --vflip                  Flip vertically
    --hflip                  Flip horizontally
    -h --help                Show this screen and exit.
""".format(f=__file__)

from docopt import docopt

def parse():
    args = docopt(USAGE)
    if '--tmpdir' not in args:
        args['--tmpdir'] = ["."]
    return args

import datetime
def make_filename():
    t = datetime.datetime.today()
    return t.strftime("%Y%m%d-%H%M%S")



# 利用する Google API のスコープを指定
SCOPE = 'https://picasaweb.google.com/data/'

# Google のアプリケーションに作成した OAuth クライアント情報
# https://code.google.com/apis/console/
OAUTH_CLIENT_FILE = './secret/oauth2.json'

# OAuth2 の credentials ファイルの保存場所
CREDENTIALS_FILE = './secret/credentials.json'


if __name__ == '__main__':
    args = parse()
    tmpdir = args['--tmpdir'][0]

    oauth2 = GoogleOAuth2(OAUTH_CLIENT_FILE, SCOPE, CREDENTIALS_FILE)
    oauth2.login()

    with picamera.PiCamera() as camera:
        #camera.resolution = '1080p'
        camera.resolution = 'VGA'
        #camera.led = False
        camera.led = True
        camera.flash_mode = 'auto'
        if args['--vflip']:
            camera.vflip = True
        if args['--hflip']:
            camera.hflip = True

        photo_stocker = PhotoStocker(oauth2, GOOGLE_USER_ID, tmpdir)
        photo_stocker.start()

        # カメラの安定待ち
        time.sleep(1)

        # 基準画像を撮影
        image = mc.shot(camera)
        origin_hash = average_hash.get_average_hash(image)

        while True:
            # 比較画像を撮影
            image = mc.shot(camera)
            validation_hash = average_hash.get_average_hash(image)
            hamming_distance = average_hash.get_hamming_distance(origin_hash, validation_hash)
            print('hamming distance: ' + str(hamming_distance))

            # 録画判定
            if hamming_distance >= RECORDING_THRESHOLD:
                filename = make_filename()
                image.save(tmpdir + '/' + filename + '.jpg')
                ret, validation_hash = mc.record(
                    camera, tmpdir, filename, validation_hash, make_filename)
                # ディスク容量不足で書き込みに失敗した場合は転送処理が終わるまで待つ
                while ret == False and photo_stocker.processing():
                    pass
                origin_hash = validation_hash
            time.sleep(0.1)


        # 転送の終了待ち
        photo_stocker.shutdown()
        while photo_stocker.processing():
            pass


