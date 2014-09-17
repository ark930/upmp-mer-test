# coding: utf-8
import hashlib
import time
import urlparse
import urllib2
import os

from BaseChannel import BaseChannel
from UpmpConfig import UpmpConfig
from logger.logger import Logger


class UpmpChannel(BaseChannel):
    def __init__(self, mer_id, secret_key):
        self.mer_id = mer_id
        self.sk = secret_key
        self.sk_md5 = hashlib.md5(self.sk).hexdigest()
        self.log_path = ''

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
        req_dict['orderDescription'] = '一个小朋友'
        req_dict['orderAmount'] = amount

        sign_string = self.gen_sign_string(req_dict, ['signature', 'signMethod'])
        sign = hashlib.md5(sign_string + '&' + self.sk_md5).hexdigest()
        req = self.sort_dict(self.para_filter(req_dict))
        req['signature'] = sign
        req['signMethod'] = 'MD5'

        post_data = self.create_link_string(req)
        print('request --', post_data)

        if amount == 123:
            Logger.logging(os.getcwd(), 'sale.txt', post_data)

        res_dict = list()
        try:
            res = urllib2.urlopen(UpmpConfig.TRADE_URL, post_data)
            res_str = res.read().decode('UTF-8')

            print('response --', res_str)

            if amount == 123:
                Logger.logging(os.getcwd(), 'sale.txt', post_data)

            res_dict = urlparse.parse_qs(res_str)
            res_dict = {key: res_dict[key][0] for key in res_dict}
            sign_string = self.gen_sign_string(res_dict, ['signature', 'signMethod'])
            sign = hashlib.md5(sign_string + '&' + self.sk_md5).hexdigest()
            original_sign = res_dict['signature']

            if original_sign == sign:
                if res_dict['respCode'] == '00':
                    print('tn -- ', res_dict['tn'])
                else:
                    print('respCode =', res_dict['respCode'])
                    print('respMsg =', res_dict['respMsg'])
            else:
                print('Sign verify error')
        except urllib2.HTTPError, e:
            print(e.code)
        except urllib2.URLError, e:
            print(e.args)

        return req_dict, res_dict['tn']

    def charge_retrieve(self, order_no, order_time):
        self._retrieve(order_no, order_time, UpmpConfig.TRANS_TYPE_TRADE)

    def void_retrieve(self, order_no, order_time):
        self._retrieve(order_no, order_time, UpmpConfig.TRANS_TYPE_VOID)

    def refund_retrieve(self, order_no, order_time):
        self._retrieve(order_no, order_time, UpmpConfig.TRANS_TYPE_REFUND)

    def _retrieve(self, order_no, order_time, trans_type):
        req_dict = dict()
        req_dict['version'] = UpmpConfig.VERTION
        req_dict['charset'] = UpmpConfig.CHARSET
        req_dict['transType'] = trans_type
        req_dict['merId'] = self.mer_id
        req_dict['orderTime'] = order_time
        req_dict['orderNumber'] = order_no

        sign_string = self.gen_sign_string(req_dict, ['signature', 'signMethod'])
        sign = hashlib.md5(sign_string + '&' + self.sk_md5).hexdigest()
        req = self.sort_dict(self.para_filter(req_dict))
        req['signature'] = sign
        req['signMethod'] = 'MD5'

        # post_data = urllib.parse.urlencode(req)
        post_data = self.create_link_string(req)
        print('request --', post_data)

        log_file = None
        if trans_type == UpmpConfig.TRANS_TYPE_REFUND:
            log_file = 'refund_query.txt'
        elif trans_type == UpmpConfig.TRANS_TYPE_VOID:
            log_file = 'void_query.txt'
        elif trans_type == UpmpConfig.TRANS_TYPE_TRADE:
            log_file = 'sale_query.txt'
        if log_file:
            Logger.logging(os.getcwd(), log_file, post_data)

        res = urllib2.urlopen(UpmpConfig.QUERY_URL, post_data)
        try:
            res_str = res.read()
            print('response --', res_str)

            if log_file:
                Logger.logging(os.getcwd(), log_file, res_str)

            res_dict = urlparse.parse_qs(res_str)
            res_dict = {key: res_dict[key][0] for key in res_dict}
            sign_string = self.gen_sign_string(res_dict, ['signature', 'signMethod'])
            sign = hashlib.md5(sign_string + '&' + self.sk_md5).hexdigest()
            original_sign = res_dict['signature']

            if original_sign == sign:
                if res_dict['respCode'] == '00':
                    print('res_dict -- ', res_dict)
                    return True
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
        req_dict['orderDescription'] = '两个小朋友'
        req_dict['orderAmount'] = order_amount
        req_dict['qn'] = qn
        print(req_dict)

        sign_string = self.gen_sign_string(req_dict, ['signature', 'signMethod'])
        sign = hashlib.md5(sign_string + '&' + self.sk_md5).hexdigest()
        req = self.sort_dict(self.para_filter(req_dict))
        req['signature'] = sign
        req['signMethod'] = 'MD5'

        # post_data = urllib.parse.urlencode(req)
        post_data = self.create_link_string(req)
        print('request --', post_data)

        log_file = None
        if trans_type == UpmpConfig.TRANS_TYPE_REFUND:
            log_file = 'refund.txt'
        elif trans_type == UpmpConfig.TRANS_TYPE_VOID:
            log_file = 'void.txt'
        if log_file:
            Logger.logging(os.getcwd(), log_file, post_data)

        # res = urllib.request.urlopen(UpmpConfig.TRADE_URL, post_data.encode('UTF-8'))
        res = urllib2.urlopen(UpmpConfig.TRADE_URL, post_data)

        try:
            res_str = res.read()
            print('response --', res_str)

            if log_file:
                Logger.logging(os.getcwd(), log_file, res_str)

            res_dict = urlparse.parse_qs(res_str)
            res_dict = {key: res_dict[key][0] for key in res_dict}
            sign_string = self.gen_sign_string(res_dict, ['signature', 'signMethod'])
            sign = hashlib.md5(sign_string + '&' + self.sk_md5).hexdigest()
            original_sign = res_dict['signature']

            if original_sign == sign:
                if res_dict['respCode'] == '00':
                    print('res_dict -- ', res_dict)
                    return True
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
        notify_dict = urlparse.parse_qs(notify_data)
        notify_dict = {key: notify_dict[key][0] for key in notify_dict}
        trans_type = notify_dict['transType']
        settle_amount = notify_dict['settleAmount']

        sign_string = self.gen_sign_string(notify_dict, ['signature', 'signMethod'])
        sign = hashlib.md5(sign_string + '&' + self.sk_md5).hexdigest()
        original_sign = notify_dict['signature']

        if original_sign == sign:
            if notify_dict['respCode'] == '00' and notify_dict['transStatus'] == '00':

                log_file = None
                if trans_type == UpmpConfig.TRANS_TYPE_REFUND:
                    log_file = 'refund.txt'
                elif trans_type == UpmpConfig.TRANS_TYPE_VOID:
                    log_file = 'void.txt'
                elif trans_type == UpmpConfig.TRANS_TYPE_TRADE and settle_amount == '123':
                    log_file = 'sale.txt'

                if log_file:
                    Logger.logging(os.getcwd(), log_file, notify_data)

                return notify_dict

        return False


