from wsgiref.simple_server import make_server
from framework.core import Application, FakeApplication, DebugApplication
import views


def set_key(request):
    request['secret_key'] = 'KEY'


def set_language(request):
    request['language'] = 'LANGUAGE'


def user_authorize(request):
    request['is_authorize'] = True


fronts = [set_key, set_language, user_authorize]

a = {}
application = Application(views.routes, fronts)
# application = DebugApplication(views.routes, fronts)
# application = FakeApplication(views.routes, fronts)




with make_server('', 8888, application) as httpd:
    print('Start server')
    httpd.serve_forever()

