# coding: utf-8
import hashlib
import time
import urlparse
import urllib2

from BaseChannel import BaseChannel
from UpmpConfig import UpmpConfig
from exception.UpmpException import InvalidNotifyException


class UpmpChannel(BaseChannel):
    def __init__(self, mer_id, secret_key):
        self.mer_id = mer_id
        self.sk = secret_key
        self.sk_md5 = hashlib.md5(self.sk).hexdigest()
        self.log_path = ''

    def _verify_sign(self, data_dict):
        sign = self._gen_sign(data_dict)
        original_sign = data_dict['signature']

        return original_sign == sign

    def _gen_sign(self, data_dict):
        sign_string = self._gen_sign_string(data_dict, ['signature', 'signMethod'])
        sign = hashlib.md5(sign_string + '&' + self.sk_md5).hexdigest()

        return sign

    def _get_post_data(self, data_dict):
        req = self.sort_dict(self.para_filter(data_dict))
        req['signature'] = self._gen_sign(data_dict)
        req['signMethod'] = UpmpConfig.SIGN_METHOD

        return self.create_link_string(req)
        # return urllib.urlencode(req)

    def _query_string_to_dict(self, qs):
        qs_dict = urlparse.parse_qs(qs)
        return {key: qs_dict[key][0] for key in qs_dict}

    def charge(self, amount):
        req_dict = dict()
        req_dict['version'] = UpmpConfig.VERTION
        req_dict['charset'] = UpmpConfig.CHARSET
        req_dict['transType'] = UpmpConfig.TRANS_TYPE_TRADE
        req_dict['merId'] = self.mer_id
        req_dict['orderCurrency'] = UpmpConfig.CURRENCY_TYPE
        req_dict['backEndUrl'] = UpmpConfig.NOTIFY_URL
        req_dict['orderTime'] = time.strftime("%Y%m%d%H%M%S", time.localtime(int(time.time())))
        # receive_req['orderTimeout'] = int(receive_req['orderTime']) + 10000
        req_dict['orderNumber'] = self.random_id(12)
        req_dict['orderDescription'] = 'a little boy'
        req_dict['orderAmount'] = amount

        post_data = self._get_post_data(req_dict)
        print('request --', post_data)

        try:
            res = urllib2.urlopen(UpmpConfig.TRADE_URL, post_data)
            res_data = res.read()
            print('response --', res_data)

            res_dict = self._query_string_to_dict(res_data)

            if self._verify_sign(res_dict):
                if res_dict['respCode'] == '00':
                    return post_data, res_data, req_dict, res_dict
                else:
                    print('respCode =', res_dict['respCode'])
                    print('respMsg =', res_dict['respMsg'])
            else:
                print('Sign verify error')
        except urllib2.HTTPError, e:
            print(e.code)
        except urllib2.URLError, e:
            print(e.args)

        return False

    def charge_retrieve(self, order_no, order_time):
        return self._retrieve(order_no, order_time, UpmpConfig.TRANS_TYPE_TRADE)

    def void_retrieve(self, order_no, order_time):
        return self._retrieve(order_no, order_time, UpmpConfig.TRANS_TYPE_VOID)

    def refund_retrieve(self, order_no, order_time):
        return self._retrieve(order_no, order_time, UpmpConfig.TRANS_TYPE_REFUND)

    def _retrieve(self, order_no, order_time, trans_type):
        req_dict = dict()
        req_dict['version'] = UpmpConfig.VERTION
        req_dict['charset'] = UpmpConfig.CHARSET
        req_dict['transType'] = trans_type
        req_dict['merId'] = self.mer_id
        req_dict['orderTime'] = order_time
        req_dict['orderNumber'] = order_no

        post_data = self._get_post_data(req_dict)
        print('request --', post_data)

        res = urllib2.urlopen(UpmpConfig.QUERY_URL, post_data)
        try:
            res_data = res.read()
            print('response ree--', res_data)

            res_dict = self._query_string_to_dict(res_data)

            if self._verify_sign(res_dict):
                if res_dict['respCode'] == '00':
                    return post_data, res_data
                else:
                    print('respCode =', res_dict['respCode'])
                    print('respMsg =', res_dict['respMsg'])
            else:
                print('Sign verify error')
        except urllib2.HTTPError, e:
            print(e.code)
        except urllib2.URLError, e:
            print(e.args)

        return False

    def void(self, order_time, order_amount, qn):
        return self._refund(order_time, order_amount, qn, UpmpConfig.TRANS_TYPE_VOID)

    def refund(self, order_time, qn):
        return self._refund(order_time, 1, qn, UpmpConfig.TRANS_TYPE_REFUND)

    def _refund(self, order_time, order_amount, qn, trans_type):
        req_dict = dict()
        req_dict['version'] = UpmpConfig.VERTION
        req_dict['charset'] = UpmpConfig.CHARSET
        req_dict['transType'] = trans_type
        req_dict['merId'] = self.mer_id
        req_dict['orderCurrency'] = UpmpConfig.CURRENCY_TYPE
        req_dict['backEndUrl'] = UpmpConfig.NOTIFY_URL
        req_dict['orderTime'] = order_time
        req_dict['orderNumber'] = self.random_id(12)
        req_dict['orderDescription'] = 'tow little boys'
        req_dict['orderAmount'] = order_amount
        req_dict['qn'] = qn
        print(req_dict)

        post_data = self._get_post_data(req_dict)
        print('request --', post_data)

        res = urllib2.urlopen(UpmpConfig.TRADE_URL, post_data)
        try:
            res_data = res.read()
            print('response --', res_data)

            res_dict = self._query_string_to_dict(res_data)

            if self._verify_sign(res_dict):
                if res_dict['respCode'] == '00':
                    return post_data, res_data, req_dict, res_dict
                else:
                    print('respCode =', res_dict['respCode'])
                    print('respMsg =', res_dict['respMsg'])
            else:
                print('Sign verify error')

        except urllib2.HTTPError, e:
            print(e.code)
        except urllib2.URLError, e:
            print(e.args)

        return False

    def notify(self, notify_data):
        notify_dict = self._query_string_to_dict(notify_data)
        if self._verify_sign(notify_dict):
            if notify_dict['respCode'] == '00' and notify_dict['transStatus'] == '00':
                return notify_dict

        raise InvalidNotifyException


if __name__ == '__main__':
    mer_id = '880000000002457'
    secret_key = 'NAMAChvG1H43B00Aui8u7EOcX18MBbke'

    uc = UpmpChannel(mer_id, secret_key)
    uc.charge(123)
    notify_dict = uc.notify(
        'orderTime=20140918172157&settleDate=0918&orderNumber=VxGwEmM0lgC6&exchangeRate=0&signature=410a5e8d36dc7f6ce40a0f9a529f07ab&settleCurrency=156&signMethod=MD5&transType=01&respCode=00&charset=UTF-8&sysReserved=%7BtraceTime%3D0918172157%26acqCode%3D00215800%26traceNumber%3D090672%7D&version=1.0.0&settleAmount=123&transStatus=00&merId=880000000002457&qn=201409181721570906727'
    )
    if notify_dict:
        order_no = notify_dict['orderNumber']
        order_time = notify_dict['orderTime']
        settle_amount = notify_dict['settleAmount']
        order_amount = settle_amount
        trans_type = notify_dict['transType']
        qn = notify_dict['qn']
        print(order_no, order_time, settle_amount, trans_type, mer_id, qn)

        if trans_type == UpmpConfig.TRANS_TYPE_TRADE:
            if settle_amount == '123':  # refund
                uc.charge_retrieve(order_no, order_time)
                uc.refund(order_time, qn)
