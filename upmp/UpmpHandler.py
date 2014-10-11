# coding: utf-8

import re
import os
import urlparse

from util.repo_git import RepoGit
from util.server_check import ServerCheck
from exception.NetException import *
from exception.UpmpException import *

from UpmpChannel import UpmpChannel
from UpmpConfig import UpmpConfig
from util.logger import Logger

root_path = "data/upmp-mer-files"

class UpmpHandler:
    @staticmethod
    def charge(json_data):
        if 'id' in json_data.keys():
            mer_id = json_data['id']
        else:
            raise InvalidMerchantException

        amount = json_data['amount'] if 'amount' in json_data.keys() else 123

        sc = ServerCheck()
        if not os.path.isfile(sc.untest_merchant_txt_path):
            sc.get_all_untest_merchant_json(root_path)

        merchant = sc.get_merchant_info_by_mer_id(mer_id)
        if not merchant or not merchant['sk']:
            raise InvalidMerchantException

        mer_key = merchant['sk']
        uc = UpmpChannel(mer_id, mer_key)
        ret = uc.charge(amount)

        if not ret:
            raise ChargeFailException

        print(ret)
        post_data, res_data, req_dict, res_dict = ret

        res = dict()
        res['upmp'] = dict()
        res['upmp']['tn'] = res_dict['tn']
        res['upmp']['mode'] = '01'

        # res['credential'] = dict()
        # res['credential']['upmp'] = dict()
        # res['credential']['upmp']['tn'] = res_dict['tn']
        # res['credential']['upmp']['mode'] = '01'

        # 如果金额为123并且商户号存在于untest_merchant.txt中, 将数据记录到charge.txt中
        if int(amount) == 123 and sc.get_merchant_info_by_mer_id(mer_id):
            log_dir = os.path.join(merchant['path'], 'log')
            Logger.logging(log_dir, 'charge.txt', post_data)
            Logger.logging(log_dir, 'charge.txt', res_data)

        return res

    @staticmethod
    def notify(data):
        notify_data = data
        notify_dict = urlparse.parse_qs(data)
        notify_dict = {key: notify_dict[key][0] for key in notify_dict}
        mer_id = notify_dict['merId']

        sc = ServerCheck()
        if not os.path.isfile(sc.untest_merchant_txt_path):
            sc.get_all_untest_merchant_json(root_path)

        merchant = sc.get_merchant_info_by_mer_id(mer_id)

        if not merchant or not merchant['sk']:
            raise InvalidMerchantException

        mer_key = merchant['sk']
        uc = UpmpChannel(mer_id, mer_key)
        notify_dict = uc.notify(notify_data)
        print '============'
        UpmpHandler.to_log(notify_data, notify_dict, mer_id, merchant, uc)

        return

    @staticmethod
    def query_merchant_info(data_path):
        """
        查询商户信息
        :return:
        """
        # 更新商户数据库
        rg = RepoGit(data_path)
        rg.pull()
        sc = ServerCheck()
        return sc.get_all_untest_merchant_json(data_path)

    @staticmethod
    def to_log(notify_data, notify_dict, mer_id, merchant, uc):
        print notify_dict
        order_no = notify_dict['orderNumber']
        order_time = notify_dict['orderTime']
        settle_amount = notify_dict['settleAmount']
        order_amount = settle_amount
        trans_type = notify_dict['transType']
        qn = notify_dict['qn']
        print(order_no, order_time, settle_amount, trans_type, mer_id, qn)

        # 如果金额不正确或者商户号不存在于untest_merchant.txt中，则立即返回
        sc = ServerCheck()
        if int(order_amount) not in [1, 123, 321] or not sc.get_merchant_info_by_mer_id(mer_id):
            return

        log_dir = os.path.join(merchant['path'], 'log')
        log_file = UpmpConfig.sale_type_file[trans_type]
        if log_file == UpmpConfig.TRANS_TYPE_TRADE:
            if int(settle_amount) == 123:
                Logger.logging(log_dir, log_file, notify_data)
        elif log_file:
            Logger.logging(log_dir, log_file, notify_data)

        if trans_type == UpmpConfig.TRANS_TYPE_TRADE:
            if int(settle_amount) == 123:  # refund
                post_data, res_data = uc.charge_retrieve(order_no, order_time)
                log_file = UpmpConfig.query_type_file[trans_type]
                Logger.logging(log_dir, log_file, post_data)
                Logger.logging(log_dir, log_file, res_data)
                print(order_time, qn)
                post_data, res_data, req_dict, res_dict = uc.refund(order_time, qn)
                log_file = UpmpConfig.sale_type_file[UpmpConfig.TRANS_TYPE_REFUND]
                Logger.logging(log_dir, log_file, post_data)
                Logger.logging(log_dir, log_file, res_data)
            elif int(settle_amount) == 321:  # void
                post_data, res_data, req_dict, res_dict = uc.void(order_time, order_amount, qn)
                log_file = UpmpConfig.sale_type_file[UpmpConfig.TRANS_TYPE_VOID]
                Logger.logging(log_dir, log_file, post_data)
                Logger.logging(log_dir, log_file, res_data)
        elif trans_type == UpmpConfig.TRANS_TYPE_VOID:
            if int(settle_amount) == 321:  # void retrieve
                post_data, res_data = uc.void_retrieve(order_no, order_time)
                log_file = UpmpConfig.query_type_file[trans_type]
                Logger.logging(log_dir, log_file, post_data)
                Logger.logging(log_dir, log_file, res_data)
        elif trans_type == UpmpConfig.TRANS_TYPE_REFUND:
            if int(settle_amount) == 1:  # refund retrieve
                post_data, res_data = uc.refund_retrieve(order_no, order_time)
                log_file = UpmpConfig.query_type_file[trans_type]
                Logger.logging(log_dir, log_file, post_data)
                Logger.logging(log_dir, log_file, res_data)

                if sc.is_merchant_test_done(log_dir):
                    print('=========TO EXCEL========')
                    from util.excel_handler import ExcelHandler

                    eh = ExcelHandler()
                    report_file = os.path.join(merchant['path'], merchant['id'] + '.xlsx')
                    eh.save('./data/template.xlsx', report_file, log_dir)
                    print('=========GIT PUSH========')
                    gm = RepoGit(root_path)
                    git_report_file = report_file[len(root_path) + 1:]
                    git_log_dir = log_dir[len(root_path) + 1:]
                    gm.add(git_report_file)
                    gm.add(os.path.join(git_log_dir, '*'))
                    gm.commit("Merchant " + merchant['id'] + ' test finished')
                    gm.push()
                    # print('========SEND MAIL========')
                    # from util import mail
                    # mail.send_email()
                    print('========REMOVE DATA=======')
                    sc.remove_merchant_info_by_mer_id(mer_id)
                    print('========TEST DONE========')
                else:
                    print('========CONTINUE=========')


if __name__ == "__main__":
    root_path = "../data/upmp-mer-files"

    try:
        UpmpHandler.query_merchant_info('/api/v1/merchanqt', root_path)
    except InvalidUrlException:
        print 'exception'
        pass