# coding=utf-8

from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
from SocketServer import ThreadingMixIn
import threading
import re
import cgi
import json
import urlparse
import os

from upmp.UpmpChannel import UpmpChannel
from upmp.UpmpConfig import UpmpConfig
from server_check import ServerCheck
from logger.logger import Logger
from repo.repo_git import RepoGit


class HTTPRequestHandler(BaseHTTPRequestHandler):
    root_path = "./data/upmp-mer-files"

    def do_POST(self):

        length = int(self.headers.getheader('content-length'))
        data = self.rfile.read(length)
        if None != re.search('/api/v1/charge', self.path):
            ctype, _ = cgi.parse_header(self.headers.getheader('content-type'))
            if ctype == 'application/json':
                json_data = json.loads(data) if data else {}

                mer_id = json_data['id'] if 'id' in json_data.keys() else '880000000002457'
                amount = json_data['amount'] if 'amount' in json_data.keys() else 123

                sc = ServerCheck()
                merchant = sc.get_merchant_info_from_log(mer_id)
                mer_key = merchant['sk']
                if mer_key:
                    uc = UpmpChannel(mer_id, mer_key)
                    ret = uc.charge(amount)
                    print(ret)
                    if ret:
                        post_data, res_data, req_dict, res_dict = ret

                        res = dict()
                        res['upmp'] = dict()
                        res['upmp']['tn'] = res_dict['tn']
                        res['upmp']['mode'] = '01'

                        # res['credential'] = dict()
                        # res['credential']['upmp'] = dict()
                        # res['credential']['upmp']['tn'] = res_dict['tn']
                        # res['credential']['upmp']['mode'] = '01'

                        if int(amount) == 123:
                            log_dir = os.path.join(merchant['path'], 'log')
                            Logger.logging(log_dir, 'charge.txt', post_data)
                            Logger.logging(log_dir, 'charge.txt', res_data)

                        self.send_response(200)
                        self.send_header('Content-Type', 'application/json')
                        self.end_headers()
                        self.wfile.write(json.dumps(res))
                    else:
                        self.send_response(400, 'Bad Request: charge fail')
                        self.send_header('Content-Type', 'application/json')
                        self.end_headers()
                else:
                    self.send_response(400, 'Bad Request: id not exist')
                    self.send_header('Content-Type', 'application/json')
                    self.end_headers()
            else:
                self.send_response(400, 'Bad Request: Content-Type not invalid')
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
        elif None != re.search('api/v1/notify', self.path):
            print(data)
            notify_data = data
            notify_dict = urlparse.parse_qs(data)
            notify_dict = {key: notify_dict[key][0] for key in notify_dict}
            mer_id = notify_dict['merId']

            sc = ServerCheck()
            merchant = sc.get_merchant_info_from_log(mer_id)
            print(merchant)

            if merchant:
                mer_key = merchant['sk']
                uc = UpmpChannel(mer_id, mer_key)
                notify_dict = uc.notify(notify_data)

                if notify_dict:
                    order_no = notify_dict['orderNumber']
                    order_time = notify_dict['orderTime']
                    settle_amount = notify_dict['settleAmount']
                    order_amount = settle_amount
                    trans_type = notify_dict['transType']
                    qn = notify_dict['qn']
                    print(order_no, order_time, settle_amount, trans_type, mer_id, qn)

                    log_dir = os.path.join(merchant['path'], 'log')
                    log_file = UpmpConfig.sale_type_file[trans_type]
                    if log_file == UpmpConfig.TRANS_TYPE_TRADE:
                        if int(settle_amount) == 123:
                            Logger.logging(log_dir, log_file, notify_data)
                    elif log_file:
                        Logger.logging(log_dir, log_file, notify_data)

                    self.send_response(200)
                    self.send_header('Content-Type', 'text/html')
                    self.end_headers()
                    self.wfile.write('success')

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
                        if int(settle_amount) == 321:  # refund
                            post_data, res_data = uc.void_retrieve(order_no, order_time)
                            log_file = UpmpConfig.query_type_file[trans_type]
                            Logger.logging(log_dir, log_file, post_data)
                            Logger.logging(log_dir, log_file, res_data)
                    elif trans_type == UpmpConfig.TRANS_TYPE_REFUND:
                        if int(settle_amount) == 1:   # void
                            post_data, res_data = uc.refund_retrieve(order_no, order_time)
                            log_file = UpmpConfig.query_type_file[trans_type]
                            Logger.logging(log_dir, log_file, post_data)
                            Logger.logging(log_dir, log_file, res_data)

                    if sc.is_merchant_test_done(log_dir):
                        print('========TEST DONE========')
                        print('=========TO EXCEL========')
                        from excel.excel_handler import ExcelHandler
                        eh = ExcelHandler()
                        report_file = os.path.join(merchant['path'], merchant['id'] + '.xlsx')
                        eh.save('./data/template.xlsx', report_file, log_dir)
                        print('=========GIT PUSH========')
                        gm = RepoGit('./data/upmp-mer-files')
                        gm.add(report_file)
                        gm.add(os.path.join(log_dir, '*'))
                        gm.commit("Merchant " + merchant['id'] + ' test finished')
                        print('========SEND MAIL========')
                        # from util import mail
                        # mail.send_email()
                    else:
                        print('========CONTINUE========')
                else:
                    self.send_response(400, 'Bad Request: notify fail')
                    self.send_header('Content-Type', 'application/json')
                    self.end_headers()
            else:
                self.send_response(400, 'Bad Request: merchant not exist')
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
        else:
            self.send_response(403)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()

        return

    def do_GET(self):
        if None != re.search('/api/v1/merchant', self.path):
            sc = ServerCheck()
            data = sc.get_all_untest_merchant_json(self.root_path)
            print(data)

            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(data))
        else:
            self.send_response(403)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()

        return


class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    allow_reuse_address = True

    def shutdown(self):
        self.socket.close()
        HTTPServer.shutdown(self)


class SimpleHttpServer():
    def __init__(self, ip, port):
        self.server = ThreadedHTTPServer((ip, port), HTTPRequestHandler)

    def start(self):
        self.server_thread = threading.Thread(target=self.server.serve_forever)
        self.server_thread.daemon = True
        self.server_thread.start()

    def waitForThread(self):
        self.server_thread.join()

    # def addRecord(self, recordID, jsonEncodedRecord):
    #
    # LocalData.records[recordID] = jsonEncodedRecord

    def stop(self):
        self.server.shutdown()
        self.waitForThread()


if __name__ == '__main__':
    # parser = argparse.ArgumentParser(description='HTTP Server')
    # parser.add_argument('port', type=int, help='Listening port for HTTP Server')
    # parser.add_argument('ip', help='HTTP Server IP')
    # args = parser.parse_args()

    # server = SimpleHttpServer(args.ip, args.port)
    server = SimpleHttpServer('', 8085)
    print 'HTTP Server Running...........'
    server.start()
    server.waitForThread()