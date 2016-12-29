# -*- coding:utf-8 -*-
import io
import os
import picamera
import time
from PIL import Image

import average_hash
from config import *


def shot(camera):
    stream = io.BytesIO()
    camera.capture(stream, format='jpeg')
    stream.seek(0)
    return Image.open(stream)


def record(camera, path, filename, hash, make_filename):
    recording_file_name = path + '/' + 'recording.tmp'
    save_file_name = '%s/%s.mov' % (path, filename)

    # 録画用の一時ファイルがあれば削除する
    if os.path.exists(recording_file_name):
        os.remove(recording_file_name)

    # 録画時間
    duration = 0

    try:
        camera.start_recording(recording_file_name, format='h264')

        # 録画延長判定
        while duration < RECORDING_TIME_LIMIT:
            time.sleep(RECORDING_TIME_PERIOD)
            duration += RECORDING_TIME_PERIOD

            image = shot(camera)
            hash2 = average_hash.get_average_hash(image)
            hamming_distance = average_hash.get_hamming_distance(hash, hash2)
            # 録画終了
            if hamming_distance < RECORDING_THRESHOLD:
                hash = hash2
                break
            fn = make_filename()
            # 録画を延長する場合はスナップショットを保存
            image.save('%s/%s.jpg' % (path, fn))
            hash = hash2

        camera.stop_recording()
    except OSError as err:
        # no disc space
        if err.errno == 28:
            return False
        raise
    else:
        os.rename(recording_file_name, save_file_name)
    return True, hash

