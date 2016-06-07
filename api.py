# coding=utf8
import httplib
import urllib
import hashlib
from Crypto.Cipher import AES
import threading
import time as t
import random
import re
import os

import var as v
import common as c


def getWebLoginNonce():
    """
    type : Client 的类型，0[web] 1[Android] 2[iOS] 3[Mac] 4[PC]
    deviceId : 设备的唯一标识，不能包含字符"_"，web可以传当前mac地址，其它Client端可自行定义
    time : 当前时间，按秒计算
    random : 随机数，没有位数限制
    for example
    nonce:0_08:9e:01:d0:f1:f4_1449649511_9171
    """
    timeNum = int(t.time())
    randomNum = random.randint(1, 9999)
    macStr = 'peanutsclient'
    nonce = '0_' + macStr + '_' + str(timeNum) + '_' + str(randomNum)
    return nonce


def getWebLoginPassword(password=v.WEB_PWD, key=v.WEB_KEY):
    """
    password = sha1(nonce+sha1(pwd+key))
    """
    result = dict()
    nonce = getWebLoginNonce()
    password = str(hashlib.sha1(nonce + str(hashlib.sha1(password + key).hexdigest())).hexdigest())
    result['nonce'] = nonce
    result['password'] = password
    return result


def getWebLoginOldPwd():
    result = dict()
    nonce = getWebLoginNonce()
    oldPwd = str(hashlib.sha1(nonce + v.ACCOUNT_DEFAULT_PWD).hexdigest())
    result['nonce'] = nonce
    result['password'] = oldPwd
    return result


def getWebLoginNewPwdEncryptBase64(password=v.WEB_PWD, key=v.WEB_KEY):

    # AES加密密钥是oldpwdnononce
    oldPwdNoNonce = v.ACCOUNT_DEFAULT_PWD
    aesKey = oldPwdNoNonce.decode('hex')
    # aes-cbc-128 的key 16bytes
    aesKey = aesKey[0:16]
    iv = v.IV.decode('hex')
    newPwdNoNonce = str(hashlib.sha1(password + key).hexdigest())
    text = newPwdNoNonce
    text = PKCSPad(text)

    encryptor = AES.new(aesKey, AES.MODE_CBC, iv)
    cipher = encryptor.encrypt(text)
    cipherbase = cipher.encode('base64')
    return cipherbase


def PKCSPad(data):
    """
    PKCS#5 padding is identical to PKCS#7 padding, except that
    it has only been defined for block ciphers that use a 64 bit (8 byte)
    block size.
    But in AES, there is no block of 8 bit, so PKCS#5 is PKCS#7.
    """
    BS = AES.block_size
    data =  data + (BS - len(data) % BS) * chr(BS - len(data) % BS)
    return data


def PKCSUnpad(data):
    data = data[0:-ord(data[-1])]
    return data


class HttpClient(object):
    def __init__(self):
        self.init = None
        self.token = None
        self.hostname = None
        self.httpClient = None
        self.headers = {"Content-type": "application/x-www-form-urlencoded",
                        "Accept": "text/plain",
                        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.106 Safari/537.36"
                        }

    def connect(self, init=0, host=v.HOST, port=80, password=v.WEB_PWD):
        self.init = init
        self.token = False
        self.hostname = host

        def connectInLoop(host, password):
            loop2 = 0
            try:
                self.httpClient = httplib.HTTPConnection(host, port, timeout=30)
                while self.token is False and loop2 < 1:
                    t.sleep(5)
                    result = self.getToken(password=password)
                    loop2 += 1
                if result is False:
                    return False
                else:
                    return True
            except:
                print 'http connection is failed. please check your network.'
                return False

        loop = 0
        ret = connectInLoop(host, password)
        while ret is False and loop < 0:
            loop += 1
            t.sleep(5)
            ret = connectInLoop(host, password)
        return ret

    def close(self):
        if self.httpClient:
            self.httpClient.close()

    def getToken(self, password):
        self.password = password
        if self.init is 0:
            self.login = getWebLoginPassword(self.password, v.WEB_KEY)
        elif self.init is 1:
            self.login = getWebLoginOldPwd()
        params = urllib.urlencode({'username': v.WEB_USERNAME,
                                   'password': self.login['password'],
                                   'init': self.init,
                                   'nonce': self.login['nonce']})

        self.httpClient.request('POST', '/cgi-bin/luci/api/xqsystem/login', params, self.headers)
        response = self.httpClient.getresponse()
        if response.status is not 200:
            print 'web server has problem'
            return False
        else:
            loginresponse = eval(response.read())
            if loginresponse['code'] is not 0:
                print 'probably use wrong web password or router hasnot been initialized.'
                return False
            self.token = 'stok=' + loginresponse['token']
            return self.token

    def getApi(self, path, **kwargs):
        try:
            apipath = re.sub('stok=token', self.token, path)
        except:
            self.getToken(password=v.WEB_PWD)
        if len(kwargs) is 0:
            self.httpClient.request('GET', apipath, headers=self.headers)
            response = self.httpClient.getresponse().read()
            responseDict = eval(response)
            return responseDict
        else:
            for key, value in kwargs.items():
                if type(value) is str and c.checkContainChinese(value):
                    kwargs[key] = value.decode('utf8').encode('utf8')
            params = urllib.urlencode(kwargs)
            self.httpClient.request('POST', apipath, params, self.headers)
            response = self.httpClient.getresponse().read()
            responseDict = eval(response)
            return responseDict


