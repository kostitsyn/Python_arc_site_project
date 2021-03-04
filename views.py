import jsonpickle

from framework.templates import render

from models import TrainingSite, CourseFactory, fill_with_objects, UserFactory
from log_settings import Log, ConsoleLog, FileLog
from decos import debug
from framework.cbv import ListView, CreateView, TemplateView

site = TrainingSite()
fill_with_objects(site)
logger = Log(ConsoleLog(), 'main_log')
# logger = Log(FileLog(), 'main_log')


# routes = dict()

class MainView(TemplateView):
    template_name = 'index.html'

    def get_context_data(self):
        logger.msg('Главная страница')
        context = super().get_context_data()
        context['title'] = 'главная'
        return context


class AboutView(TemplateView):
    template_name = 'about.html'

    def get_context_data(self):
        logger.msg('Страница "О нас"')
        context = super().get_context_data()
        context['title'] = 'о нас'
        return context


class ContactsView(TemplateView):
    template_name = 'contacts.html'

    def get_context_data(self):
        logger.msg('Страница "Контакты"')
        context = super().get_context_data()
        context['title'] = 'контакты'

        return context


class CategoryListView(ListView):
    queryset = site.categories
    template_name = 'category_list.html'

    def get_context_data(self):
        logger.msg('Страница "Список категорий"')
        context = super().get_context_data()
        context['title'] = 'список категорий'
        return context


class CourseListView(ListView):
    queryset = site.courses
    template_name = 'course_list.html'

    def get_context_data(self):
        logger.msg('Страница "Список курсов"')
        context = super().get_context_data()
        context['title'] = 'список курсов'
        return context


class StudentListView(ListView):
    queryset = site.students
    template_name = 'student_list.html'

    def get_context_data(self):
        logger.msg('Страница "Список студентов"')
        context = super().get_context_data()
        context['title'] = 'список студентов'
        return context


class CreateCategoryView(CreateView):
    template_name = 'create_category.html'

    def get_context_data(self):
        logger.msg('Страница "Создание категории"')
        context = super().get_context_data()
        context['title'] = 'создание категории'
        context['categories'] = site.categories
        return context

    def create_obj(self, data):
        if data.get('name'):
            site.create_category(data['name'])
            logger.msg(f'Категория {data["name"]} успешно создана!')


class CreateSubcategoryView(CreateView):
    template_name = 'create_subcategory.html'

    def get_context_data(self):
        logger.msg('Страница "Создание подкатегории')
        context = super().get_context_data()
        context['title'] = 'создание подкатегории'
        context['categories'] = site.categories
        return context

    def create_obj(self, data):
        if data.get('name') and data.get('category_id'):
            category = site.get_category_by_id(int(data['category_id']))
            site.create_subcategory(data['name'], category)
            logger.msg(f'Подкатегория {data["name"]} категории {category.name} успешно создана!')


class CreateCourseView(CreateView):
    template_name = 'create_course.html'

    def get_context_data(self):
        logger.msg('Страница "Создание курса"')
        context = super().get_context_data()
        context['title'] = 'создание курса'
        context['course_types'] = CourseFactory.course_types.keys()
        context['subcategories'] = site.subcategories
        return context

    def create_obj(self, data):
        if data.get('name') and data.get('subcategory_id') and data.get('course_type'):
            subcategory = site.get_subcategory_by_id(int(data['subcategory_id']))
            site.create_course(data['course_type'], data['name'], subcategory)
            logger.msg(f'Курс {data["name"]} категории {subcategory.name}/'
                       f'{subcategory.category.name} успешно создан!')


class CreateStudentView(CreateView):
    template_name = 'create_student.html'

    def get_context_data(self):
        logger.msg('Страница "Регистрация студента"')
        context = super().get_context_data()
        context['title'] = 'регистрация студента'
        return context

    def create_obj(self, data):
        if data.get('name') and data.get('surname'):
            site.create_user('student', data['name'], data['surname'])
            logger.msg(f'Студент {data["name"]} {data["surname"]} успешно зарегистрирован!')


class AddStudentView(CreateView):
    template_name = 'add_student.html'

    def get_context_data(self):
        logger.msg('Страница "Запись студента на курс"')
        context = super().get_context_data()
        context['title'] = 'запись на курс'
        context['courses_list'] = site.courses
        context['students_list'] = site.students
        return context

    def create_obj(self, data):
        if data.get('course_id') and data.get('student_id'):
            course = site.get_course_by_id(int(data['course_id']))
            student = site.get_student_by_id(int(data['student_id']))
            course.add_student(student)
            logger.msg(f'Студент {student.name} {student.surname} был успешно добавлен на курс "{course.name}"!')

routes = {
    '/': MainView(),
    '/about/': AboutView(),
    '/contacts/': ContactsView(),
    '/category_list/': CategoryListView(),
    '/course_list/': CourseListView(),
    '/student_list/': StudentListView(),
    '/create_category/': CreateCategoryView(),
    '/create_subcategory/': CreateSubcategoryView(),
    '/create_course/': CreateCourseView(),
    '/create_student/': CreateStudentView(),
    '/add_student/': AddStudentView(),
}


def set_url(url):
    """
    Функция-декоратор, добавляющая новую пару путь: словарь.
    :param url:
    :return:
    """
    def wrapper(func):
        routes[url] = func
    return wrapper


