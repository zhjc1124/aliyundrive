import base64
import configparser
import rsa
import os
import logging
from urllib.parse import urlparse, parse_qs
__all__ = ['logger', 'UA', 'SIGN', 'AUTHORIZE', 'MINI_LOGIN', 'LOGIN', 'TOKEN_LOGIN', 'TOKEN_GET',
           'QR_GEN', 'QR_QUERY', 'SMS_SEND', 'SMS_LOGIN', 'b64decode', 'save_conf', 'read_conf', 'encrypt',
           ]

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(os.path.dirname(ROOT_DIR))

# set logger
logger = logging.getLogger('aliyundrive')
log_file = os.path.join(ROOT_DIR, 'debug-aliyundrive.log')
fmt_str = "%(asctime)s [%(filename)s:%(lineno)d] %(funcName)s %(levelname)s - %(message)s"
logging.basicConfig(level=logging.DEBUG,
                    filename=log_file,
                    filemode="a",
                    format=fmt_str,
                    datefmt="%Y-%m-%d %H:%M:%S")

# http requests
UA = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) ????/1.0.0 ' \
     'Chrome/69.0.3497.128 Electron/4.2.12 Safari/537.36 '

SIGN = {
    'method': 'GET',
    'url': 'https://www.aliyundrive.com/sign/in',
}

AUTHORIZE = {
    'method': 'GET',
    'url': 'https://auth.aliyundrive.com/v2/oauth/authorize',
    'params': {
        'client_id': 'client_id',
        'response_type': 'code',
        'login_type': 'custom',
    }
}

MINI_LOGIN = {
    'method': 'GET',
    'url': 'https://passport.aliyundrive.com/mini_login.htm',
    'params': {'appName': 'aliyun_drive'}
}

LOGIN = {
    'method': 'POST',
    'url': 'https://passport.aliyundrive.com/newlogin/login.do',
    'data': {
        'loginId': 'loginId',
        'password2': 'password2',
        'appName': 'aliyun_drive',
    }
}

TOKEN_LOGIN = {
    'method': 'POST',
    'url': 'https://auth.aliyundrive.com/v2/oauth/token_login',
    'data': {'token': 'biz_ext'}
}

TOKEN_GET = {
    'method': 'POST',
    'url': 'https://websv.aliyundrive.com/token/get',
    'data': {'code': 'code'}
}

QR_GEN = {
    'method': 'get',
    'url': 'https://passport.aliyundrive.com/newlogin/qrcode/generate.do',
    'params': {
        'appName': 'aliyun_drive',
    }
}

QR_QUERY = {
    'method': 'post',
    'url': 'https://passport.aliyundrive.com/newlogin/qrcode/query.do',
    'data': {
        't': 't',
    }
}

SMS_SEND = {
    'method': 'POST',
    'url': 'https://passport.aliyundrive.com/newlogin/sms/send.do',
    'params': {'appName': 'aliyun_drive'},
    'data': {
        'phoneCode': '86',
        'loginId': 'username',
        'countryCode': 'CN'
    }
}

SMS_LOGIN = {
    'method': 'POST',
    'url': 'https://passport.aliyundrive.com/newlogin/sms/login.do',
    'params': {'appName': 'aliyun_drive'},
    'data': {
        'phoneCode': '86',
        'loginId': 'username',
        'countryCode': 'CN',
        'smsCode': 'sms_code',
        'smsToken': 'sms_token'
    }
}


# base64
def b64decode(string):
    b = base64.b64decode(string)
    return bytes.decode(b, 'gbk')


# config save/read
def save_conf(user_info, configfile):
    config = configparser.ConfigParser()
    config['DEFAULT'] = user_info
    configfile = os.path.join(ROOT_DIR, configfile)
    with open(configfile, 'w') as f:
        config.write(f)


def read_conf(configfile):
    configfile = os.path.join(ROOT_DIR, configfile)
    config = configparser.ConfigParser()
    if os.path.exists(configfile):
        config.read(configfile)
        return config.defaults()
    else:
        user = {
                'username': '',
                'password': '',
        }
        return user


# RSA encrypt
PUBLIC_KEY = b'-----BEGIN PUBLIC KEY-----\n' \
            b'MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDTvO8fAEJPMmHIkyP6jN+hK7rE\n' \
            b'ANn+i7Yn6NJ6RL1dWdzlWRNdZ4qBQ761uNcFbE4ficTh8VJHBiW3tBlEqX8C2m9g\n' \
            b'WkmpPsbrnLry56wrJqNUzmnrJllT0sKeOV1tjBzbaIl4VRqg91IfKQA1+tOBF42g\n' \
            b'vqj55q3OOQIPUTEz+wIDAQAB\n' \
            b'-----END PUBLIC KEY-----'

MAP = "0123456789abcdefghijklmnopqrstuvwxyz"


def encrypt(password):
    rsa_result = rsa.encrypt(
        password.encode(),
        rsa.PublicKey.load_pkcs1_openssl_pem(PUBLIC_KEY)
    )
    ans = ''
    for byte in rsa_result:
        ans += MAP[byte >> 4]
        ans += MAP[byte & 0x0F]
    return ans

