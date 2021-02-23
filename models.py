from abc import ABC

from patterns.prototype import PrototypeMixin
from logging import Log

logger = Log('main_log')


class User(ABC):
    def __init__(self, name):
        self.name = name


class Teacher(User):
    pass


class Student(User):
    pass


class UserFactory:
    user_types = {
        'teacher': Teacher,
        'student': Student,
    }

    @classmethod
    def create_user(cls, type, name):
        return cls.user_types[type](name)


class Category:
    auto_id = 0

    def __init__(self, name):
        self.name = name
        self.courses_set = set()
        self.id = Category.auto_id
        Category.auto_id += 1

    def course_count(self):
        return len(self.courses_set)


# class CategoryRepo:
#     """Класс - хранение и управление объектами категорий."""
#     object_dict = dict()
#
#     @classmethod
#     def add_category(cls, cat_name, courses_set=None):
#         """Создать объект категории и сохранить его."""
#         category_obj = Category(cat_name)
#
#         # Если такой категории еще не существует, добавить её в словарь объектов категорий.
#         if category_obj.name not in cls.object_dict:
#             cls.object_dict[category_obj.name] = category_obj
#
#         # Если передано множество содержащее курсы, наполнить ими текущий объект.
#         if courses_set:
#             cls.fill_with_courses(category_obj, courses_set)
#
#     @classmethod
#     def fill_with_courses(cls, category_obj, courses_set):
#         """Наполнить объект категория объектами входящих в него курсов."""
#         for course_name in courses_set:
#
#             # Если в словаре курсов объекта категории нет текущего курса, добавить его.
#             if course_name not in category_obj.courses_dict:
#                 course_obj = CourseRepo.add_course(course_name, category_obj.name)
#                 category_obj.courses_dict[course_name] = course_obj
#
#     @classmethod
#     def delete_category(cls, category_obj):
#         """Удалить категорию."""
#         try:
#             cls.object_dict.pop(category_obj.name)
#         except KeyError:
#             print('Такой категории не существует!')
#
#     @classmethod
#     def load_categories(cls):
#         """Получить список объектов категорий."""
#         return cls.object_dict.values()


class Course(ABC, PrototypeMixin):

    def __init__(self, type, course_name, category):
        self.type = type
        self.name = course_name
        self.category = category
        self.category.courses_set.add(self)


class CourseInteractive(Course):
    pass


class CourseRecord(Course):
    pass


class CourseWebinar(Course):
    pass


class CourseFactory:
    course_types = {
        'interactive': CourseInteractive,
        'record': CourseRecord,
        'webinar': CourseWebinar,
    }

    @classmethod
    def create_course(cls, type, name, category):
        return cls.course_types[type](type, name, category)


# class CourseRepo:
#     """Класс - хранение и управление объектов курсов."""
#     object_dict = dict()
#
#     @classmethod
#     def add_course(cls, course_name, cat_name):
#         """Создать объект курса и сохранить его."""
#         course_obj = Course(course_name, cat_name)
#
#         # Если такого курса не существует, добавляем его в словарь объектов курсов.
#         if course_obj.name not in cls.object_dict:
#             cls.object_dict[course_obj.name] = course_obj
#
#             # Получить объект категории, в который будет добавлен данный курс.
#             category_obj = CategoryRepo.object_dict[course_obj.category]
#
#             # Добавить новый курс в соответствующий объект категории.
#             CategoryRepo.fill_with_courses(category_obj, {course_obj.name})
#             return course_obj
#
#     @classmethod
#     def delete_course(cls, course_obj):
#         """Удалить объект курса."""
#         try:
#             cls.object_dict.pop(course_obj.name)
#         except KeyError:
#             print('Такого курса не существует!')
#
#     @classmethod
#     def load_courses(cls):
#         """Получить список объектов курсов."""
#         return cls.object_dict.values()


class TrainingSite:
    def __init__(self):
        self.teachers = []
        self.students = []
        self.categories = []
        self.courses = []

    def create_user(self, type, name):
        new_user = UserFactory.create_user(type, name)
        if type == 'teacher':
            self.teachers.append(new_user)
        else:
            self.students.append(new_user)
        return new_user

    def create_category(self, name):
        for category in self.categories:
            if category.name == name:
                logger.msg('Такая категория уже существует!')
                return
        new_category = Category(name)
        self.categories.append(new_category)
        return new_category

    def create_course(self, type, name, category):
        for course in self.courses:
            if course.name == name:
                logger.msg('Такой курс уже существует!')
                return
        new_course = CourseFactory.create_course(type, name, category)
        self.courses.append(new_course)
        return new_course

    def get_category_by_id(self, category_id):
        for category in self.categories:
            if category.id == category_id:
                return category
        logger.msg(f'Категории с id = {category_id} не существует!')

    def get_course_by_name(self, name):
        for course in self.courses:
            if course.name == name:
                return course
        logger.msg(f'Курса с названием "{name}" не существует!')


def create_category_obj(site):
    """Создать объекты категорий и курсов этих категорий."""
    course_types = list(CourseFactory.course_types.keys())
    catalog = [
        ('Python', [('Основы Питона', course_types[0]),
                    ('Алгоритмы', course_types[2]),
                    ('Клиент-серверные приложения', course_types[2])]),
        ('JavaScript', [('Основы JS', course_types[1]),
                        ('Продвинутый JS', course_types[2])]),
        ('MySql', [('PostgreSql', course_types[2]),
                   ('Не реляционные БД', course_types[2])]),
    ]

    for category, courses in catalog:
        cat_obj = site.create_category(category)
        [site.create_course(course[1], course[0], cat_obj) for course in courses]


if __name__ == '__main__':
    site = TrainingSite()
    create_category_obj(site)
