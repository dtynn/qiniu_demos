#coding=utf-8
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
sys.path.insert(0, '../')

from base64 import urlsafe_b64decode, b64decode
import json

from qiniu import conf, rs

import tornado.ioloop
import tornado.web
import tornado.httpserver
from tornado.httpserver import HTTPServer

#http server
PORT = 50021

#qiniu
ACCESS_KEY = ''
SECRET_KEY = ''
BUCKET = 'for-temp'
DOMAIN = 'for-temp.qiniudn.com'


class makeTokenHdl(tornado.web.RequestHandler):
    def get(self):
        jsonp = self.get_argument('jsonp', 'callback')
        self.set_header('Content-Type', 'application/json')
        conf.ACCESS_KEY = ACCESS_KEY
        conf.SECRET_KEY = SECRET_KEY
        policy = rs.PutPolicy(BUCKET)
        policy.callbackUrl = 'http://dev-api.tuktalk.com/apis/cb'
        policy.callbackBody = 'key=$(etag)'
        #policy.persistentOps = 'avthumb/mp3/ar/44100/ab/32k;avthumb/mp3/aq/6/ar/16000'
        #policy.persistentNotifyUrl = ''
        uploadToken = policy.token()
        self.write('%s(%s)' % (jsonp, json.dumps(uploadToken)))
        return


class callbackForImage(tornado.web.RequestHandler):
    def post(self):
        key = self.get_argument('key', '')
        self.set_header('Content-Type', 'application/json')
        url = 'http://%s/%s' % (DOMAIN, key)
        self.write(json.dumps(url))
        return

settings = dict(
    debug=False,
    #cookie_domain='',
    login_url='/',
    template_path='tmpl',
)


urls = [
    (r'/apis/make_uptoken', makeTokenHdl),
]

app = tornado.web.Application(urls, **settings)
server = HTTPServer(app, xheaders=True)
server.bind(PORT)
server.start()
tornado.ioloop.IOLoop.instance().start()