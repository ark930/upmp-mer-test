#!/usr/bin/python

import json

import web

from upmp.UpmpHandler import UpmpHandler
from exception.NetException import *
from exception.UpmpException import *

urls = (
    '/', 'index',
    '/api/charge', 'charge',
    '/api/notify', 'notify',
    '/api/merchant', 'merchant'
)

data_path = "data/upmp-mer-files"


class index:
    def GET(self):
        return "Hello, world!"


class charge:
    def POST(self):
        try:
            data = web.data()
            json_data = json.loads(data) if data else {}
            res = UpmpHandler.charge(json_data)
            web.header('Content-Type', 'application/json')
            raise web.OK(json.dumps(res))
        except InvalidMerchantException:
            raise web.BadRequest('Invalid merchant')
        except ChargeFailException:
            raise web.BadRequest('Charge fail')
        except InvalidContentTypeException:
            raise web.BadRequest('Invalid content type')


class notify:
    def POST(self):
        try:
            data = web.data()
            UpmpHandler.notify(data)
            web.header('Content-Type', 'application/json')
            raise web.OK('success')
        except InvalidMerchantException:
            raise web.BadRequest('Invalid merchant')
        except InvalidNotifyException:
            raise web.BadRequest('Notify fail')
        except InvalidContentTypeException:
            raise web.BadRequest('Invalid content type')


class merchant:
    def GET(self):
        merchant_data = UpmpHandler.query_merchant_info(data_path)
        web.header('Content-Type', 'application/json')
        raise web.OK(json.dumps(merchant_data))


class MyWebApplication(web.application):
    def run(self, port=8080, *middleware):
        func = self.wsgifunc(*middleware)
        return web.httpserver.runsimple(func, ('0.0.0.0', port))


if __name__ == "__main__":
    def notfound():
        return web.notfound("Sorry, the page you were looking for was not found.")

    app = MyWebApplication(urls, globals())
    app.notfound = notfound
    app.run(port=8085)