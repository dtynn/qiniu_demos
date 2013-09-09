#coding=utf-8
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
sys.path.insert(0, '../')

from base64 import urlsafe_b64decode, b64decode

from qiniu import conf, rs

import tornado.ioloop
import tornado.web
from tornado.httpserver import HTTPServer

#http server
PORT = 50011

#qiniu
ACCESS_KEY = ''
SECRET_KEY = ''
BUCKET = ''
DOMAIN = ''
HOST = ''


class UploadPageHdl(tornado.web.RequestHandler):
    def get(self):
        conf.ACCESS_KEY = ACCESS_KEY
        conf.SECRET_KEY = SECRET_KEY
        policy = rs.PutPolicy(BUCKET)
        policy.returnUrl = ''
        policy.returnBody = 'etag=$(etag)&pid=$(persistentId)'
        #policy.callbackUrl = ''
        #policy.callbackBody = ''
        policy.persistentOps = '"avthumb/mp3/ar/44100/ab/32k;avthumb/mp3/aq/6/ar/16000"'
        policy.persistentNotifyUrl = ''
        uploadToken = policy.token()
        self.render('upload.html', token=uploadToken)
        return


class ResultPageHdl(tornado.web.RequestHandler):
    def get(self):
        result = self.get_argument('upload_ret')
        #self.write(result)
        self.write(b64decode(result))
        return


class NotifyCallbackHdl(tornado.web.RequestHandler):
    def check_xsrf_cookie(self):
        return

    def get(self):
        self.post()
        return

    def post(self):
        print 'posted'
        return


settings = dict(
    debug=False,
    #cookie_domain='',
    login_url='/',
    template_path='tmpl',
)


urls = [
    (r'/upload', UploadPageHdl),
    (r'/result', ResultPageHdl),
    (r'/notify_cb', NotifyCallbackHdl),
]

app = tornado.web.Application(urls, **settings)
server = HTTPServer(app, xheaders=True)
server.bind(PORT)
server.start()
tornado.ioloop.IOLoop.instance().start()