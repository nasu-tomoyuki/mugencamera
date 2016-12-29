# -*- coding:utf-8 -*-
u"""
Picasa Web Albums Data API
https://developers.google.com/picasa-web/docs/2.0/developers_guide_protocol
"""

import requests
import time
import threading
import os
import os.path

from google_oauth2 import GoogleOAuth2
from requests_toolbelt import MultipartEncoder


BASE_URL = "https://picasaweb.google.com/data/feed/api"

mediaExtensions = {
    '.png': 'image/png',
    '.jpeg': 'image/jpeg',
    '.jpg': 'image/jpeg',

    '.avi': 'video/avi',
    '.wmv': 'video/wmv',
    '.3gp': 'video/3gp',
    '.m4v': 'video/m4v',
    '.mp4': 'video/mp4',

    '.h264': 'video/h264',

    #'.mov': 'video/mov',
    #'.mov': 'video/mp4',
    #'.mov': 'video/quicktime',
    #'.mov': 'video/x-m4v',
    #'.mov': 'video/h264',
    '.mov': 'video/quicktime',
    }

def get_content_type(file_name):
    _, ext = os.path.splitext(file_name)
    if ext in mediaExtensions:
        return mediaExtensions[ext]
    else:
        return None

class PhotoStocker(threading.Thread):
    u""" バックグラウンドで写真や動画を Google Photos に同期します
    """

    def __init__(self, oauth2, user_id, path):
        threading.Thread.__init__(self)
        self._running = True
        self._oauth2 = oauth2
        self._endpoint = '%s/user/default/albumid/default' % (BASE_URL)
        #self._endpoint = 'http://localhost:8080/'
        self._path = path
        self._in_processing = False

    def run(self):
        while self._running:
            self._in_processing = True
            files = os.listdir(self._path)
            for f in files:
                if get_content_type(f) == None:
                    continue

                print(f)
                r = self._oauth2.refresh()
                if r == True:
                    print('access token is refreshed')
                file_name = self._path + '/' + f
                self._post(file_name, f)
                os.remove(file_name)

            self._in_processing = False
            time.sleep(1)

    def processing(self):
        return self._in_processing

    def shutdown(self):
        self._running = False

    def _post(self, path, file_name):
        content_type = get_content_type(file_name)
        print(content_type)

        boundary = 'END_OF_PART'

        metadata = '''
<entry xmlns='http://www.w3.org/2005/Atom' xmlns:media='http://search.yahoo.com/mrss/' xmlns:gphoto='http://schemas.google.com/photos/2007'>
<title type='text'>%s</title>
<summary type='text'>by Mugencamera</summary>
<category scheme='http://schemas.google.com/g/2005#kind' term='http://schemas.google.com/photos/2007#photo'></category>
</entry>
''' % (file_name)

        multipart_data = MultipartEncoder(
            fields = {
                'file': (file_name, open(path, 'rb'), content_type),
                'metadata': ('', metadata, 'application/atom+xml'), 
                },
            boundary = boundary
            )

        body = multipart_data
        headers = {
            'Content-Type': 'multipart/related; boundary="%s"' % (boundary),
            'MIME-version': '1.0',
            'Authorization': 'OAuth ' + self._oauth2.get_credentials().access_token,
            }
        with requests.Session() as session:
            r = session.post(
                self._endpoint,
                headers = headers,
                data = body
                )
            print('%s %s' % (file_name, r))

        return



