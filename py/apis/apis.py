#coding=utf-8
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
sys.path.insert(0, '../')

from base64 import urlsafe_b64decode, b64decode

from qiniu import conf, rs

import tornado.ioloop
import tornado.web
import tornado.httpserver
from tornado.httpserver import HTTPServer

#http server
PORT = 50021


class makeTokenHdl(tornado.web.RequestHandler):
    def get(self):
        self.set_header('Content-Type', 'application/json')
        return

settings = dict(
    debug=False,
    #cookie_domain='',
    login_url='/',
    template_path='tmpl',
)


urls = [

]

app = tornado.web.Application(urls, **settings)
server = HTTPServer(app, xheaders=True)
server.bind(PORT)
server.start()
tornado.ioloop.IOLoop.instance().start()