@set_url('/copy_course/')
@debug
def copy_course_view(requests):
    logger.msg('Страница "Копирование курса"')
    title = 'список курсов'
    obj_list = site.courses
    data = requests['data']
    source_course = site.get_course_by_id(int(data['course_id']))
    if source_course:
        new_course = source_course.clone()
        new_course.name = f'copy_{data["name"]}'
        site.courses.append(new_course)
    return '200 OK', render('course_list.html', title=title, obj_list=obj_list)


@set_url('/api/')
@debug
def get_json_list(requests):
    logger.msg('Данные о курсах в JSON')
    data_string = jsonpickle.encode(site.courses, keys=True)
    return '200 OK', data_string


# @set_url('/')
# @debug
# def main_view(requests):
#     logger.msg('Главная страница')
#     title = 'главная'
#     secret = requests.get('secret_key', None)
#     language = requests.get('language', 'en')
#     return '200 OK', render('index.html', secret_key=secret, language=language, title=title)

# @set_url('/about/')
# @debug
# def about_view(requests):
#     logger.msg('Страница "О нас"')
#     title = 'о нас'
#     return '200 OK', render('about.html', title=title)

# @set_url('/contacts/')
# @debug
# def contacts_view(requests):
#     logger.msg('Страница "Контакты"')
#     title = 'контакты'
#     if requests['method'] == 'POST':
#         data = requests['data']
#         theme = data['theme']
#         text = data['text']
#         email = data['email']
#         logger.msg(f'Пришло сообщение от {email} с темой {theme} и текстом {text}')
#     return '200 OK', render('contacts.html', title=title)

# @set_url('/category_list/')
# @debug
# def category_list_view(requests):
#     logger.msg('Страница "Список категорий"')
#     title = 'список категорий'
#     obj_list = site.categories
#     return '200 OK', render('category_list.html', title=title, objects_list=obj_list)

# @set_url('/course_list/')
# @debug
# def course_list_view(requests):
#     logger.msg('Страница "Список курсов"')
#     title = 'список курсов'
#     obj_list = site.courses
#     return '200 OK', render('course_list.html', title=title, objects_list=obj_list)

# @set_url('/create_category/')
# @debug
# def create_category_view(requests):
#     logger.msg('Страница "Создание категории"')
#     title = 'создание категории'
#     categories = site.categories
#     if requests['method'] == 'POST':
#         data = requests['data']
#         if data.get('name'):
#             site.create_category(data['name'])
#             logger.msg(f'Категория {data["name"]} успешно создана!')
#     return '200 OK', render('create_category.html', title=title, categories=categories)

# @set_url('/create_subcategory/')
# @debug
# def create_subcategory_view(requests):
#     logger.msg('Страница "Создание подкатегории')
#     title = 'создание подкатегории'
#     categories = site.categories
#     if requests['method'] == 'POST':
#         data = requests['data']
#         if data.get('name') and data.get('category_id'):
#             category = site.get_category_by_id(int(data['category_id']))
#             site.create_subcategory(data['name'], category)
#             logger.msg(f'Подкатегория {data["name"]} категории {category.name} успешно создана!')
#     return '200 OK', render('create_subcategory.html', title=title, categories=categories)

# @set_url('/create_course/')
# @debug
# def create_course_view(requests):
#     logger.msg('Страница "Создание курса"')
#     title = 'создание курса'
#     subcategories = site.subcategories
#     course_types = CourseFactory.course_types.keys()
#     if requests['method'] == 'POST':
#         logger.msg(requests['data'])
#         data = requests['data']
#         if data.get('name') and data.get('subcategory_id') and data.get('course_type'):
#             subcategory = site.get_subcategory_by_id(int(data['subcategory_id']))
#             site.create_course(data['course_type'], data['name'], subcategory)
#             logger.msg(f'Курс {data["name"]} категории {subcategory.name}/
#             {subcategory.category.name} успешно создан!')
#     return '200 OK', render('create_course.html', title=title, subcategories=subcategories, course_types=course_types)

# @set_url('/create_student/')
# @debug
# def create_student_view(requests):
#     logger.msg('Страница "Регистрация студента"')
#     title = 'регистрация студента'
#     if requests['method'] == 'POST':
#         data = requests['data']
#         if data.get('name') and data.get('surname'):
#             site.create_user('student', data['name'], data['surname'])
#             logger.msg(f'Студент {data["name"]} {data["surname"]} успешно зарегистрирован!')
#     return '200 OK', render('create_student.html', title=title)

# @set_url('/student_list/')
# @debug
# def student_list_view(requests):
#     logger.msg('Страница "Список студентов"')
#     title = 'список студентов'
#     students = site.students
#     return '200 OK', render('student_list.html', title=title, objects_list=students)

# @set_url('/add_student/')
# @debug
# def add_student_view(requests):
#     logger.msg('Страница "Запись студента на курс"')
#     title = 'запись на курс'
#     courses = site.courses
#     students = site.students
#     if requests['method'] == 'POST':
#         data = requests['data']
#         if data.get('course_id') and data.get('student_id'):
#             course = site.get_course_by_id(int(data['course_id']))
#             student = site.get_student_by_id(int(data['student_id']))
#             course.add_student(student)
#             logger.msg(f'Студент {student.name} {student.surname} был успешно добавлен на курс "{course.name}"!')
#     return '200 OK', render('add_student.html', title=title, courses_list=courses, students_list=students)
