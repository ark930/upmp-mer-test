# coding=utf-8

from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
from SocketServer import ThreadingMixIn
import threading
import re
import cgi
import json
import urlparse

from upmp.UpmpChannel import UpmpChannel
from upmp.UpmpConfig import UpmpConfig
from server_check import ServerCheck


class HTTPRequestHandler(BaseHTTPRequestHandler):
    root_path = "/Users/edwin/dev/test/notebook"

    def do_POST(self):

        length = int(self.headers.getheader('content-length'))
        data = self.rfile.read(length)
        if None != re.search('/api/v1/charge', self.path):
            ctype, _ = cgi.parse_header(self.headers.getheader('content-type'))
            if ctype == 'application/json':
                json_data = json.loads(data)
                amount = json_data['amount']
                mer_id = json_data['id'].encode('utf-8')

                sc = ServerCheck()
                merchant = sc.get_merchant_info_from_log(mer_id)
                mer_key = merchant['sk']
                if mer_key:
                    uc = UpmpChannel(mer_id, mer_key)
                    req_dict, tn = uc.charge(amount)

                    res = dict()
                    res['tn'] = tn
                    res['mode'] = '01'

                    self.send_response(200)
                    self.send_header('Content-Type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps(res))
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
            notify_data = urlparse.parse_qs(data)
            notify_dict = {key: notify_data[key][0] for key in notify_data}
            mer_id = notify_dict['merId']

            sc = ServerCheck()
            merchant = sc.get_merchant_info_from_log(mer_id)
            print(merchant)

            if merchant:
                mer_key = merchant['sk']
                uc = UpmpChannel(mer_id, mer_key)
                notify_dict = uc.notify(data)

                if notify_dict:
                    order_no = notify_dict['orderNumber']
                    order_time = notify_dict['orderTime']
                    settle_amount = notify_dict['settleAmount']
                    order_amount = settle_amount
                    trans_type = notify_dict['transType']
                    qn = notify_dict['qn']
                    print(order_no, order_time, settle_amount, trans_type, mer_id, qn)

                    self.send_response(200)
                    self.send_header('Content-Type', 'text/html')
                    self.end_headers()
                    self.wfile.write('success')

                    if trans_type == UpmpConfig.TRANS_TYPE_TRADE:
                        if settle_amount == '123':    # refund
                            uc.charge_retrieve(order_no, order_time)
                            uc.refund(order_time, qn)
                        elif settle_amount == '321':  # void
                            uc.void(order_time, order_amount, qn)
                    elif trans_type == UpmpConfig.TRANS_TYPE_VOID:
                        uc.void_retrieve(order_no, order_time)
                    elif trans_type == UpmpConfig.TRANS_TYPE_REFUND:
                        uc.refund_retrieve(order_no, order_time)
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
            data = sc.get_untest_merchant_json(self.root_path)
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