from framework.templates import render

from framework.models import CategoryRepo, create_category_obj, CourseRepo

# Создаём объекты категорий, которые уже содержат в себе объекты курсов.
create_category_obj()


def category_list_view(requests):
    title = 'список категорий'
    obj_list = CategoryRepo.load_categories()
    return '200 OK', render('category_list.html', title=title, obj_list=obj_list)


def course_list_view(requests):
    title = 'список курсов'
    obj_list = CourseRepo.load_courses()
    return '200 OK', render('course_list.html', title=title, obj_list=obj_list)


def create_category_view(requests):
    categories = CategoryRepo.load_categories()
    if requests['method'] == 'POST':
        print(requests['data'])
        data = requests['data']
        if data.get('name'):
            CategoryRepo.add_category(data['name'])
    title = 'создание категории'
    return '200 OK', render('create_category.html', title=title, categories=categories)


def create_course_view(requests):
    categories = CategoryRepo.load_categories()
    if requests['method'] == 'POST':
        print(requests['data'])
        data = requests['data']
        if data.get('name') and data.get('category'):
            CourseRepo.add_course(data['name'], data['category'])
    title = 'создание курса'
    return '200 OK', render('create_course.html', title=title, categories=categories)

