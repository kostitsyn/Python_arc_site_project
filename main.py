from wsgiref.simple_server import make_server
from framework.core import Application
import views
from logging import Log

logger = Log('main_log')

routes = {'/': views.main_view,
          '/index/': views.main_view,
          '/about/': views.about_view,
          '/contacts/': views.contacts_view,
          '/category_list/': views.category_list_view,
          '/course_list/': views.course_list_view,
          '/create_category/': views.create_category_view,
          '/create_course/': views.create_course_view,
          '/copy_course/': views.copy_course_view,
          }


def set_key(request):
    request['secret_key'] = 'KEY'


def set_language(request):
    request['language'] = 'LANGUAGE'


def user_authorize(request):
    request['is_authorize'] = True


fronts = [set_key, set_language, user_authorize]

application = Application(routes, fronts)

with make_server('', 8888, application) as httpd:
    print('Start server')
    httpd.serve_forever()


