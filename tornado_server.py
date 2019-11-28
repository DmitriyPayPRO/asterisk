import tornado.httpserver
import tornado.ioloop
import tornado.web
import tornado.escape
import tornado.autoreload
import os
import sys
from asterisk_client import AsteriskClient

asterisk=None

class MainHandler(tornado.web.RequestHandler):
    # принимать запросы
    def get(self):
        self.write("API GET")

    def post(self):
        data = tornado.escape.json_decode(self.request.body)
        self.write('data is:  ' + data)
        if asterisk!=None:
            asterisk.Parse(data)




# class Asterisk(tornado.web.RequestHandler):
#     # общение с астериском
#     def get(self):
#         self.write("ASTERISK GET")


def make_app():
    return tornado.web.Application([
        (r"/api", MainHandler),
        # (r"/asterisk", Asterisk),
    ], **app_settings)


BASE_DIR = os.path.abspath(os.path.dirname(sys.argv[0]))

app_settings = {
    # 'autoreload': True,
    'debug': False,
    # 'gzip': False,
    'serve_traceback': False, # True, if Debug
    #'log_function': SOME_LOG_Function,
    #'default_handler_class': SOME_VALUE,
    #'default_handler_args': SOME_VALUE,
    # 'cookie_secret': "SOME_COOKIE_SECRET",
    # 'login_url': "/login",
    # 'xsrf_cookies': True,
    #'autoescape': None,
    # 'compiled_template_cache': False, # False, if Debug
    # 'template_path': os.path.join(BASE_DIR, 'templates'),
    #'template_loader': SOME_VALUE,
    # 'static_hash_cache': False, # False, if Debug
    # 'static_path': "/static",
    # 'static_url_prefix': "/static/",
}

if __name__ == "__main__":
    app = make_app()
    app.listen(8888)
    loop=tornado.ioloop.IOLoop.current().asyncio_loop
    asterisk=AsteriskClient(loop)
    tornado.ioloop.IOLoop.current().start()