if __name__ == '__main__':
    mer_id = '880000000002457'
    secret_key = 'NAMAChvG1H43B00Aui8u7EOcX18MBbke'

    uc = UpmpChannel(mer_id, secret_key)
    uc.charge(123)
    notify_dict = uc.notify(
        'orderTime=20140917101934&settleDate=0916&orderNumber=afd4cbd40dc0&exchangeRate=0&signature=fd4901b1d99870604b4cc2ffc95eb7ab&settleCurrency=156&signMethod=MD5&transType=01&respCode=00&charset=UTF-8&sysReserved=%7BtraceTime%3D0917101934%26acqCode%3D00215800%26traceNumber%3D072753%7D&version=1.0.0&settleAmount=123&transStatus=00&merId=880000000002457&qn=201409171019340727537')

    if notify_dict:
        order_no = notify_dict['orderNumber']
        order_time = notify_dict['orderTime']
        settle_amount = notify_dict['settleAmount']
        order_amount = settle_amount
        trans_type = notify_dict['transType']
        qn = notify_dict['qn']
        print(order_no, order_time, settle_amount, trans_type, mer_id, qn)

        if trans_type == UpmpConfig.TRANS_TYPE_TRADE:
            if settle_amount == '123':    # refund
                uc.charge_retrieve(order_no, order_time)
                uc.refund(order_time, qn)
