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

from database.sqlite import Sqlite

root_path = "data"

class UpmpHandler:
    @staticmethod
    def charge(json_data):
        if 'id' in json_data.keys():
            mer_id = json_data['id']
        else:
            raise InvalidMerchantException

        amount = json_data['amount'] if 'amount' in json_data.keys() else 123

        # 根据mer_id获取商户数据
        db = Sqlite()
        merchant = db.get_upmp_data_by_merid(mer_id)

        if not merchant:
            # 更新商户数据库
            repo = RepoGit("../data/")
            repo.pull()
            mer_name, mer_key = UpmpHandler.get_merchant_info_by_merid("data/2014/", mer_id)
            db.set_upmp_basic_info(mer_name, mer_id, mer_key)
            merchant = db.get_upmp_data_by_merid(mer_id)

        if not merchant or not merchant['sk']:
            raise InvalidMerchantException

        # 交易请求
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

        # 如果金额为123,则记录数据
        if int(amount) == 123:
            db.set_upmp_charge_data(mer_id, post_data, res_data)

        return res

    @staticmethod
    def notify(data):
        notify_data = data
        notify_dict = urlparse.parse_qs(data)
        notify_dict = {key: notify_dict[key][0] for key in notify_dict}
        mer_id = notify_dict['merId']

        db = Sqlite()
        merchant = db.get_upmp_data_by_merid(mer_id)

        if not merchant or not merchant['sk']:
            raise InvalidMerchantException

        mer_key = merchant['sk']
        uc = UpmpChannel(mer_id, mer_key)
        notify_dict = uc.notify(notify_data)
        UpmpHandler.to_log(notify_data, notify_dict, mer_id, uc)

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
    def get_merchant_info_by_merid(path, mer_id):
        """
        获取指定的未测试商户的商户信息
        :param path:
        :return: 指定的未测试商户的商户信息
        """
        print os.path.join(path, mer_id + '.txt')
        with open(os.path.join(path, mer_id + '.txt')) as f:
            lines = f.readlines()

        if len(lines) == 2:
            mer_name, mer_key = lines[0].strip(), lines[1].strip()
            return mer_name, mer_key
        else:
            return None

    @staticmethod
    def to_log(notify_data, notify_dict, mer_id, uc):
        print notify_dict
        order_no = notify_dict['orderNumber']
        order_time = notify_dict['orderTime']
        settle_amount = notify_dict['settleAmount']
        order_amount = settle_amount
        trans_type = notify_dict['transType']
        qn = notify_dict['qn']
        print(order_no, order_time, settle_amount, trans_type, mer_id, qn)

        # 如果金额不正确或者商户号不存，则立即返回
        db = Sqlite()
        merchant = db.get_upmp_data_by_merid(mer_id)
        if int(order_amount) not in [1, 123, 321] or not merchant:
            return

        if trans_type == UpmpConfig.TRANS_TYPE_TRADE:
            if int(settle_amount) == 123:
                db.set_upmp_charge_notify_data(notify_data)

        if trans_type == UpmpConfig.TRANS_TYPE_TRADE:
            if int(settle_amount) == 123:  # refund
                post_data, res_data = uc.charge_retrieve(order_no, order_time)
                db.set_upmp_charge_query_data(mer_id, post_data, res_data)

                post_data, res_data, req_dict, res_dict = uc.refund(order_time, qn)
                db.set_upmp_refund_data(mer_id, post_data, res_data)
            elif int(settle_amount) == 321:  # void
                post_data, res_data, req_dict, res_dict = uc.void(order_time, order_amount, qn)
                db.set_upmp_void_data(mer_id, post_data, res_data)
        elif trans_type == UpmpConfig.TRANS_TYPE_VOID:
            if int(settle_amount) == 321:  # void retrieve
                post_data, res_data = uc.void_retrieve(order_no, order_time)
                db.set_upmp_void_query_data(mer_id, post_data, res_data)
        elif trans_type == UpmpConfig.TRANS_TYPE_REFUND:
            if int(settle_amount) == 1:  # refund retrieve
                post_data, res_data = uc.refund_retrieve(order_no, order_time)
                db.set_upmp_refund_query_data(mer_id, post_data, res_data)

                # if sc.is_merchant_test_done(log_dir):
                if db.is_upmp_data_complete(mer_id):
                    print('=========TO EXCEL========')
                    from util.excel_handler import ExcelHandler
                    eh = ExcelHandler()
                    # report_file = os.path.join(merchant['path'], merchant['id'] + '.xlsx')
                    report_file = merchant['id'] + '.xlsx'
                    eh.save('./data/template.xlsx', report_file, log_dir)
                    # print('=========GIT PUSH========')
                    # gm = RepoGit(root_path)
                    # git_report_file = report_file[len(root_path) + 1:]
                    # git_log_dir = log_dir[len(root_path) + 1:]
                    # gm.add(git_report_file)
                    # gm.add(os.path.join(git_log_dir, '*'))
                    # gm.commit("Merchant " + merchant['id'] + ' test finished')
                    # gm.push()
                    # print('========SEND MAIL========')
                    # from util import mail
                    # mail.send_email()
                    # print('========REMOVE DATA=======')
                    # sc.remove_merchant_info_by_mer_id(mer_id)
                    print('========TEST DONE========')
                else:
                    print('========CONTINUE=========')


if __name__ == "__main__":
    root_path = "../data/2014"
    print UpmpHandler.get_merchant_info_by_merid(root_path, '880000000002457')

    # try:
    #     UpmpHandler.query_merchant_info('/api/v1/merchanqt', root_path)
    # except InvalidUrlException:
    #     print 'exception'
    #     pass