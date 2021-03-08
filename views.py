import json
import jsonpickle

from framework.templates import render

from models import TrainingSite, Category, SubCategory, Course, Student, CoursesType
from log_settings import Log, ConsoleLog, FileLog
from decos import debug
from framework.cbv import ListView, CreateView, TemplateView
from mappers import MapperRegistry

site = TrainingSite()
logger = Log(ConsoleLog(), 'main_log')
# logger = Log(FileLog(), 'main_log')


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
    template_name = 'category_list.html'

    def get_queryset(self):
        category_objects = MapperRegistry.get_current_mapper(Category).get_all_records()
        subcategory_objects = MapperRegistry.get_current_mapper(SubCategory).get_all_records()
        for category in category_objects:
            for subcategory in subcategory_objects:
                if subcategory.category_id == category.id:
                    category.subcategories_list.append(subcategory)
        return category_objects

    def get_context_data(self):
        logger.msg('Страница "Список категорий"')
        context = super().get_context_data()
        context['title'] = 'список категорий'
        return context


class CourseListView(ListView):
    template_name = 'course_list.html'

    def get_queryset(self):
        course_objects = MapperRegistry.get_current_mapper(Course).get_all_records()
        return course_objects

    def get_context_data(self):
        logger.msg('Страница "Список курсов"')
        context = super().get_context_data()
        context['title'] = 'список курсов'
        return context


class StudentListView(ListView):
    template_name = 'student_list.html'

    def get_queryset(self):
        queryset = MapperRegistry.get_current_mapper(Student).get_all_records()
        return queryset

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
        context['categories'] = MapperRegistry.get_current_mapper(Category).get_all_records()
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
        context['categories'] = MapperRegistry.get_current_mapper(Category).get_all_records()
        return context

    def create_obj(self, data):
        if data.get('name') and data.get('category_id'):
            site.create_subcategory(data['name'], data['category_id'])
            logger.msg(f'Подкатегория {data["name"]} успешно создана!')


class CreateCourseView(CreateView):
    template_name = 'create_course.html'

    def get_context_data(self):
        logger.msg('Страница "Создание курса"')
        context = super().get_context_data()
        context['title'] = 'создание курса'
        context['courses_type'] = MapperRegistry.get_current_mapper(CoursesType).get_all_records()
        context['subcategories'] = MapperRegistry.get_current_mapper(SubCategory).get_all_records()
        return context

    def create_obj(self, data):
        if data.get('name') and data.get('subcategory_id') and data.get('course_type'):
            site.create_course(data['course_type'], data['name'], data['subcategory_id'])
            logger.msg(f'Курс {data["name"]} успешно создан!')


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
        context['courses_list'] = MapperRegistry.get_current_mapper(Course).get_all_records()
        context['students_list'] = MapperRegistry.get_current_mapper(Student).get_all_records()
        return context

    def create_obj(self, data):
        if data.get('course_id') and data.get('student_id'):
            course = MapperRegistry.get_current_mapper(Course).find_by_id(int(data['course_id']))
            student = MapperRegistry.get_current_mapper(Student).find_by_id(int(data['student_id']))
            site.add_student(course, student)
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
    data = requests['data']
    source_course = MapperRegistry.get_current_mapper(Course).find_by_id(int(data['course_id']))
    if source_course:
        new_course = source_course.clone()
        new_course.name = f'copy_{data["name"]}'
        site.add_copy_course(new_course)
    course_objects = MapperRegistry.get_current_mapper(Course).get_all_records()

    return '200 OK', render('course_list.html', title=title, objects_list=course_objects)


@set_url('/api/')
@debug
def get_json_list(requests):
    logger.msg('Данные о курсах в JSON')
    course_objects = MapperRegistry.get_current_mapper(Course).get_all_records()
    data_string = jsonpickle.encode(course_objects, keys=True)
    data_string = str(json.loads(data_string))

    return '200 OK', data_string
