from framework.templates import render


def main_view(request):
    secret = request.get('secret_key', None)
    language = request.get('language', 'en')
    return '200 OK', render('index.html', secret=secret, language=language)


def about_view(request):
    return '200 OK', render('about.html')


def contacts_view(request):
    return '200 OK', render('contacts.html')


def catalog_view(request):
    return '200 OK', render('catalog.html')


def other_view(request):
    return '200 OK', '<h1>Just another page...</h1>'
