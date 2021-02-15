from framework.templates import render


def main_view(requests):
    if requests['method'] == 'GET':
        data = requests.get('data')
        if data:
            name = data['name']
            surname = data['surname']
            age = data['age']
            print(f'Получено сообщение от {name} {surname}, возраст {age}')
    secret = requests.get('secret_key', None)
    language = requests.get('language', 'en')
    return '200 OK', render('index.html', secret=secret, language=language)


def about_view(requests):
    return '200 OK', render('about.html')


def contacts_view(requests):
    if requests['method'] == 'POST':
        data = requests['data']
        theme = data['theme']
        text = data['text']
        email = data['email']
        print(f'Пришло сообщение от {email} с темой {theme} и текстом {text}')
    return '200 OK', render('contacts.html')


def catalog_view(requests):
    return '200 OK', render('catalog.html')


def other_view(requests):
    return '200 OK', '<h1>Just another page...</h1>'
