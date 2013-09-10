#coding=utf-8
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
sys.path.insert(0, '../')

from base64 import b64decode
import json
import os
from qiniu import conf, rs, io
import tornado.ioloop
import tornado.web
import tornado.httpserver
from tornado.httpserver import HTTPServer
import urllib
import urllib2

#http server
PORT = 50011

#qiniu
STORAGE_ACCESS_KEY = ''
STORAGE_SECRET_KEY = ''
STORAGE_BUCKET = 't-persistent-status'
STORAGE_DOMAIN = 'http://t-persistent-status.qiniudn.com'

#DOMAIN = 'http://t-test2.qiniudn.com'
HOST = 'http://test.com:50011'


class UploadPageHdl(tornado.web.RequestHandler):
    def get(self):
        token = self.get_cookie('token', '')
        self.render('upload_custom.html', token=token)
        return


class ResultPageHdl(tornado.web.RequestHandler):
    def get(self):
        result = self.get_argument('upload_ret', '')
        success = False
        if not result:
            errCode = self.get_argument('code', '')
            errDetail = self.get_argument('error', 'something error')
            detail = 'Err Code:%s|Err Msg:%s' % (errCode, urllib.unquote(errDetail))
        else:
            try:
                detail = json.loads(b64decode(result))
                if detail.get('bucket') and detail.get('key') and detail.get('persistentId'):
                    success = True
                else:
                    detail = 'not enough data'
            except (TypeError, ValueError):
                detail = 'invalid data'

        self.render('result.html', success=success, detail=detail)
        return


class NotifyCallbackHdl(tornado.web.RequestHandler):
    def check_xsrf_cookie(self):
        return True

    def get(self):
        self.post()
        return

    def post(self):
        mimeType = 'application/json'
        if self.request.headers.get('Content-Type', '') == mimeType:
            data = self.request.body
            dataObj = json.loads(data)
            pid = dataObj.get('id', 'default')
            conf.ACCESS_KEY = STORAGE_ACCESS_KEY
            conf.SECRET_KEY = STORAGE_SECRET_KEY
            storagePolicy = rs.PutPolicy(STORAGE_BUCKET)
            storageToken = storagePolicy.token()

            extra = io.PutExtra()
            extra.mime_type = mimeType

            io.put(storageToken, str(pid), data, extra)
        return


class TokenHdl(tornado.web.RequestHandler):
    def get(self):
        token = self.get_cookie('token', '')
        self.render('makeToken.html', token=token)
        return


class MakeTokenHdl(tornado.web.RequestHandler):
    def get(self):
        self.post()
        return

    def post(self):
        bucket = str(self.get_argument('bucket', ''))
        aKey = str(self.get_argument('access_key', ''))
        sKey = str(self.get_argument('secret_key', ''))
        persistentOps = filter(lambda x: x, self.get_arguments('ops'))
        persistentNotifyUrl = '%s/notify_cb' % (HOST,)
        returnUrl = '%s/result' % (HOST,)
        #returnBody = 'etag=$(etag)&pid=$(persistentId)'
        if bucket and aKey and sKey and persistentOps and persistentNotifyUrl:
            conf.ACCESS_KEY = aKey
            conf.SECRET_KEY = sKey
            policy = rs.PutPolicy(bucket)
            policy.returnUrl = returnUrl
            #policy.returnBody = returnBody
            policy.persistentOps = str(';'.join(persistentOps))
            policy.persistentNotifyUrl = persistentNotifyUrl
            uploadToken = policy.token()
            self.set_cookie('token', uploadToken)
        else:
            self.set_cookie('token', '')
        self.redirect('/token')
        return


class StatusHdl(tornado.web.RequestHandler):
    def get(self):
        pid = self.get_argument('pid', '')
        success = False
        if not pid:
            status = '<persistentId> required'
        else:
            status = self.status_from_api(pid) or self.status_from_storage(pid)
            if status is None:
                status = 'no such pre-operations'
            else:
                success = True
        self.render('status.html', success=success, status=status)
        return

    def status_from_api(self, pid):
        api_url = 'http://api.qiniu.com/status/get/prefop?id=%s' % (pid,)
        req = urllib2.Request(api_url)
        try:
            resp = urllib2.urlopen(req, timeout=10)
        except urllib2.HTTPError:
            return
        if resp.code == 200:
            data = resp.read()
            try:
                data = json.loads(data)
            except (TypeError, ValueError):
                data = None
            return data
        return

    def status_from_storage(self, pid):
        api_url = '%s/%s' % (STORAGE_DOMAIN, pid)
        req = urllib2.Request(api_url)
        try:
            resp = urllib2.urlopen(req, timeout=10)
        except urllib2.HTTPError:
            return
        if resp.code == 200:
            data = resp.read()
            try:
                data = json.loads(data)
            except (TypeError, ValueError):
                data = None
            return data
        return

settings = dict(
    debug=False,
    #cookie_domain='',
    login_url='/',
    template_path='tmpl',
    static_path=os.path.abspath('static'),
)


urls = [
    (r'/upload', UploadPageHdl),
    (r'/token', TokenHdl),
    (r'/make_token', MakeTokenHdl),
    (r'/result', ResultPageHdl),
    (r'/notify_cb', NotifyCallbackHdl),
    (r'/status', StatusHdl),
]

app = tornado.web.Application(urls, **settings)
server = HTTPServer(app, xheaders=True)
server.bind(PORT)
server.start()
tornado.ioloop.IOLoop.instance().start()