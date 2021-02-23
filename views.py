from framework.templates import render

from models import TrainingSite, CourseFactory, create_category_obj, UserFactory
from logging import Log


site = TrainingSite()
create_category_obj(site)
logger = Log('main_log')


def main_view(requests):
    logger.msg('Главная страница')
    title = 'главная'
    user_types = UserFactory.user_types.keys()
    if requests['method'] == 'GET':
        data = requests.get('data')
        if data:
            site.create_user(data["user_type"], data["name"])
            logger.msg(f'Пользователь {data["name"]} {data["surname"]} успешно сохранён!')
    secret = requests.get('secret_key', None)
    language = requests.get('language', 'en')
    return '200 OK', render('index.html', secret=secret, language=language, title=title, user_types=user_types)


def about_view(requests):
    logger.msg('Страница "О нас"')
    title = 'о нас'
    return '200 OK', render('about.html', title=title)


def contacts_view(requests):
    logger.msg('Страница "Контакты"')
    title = 'контакты'
    if requests['method'] == 'POST':
        data = requests['data']
        theme = data['theme']
        text = data['text']
        email = data['email']
        logger.msg(f'Пришло сообщение от {email} с темой {theme} и текстом {text}')
    return '200 OK', render('contacts.html', title=title)


def category_list_view(requests):
    logger.msg('Страница "Список категорий"')
    title = 'список категорий'
    obj_list = site.categories
    return '200 OK', render('category_list.html', title=title, obj_list=obj_list)


def course_list_view(requests):
    logger.msg('Страница "Список курсов"')
    title = 'список курсов'
    obj_list = site.courses
    return '200 OK', render('course_list.html', title=title, obj_list=obj_list)


def create_category_view(requests):
    logger.msg('Страница "Создание категории"')
    title = 'создание категории'
    categories = site.categories
    if requests['method'] == 'POST':
        data = requests['data']
        if data.get('name'):
            site.create_category(data['name'])
            logger.msg(f'Категория {data["name"]} успешно создана!')
    return '200 OK', render('create_category.html', title=title, categories=categories)


def create_course_view(requests):
    logger.msg('Страница "Создание курса"')
    title = 'создание курса'
    categories = site.categories
    course_types = CourseFactory.course_types.keys()

    if requests['method'] == 'POST':
        logger.msg(requests['data'])
        data = requests['data']
        if data.get('name') and data.get('category_id') and data.get('course_type'):
            category = site.get_category_by_id(int(data['category_id']))
            site.create_course(data['course_type'], data['name'], category)
            logger.msg(f'Курс {data["name"]} категории {data["course_type"]} успешно создан!')
    return '200 OK', render('create_course.html', title=title, categories=categories, course_types=course_types)


def copy_course_view(requests):
    logger.msg('Страница "Копирование курса"')
    title = 'список курсов'
    obj_list = site.courses
    data = requests['data']
    name = data['name']
    source_course = site.get_course_by_name(name)
    if source_course:
        new_course = source_course.clone()
        new_course.name = f'copy_{name}'
        site.courses.append(new_course)
    return '200 OK', render('course_list.html', title=title, obj_list=obj_list)