def setGet(terminal, apipath, **kwargs):

    if not os.path.exists(v.LOG_PATH):
        os.makedirs(v.LOG_PATH)

    def setGetInLoop(terminal, apipath, **kwargs):
        try:
            curTime = t.strftime('%Y.%m.%d %H:%M:%S', t.localtime())
            ret = terminal.getApi(apipath, **kwargs)
            f = open(v.LOG_PATH + v.LOG_NAME, 'a')
            f.write(curTime + '~#API request to ' + terminal.hostname + '#')
            f.write(apipath + '?' + str(kwargs) + '\n')
            f.writelines(str(ret))
            f.write('\n\n')
            if ret['code'] == 401:
                f.write('token timeout, renew token.\n\n')
                f.close()
                terminal.getToken(password=v.WEB_PWD)
                setGet(terminal, apipath, **kwargs)
            f.close()
            return ret
        except Exception, e:
            curTime = t.strftime('%Y.%m.%d %H:%M:%S', t.localtime())
            f = open(v.LOG_PATH + v.LOG_NAME, 'a')
            f.write(curTime + '~#API request to ' + terminal.hostname + ' failed#')
            f.write(apipath + '?' + str(kwargs) + '\n')
            f.write(str(e))
            f.write('\n\n')
            terminal.close()
            f.close()
            return None

    loop = 0
    ret = setGetInLoop(terminal, apipath, **kwargs)
    while (ret is None or ret['code'] != 0) and loop < 1:
        loop += 1
        t.sleep(10)
        ret = setGetInLoop(terminal, apipath, **kwargs)

    return ret


def setCheck(terminal, apipath, **kwargs):
    if not os.path.exists(v.LOG_PATH):
        os.makedirs(v.LOG_PATH)

    def setCheckInLoop(terminal, apipath, **kwargs):
        try:
            curTime = t.strftime('%Y.%m.%d %H:%M:%S', t.localtime())
            ret = terminal.getApi(apipath, **kwargs)
            f = open(v.LOG_PATH + v.LOG_NAME, 'a')
            f.write(curTime + '~#API request to ' + terminal.hostname + '#')
            f.write(apipath + '?' + str(kwargs) + '\n')
            f.writelines(str(ret))
            f.write('\n')
            if ret['code'] == 0:
                f.write('api processes PASS.\n\n')
                f.close()
                return True
            elif ret['code'] == 401:
                f.write('token timeout, renew token.\n\n')
                f.close()
                terminal.getToken(password=v.WEB_PWD)
                setCheck(terminal, apipath, **kwargs)
            else:
                f.write('api processes FAIL.\n\n')
                f.close()
                return False

        except Exception, e:
            curTime = t.strftime('%Y.%m.%d %H:%M:%S', t.localtime())
            f = open(v.LOG_PATH + v.LOG_NAME, 'a')
            f.write(curTime + '~#API request to ' + terminal.hostname + ' failed#')
            f.write(apipath + '?' + str(kwargs) + '\n')
            f.write(str(e))
            f.write('\n\n')
            terminal.close()
            f.close()
            return False

    loop = 0
    ret = setCheckInLoop(terminal, apipath, **kwargs)
    while ret is False and loop < 1:
        loop += 1
        t.sleep(10)
        ret = setCheckInLoop(terminal, apipath, **kwargs)

    return ret


def setRouterNormal(terminal, **kwargs):
    """
    name 路由器名
    locale 路由器地点
    nonce 加密用
    newPwd 新管理密码
    oldPwd 旧管理密码
    ssid wifi ssid
    encryption (none,mixed-psk,psk2)
    password wifi 密码
    txpwr 1 穿墙
    :param terminal:
    :param kwargs:
    :return:
    """
    # old = getWebLoginOldPwd()
    # new = getWebLoginNewPwdEncryptBase64()
    t.sleep(1)  # wait 1 sec for nonce check, new nonce > old nonce
    old = getWebLoginOldPwd()
    new = getWebLoginNewPwdEncryptBase64()
    option = {
        'name': 'coconuts',
        'locale': 'company',
        'ssid': 'coconuts',
        'encryption': 'mixed-psk',
        'password': '12345678',
        'nonce': old['nonce'],
        'newPwd': new,
        'oldPwd': old['password'],
        'txpwr': 1,
    }
    option.update(kwargs)
    api = '/cgi-bin/luci/;stok=token/api/misystem/set_router_normal'
    result = setCheck(terminal, api, **option)
    return result


def setWan(terminal, **kwargs):
    """
    wanType (pppoe/dhcp)
    pppoeName (pppoe 账号)
    pppoePwd (pppoe 密码)
    service (pppoe的服务名，可以选择使用，一般情况下不会去设置)
    :param terminal:
    :param kwargs:
    :return:
    """
    option = {
        'wanType': 'pppoe',
        'pppoeName': '',
        'pppoePwd': '',
    }
    option.update(kwargs)
    api = '/cgi-bin/luci/;stok=token/api/xqnetwork/set_wan'
    return setCheck(terminal, api, **option)


def getWifiStatus(terminal):
    """
    {'status': [{'ssid': 'peanuts', 'up': 0}, {'ssid': 'peanuts_automatic_test_suite-5G', 'up': 0}], 'code': 0}
    :param terminal:
    :return:
    """
    api = '/cgi-bin/luci/;stok=token/api/xqnetwork/wifi_status'
    ret = setGet(terminal, api)
    if ret is not None:
        return ret
    return None


def getPPPOEStatus(terminal):
    """
    {"gw":"","dns":[],"code":0,"pppoename":"pppoe","peerdns":"","ip":{"mask":"","address":""},"password":"pppoe","status":1,"proto":"pppoe"}
    :param terminal:
    :return:
    """
    api = '/cgi-bin/luci/;stok=token/api/misystem/pppoe_status'
    ret = setGet(terminal, api)
    return ret