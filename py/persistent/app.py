#coding=utf-8
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
sys.path.insert(0, '../')

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


class UploadPageHdl(tornado.web.RequestHandler):
    def get(self):
        conf.ACCESS_KEY = ACCESS_KEY
        conf.SECRET_KEY = SECRET_KEY
        policy = rs.PutPolicy(BUCKET)
        policy.callbackUrl = ''
        policy.callbackBody = ''
        policy.persistentUrl = ''
        policy.persistentNotifyUrl = ''
        uploadToken = policy.token()
        self.render('upload.html')
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