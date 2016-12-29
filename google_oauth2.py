# -*- coding:utf-8 -*-
import httplib2
from datetime import datetime, timedelta
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage


class GoogleOAuth2:
    def __init__(self, oauth_client_file, scope, credentials_file):
        self._oauth_client_file = oauth_client_file
        self._scope = scope
        self._credentials_file = credentials_file
        self._credentials = None

    def login(self):
        storage = Storage(self._credentials_file)
        self._credentials = storage.get()

        # credentials ファイルがなければ取得する
        if self._credentials is None or self._credentials.invalid:
            self._credentials = _get_credentials_file(
                self._oauth_client_file, self._scope, self._credentials_file)

        self.refresh()

    def refresh(self):
        if (self._credentials.token_expiry - datetime.utcnow()) < timedelta(minutes=5):
            http = httplib2.Http()
            http = self._credentials.authorize(http)
            self._credentials.refresh(http)
            return True
        return False

    def get_credentials(self):
        return self._credentials

def _get_credentials_file(oauth_client_file, scope, credentials_file):
    u''' credentials ファイルを取得する
    '''
    # 認証フローを作成
    flow = flow_from_clientsecrets(
        oauth_client_file,
        scope = scope,
        redirect_uri = 'urn:ietf:wg:oauth:2.0:oob')

    auth_uri = flow.step1_get_authorize_url()

    print('OPEN BELOW URL BY BROWSER:')
    print(auth_uri)

    # ユーザーが token を入力するまで待つ
    token = input("INPUT YOUR CODE > ")

    credentials = flow.step2_exchange(token)

    Storage(credentials_file).put(credentials)
    return credentials




