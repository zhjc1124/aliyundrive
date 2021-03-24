import requests
import re
from utils import *
import json
import time


class Login(object):
    session = requests.session()
    session.headers['User-Agent'] = UA
    access_token = None

    def __init__(self, configfile='user.ini'):
        self._init()
        self.configfile = configfile
        self.user = read_conf(configfile)
        if self.user['username'] and self.user['password']:
            self.login_by_password(self.user['username'], self.user['password'])
        if self.access_token:
            print('Login success!')
        else:
            print('Please login')

    # it seems no need
    def _init(self):
        s = self.session

        # get client_id
        r = s.request(**SIGN)
        self.client_id = re.findall(r'client_id:"(.*?)"', r.text)[0]

        # get cookie
        AUTHORIZE['params']['client_id'] = self.client_id
        r = s.request(**AUTHORIZE)

        # set some useless cookie
        r = s.request(**MINI_LOGIN)

    def login_by_rsa(self, username, rsa):
        self.user['username'] = username
        s = self.session

        LOGIN['data']['loginId'] = username
        LOGIN['data']['password2'] = rsa
        r = s.request(**LOGIN)
        data = json.loads(r.text)['content']['data']

        if 'bizExt' not in data:
            print(data['titleMsg'])
            return False
        else:
            self.parse_biz_ext(data)
        return True

    def login_by_password(self, username, password):
        self.user['password'] = password
        rsa = encrypt(password)
        self.login_by_rsa(username, rsa)

    # not work
    # def login_by_qrcode(self):
    #     s = self.session
    #
    #     r = s.request(**QR_GEN)
    #     data = json.loads(r.text)['content']['data']
    #     t = data['t']
    #     code = data['codeContent']
    #
    #     print(code)
    #     r = s.get(code)
    #     print(r.text)
    #
    #     QR_QUERY['data']['t'] = t
    #     # wait 30 * 2s = 60s
    #     for i in range(30):
    #         r = s.request(**QR_QUERY)
    #         data = json.loads(r.text)['content']['data']
    #         if 'bizExt' not in data:
    #             time.sleep(2)
    #         else:
    #             self.parse_biz_ext(data)
    #             return True
    #     return False

    def login_by_sms(self, username, phone_code='86'):
        s = self.session

        SMS_SEND['data']['loginId'] = username
        r = s.request(**SMS_SEND)
        data = json.loads(r.text)['content']['data']

        if 'smsToken' not in data:
            print(data['titleMsg'])
            return False
        else:
            sms_token = data['smsToken']

        sms_code = input('Please input the sms code: ')
        SMS_LOGIN['data']['loginId'] = username
        SMS_LOGIN['data']['smsToken'] = sms_token
        SMS_LOGIN['data']['smsCode'] = sms_code
        r = s.request(**SMS_LOGIN)
        data = json.loads(r.text)['content']['data']

        if 'bizExt' not in data:
            print(data['titleMsg'])
            return False
        else:
            self.parse_biz_ext(data)
        return True

    def parse_biz_ext(self, data):
        biz_ext = data['bizExt']
        biz_ext = b64decode(biz_ext)
        access_token = json.loads(biz_ext)['pds_login_result']['accessToken']
        self.access_token = access_token
        save_conf(self.user, self.configfile)



