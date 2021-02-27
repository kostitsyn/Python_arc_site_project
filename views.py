from framework.templates import render

from models import TrainingSite, CourseFactory, fill_with_objects, UserFactory
from logging import Log
from decos import debug


site = TrainingSite()
fill_with_objects(site)
logger = Log('main_log')

routes = dict()


def set_url(url):
    """
    Функция-декоратор, добавляющая новую пару путь: словарь.
    :param url:
    :return:
    """
    def wrapper(func):
        routes[url] = func
    return wrapper


@set_url('/')
@debug
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


@set_url('/about/')
@debug
def about_view(requests):
    logger.msg('Страница "О нас"')
    title = 'о нас'
    return '200 OK', render('about.html', title=title)


@set_url('/contacts/')
@debug
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


@set_url('/category_list/')
@debug
def category_list_view(requests):
    logger.msg('Страница "Список категорий"')
    title = 'список категорий'
    obj_list = site.categories
    return '200 OK', render('category_list.html', title=title, category_list=obj_list)


@set_url('/course_list/')
@debug
def course_list_view(requests):
    logger.msg('Страница "Список курсов"')
    title = 'список курсов'
    obj_list = site.courses
    return '200 OK', render('course_list.html', title=title, obj_list=obj_list)


@set_url('/create_category/')
@debug
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


@set_url('/create_subcategory/')
@debug
def create_subcategory_view(requests):
    logger.msg('Страница "Создание подкатегории')
    title = 'создание подкатегории'
    categories = site.categories
    subcategories = site.subcategories
    if requests['method'] == 'POST':
        data = requests['data']
        if data.get('name') and data.get('category_id'):
            category = site.get_category_by_id(int(data['category_id']))
            site.create_subcategory(data['name'], category)
            logger.msg(f'Подкатегория {data["name"]} категории {category.name} успешно создана!')
    return '200 OK', render('create_subcategory.html', title=title, categories=categories)


@set_url('/create_course/')
@debug
def create_course_view(requests):
    logger.msg('Страница "Создание курса"')
    title = 'создание курса'
    subcategories = site.subcategories
    course_types = CourseFactory.course_types.keys()

    if requests['method'] == 'POST':
        logger.msg(requests['data'])
        data = requests['data']
        if data.get('name') and data.get('subcategory_id') and data.get('course_type'):
            subcategory = site.get_subcategory_by_id(int(data['subcategory_id']))
            site.create_course(data['course_type'], data['name'], subcategory)
            logger.msg(f'Курс {data["name"]} категории {subcategory.name}/{subcategory.category.name} успешно создан!')
    return '200 OK', render('create_course.html', title=title, subcategories=subcategories, course_types=course_types)


@set_url('/copy_course/')
@debug
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

