from framework.core import Application
import views

routes = {'/': views.main_view,
          '/index.html': views.main_view,
          '/about.html': views.about_view,
          '/contacts.html': views.contacts_view,
          '/catalog.html': views.catalog_view,
          '/other/': views.other_view,
          }


def set_key(request):
    request['secret_key'] = 'KEY'


def set_language(request):
    request['language'] = 'LANGUAGE'


def user_authorize(request):
    request['is_authorize'] = True


fronts = [set_key, set_language, user_authorize]

application = Application(routes, fronts)


