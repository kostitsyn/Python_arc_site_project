from abc import ABC

from patterns.prototype import PrototypeMixin

from patterns.observer import Subject, Observer

from log_settings import Log, ConsoleLog, FileLog

from orm.unit_of_work import DomainObject

from orm.unit_of_work import UnitOfWork

logger = Log(ConsoleLog(), 'main_log')
# logger = Log(FileLog(), 'main_log')


class User(ABC):
    def __init__(self, name, surname):
        self.name = name
        self.surname = surname


class Teacher(User):
    pass


class Student(User, DomainObject):

    def __init__(self, name, surname):
        super().__init__(name, surname)
        self.courses = list()


class UserFactory:
    user_types = {
        'teacher': Teacher,
        'student': Student,
    }

    @classmethod
    def create_user(cls, type, name, surname):
        return cls.user_types[type](name, surname)


class Category(DomainObject):

    def __init__(self, name):
        self.name = name
        self.subcategories_list = list()

    def course_count(self):
        result = 0
        for subcategory in self.subcategories_list:
            result += len(subcategory.courses_list)
        return result


class SubCategory(DomainObject):

    def __init__(self, name, category_id):
        self.name = name
        self.courses_list = list()
        self.category_id = category_id

    def course_count(self):
        return len(self.courses_list)


class Course(PrototypeMixin, Subject, DomainObject):

    def __init__(self, type_id, course_name, subcategory_id):
        super().__init__()
        self.type_id = type_id
        self.name = course_name
        self.subcategory_id = subcategory_id
        self.students = list()

    def add_student(self, student):
        self.students.append(student)
        student.courses.append(self)
        self.notify()

    def attach(self, observer):
        self._observers.append(observer)

    def detach(self, observer):
        self._observers.remove(observer)

    def notify(self):
        for observer in self._observers:
            observer.update(self)


class SmsNotifier(Observer):
    def update(self, course_obj):
        logger.msg(f'SMS: К курсу {course_obj.name} присоединился'
                   f' {course_obj.students[-1].name} {course_obj.students[-1].surname}')


class EmailNotifier(Observer):
    def update(self, course_obj):
        logger.msg(f'EMAIL: К курсу {course_obj.name} присоединился'
                   f' {course_obj.students[-1].name} {course_obj.students[-1].surname}')


class CoursesType(DomainObject):
    def __init__(self, name):
        self.name = name


class CoursesStudents(DomainObject):
    def __init__(self, course_id, student_id):
        self.course_id = course_id
        self.student_id = student_id


class TrainingSite:
    def __init__(self):
        self.teachers = []
        self.students = []
        self.categories = []
        self.subcategories = []
        self.courses = []

    def create_user(self, type, name, surname):
        new_user = UserFactory.create_user(type, name, surname)
        if type == 'teacher':
            self.teachers.append(new_user)
        else:
            new_user.mark_new()
            UnitOfWork.get_current().commit()

            self.students.append(new_user)
        return new_user

    def create_category(self, name):
        for category in self.categories:
            if category.name == name:
                logger.msg('Такая категория уже существует!')
                return
        new_category = Category(name)
        new_category.mark_new()
        UnitOfWork.get_current().commit()

        self.categories.append(new_category)
        return new_category

    def create_subcategory(self, name, category_id):
        for subcategory in self.subcategories:
            if subcategory.name == name:
                logger.msg('Такая подкатегория уже существует!')
                return
        new_subcat = SubCategory(name, category_id)
        new_subcat.mark_new()
        UnitOfWork.get_current().commit()

        self.subcategories.append(new_subcat)
        return new_subcat

    def create_course(self, type_id, name, subcategory_id):
        for course in self.courses:
            if course.name == name:
                logger.msg(f'Внимание! такой курс уже существует в подкатегории {course.subcategory.name}.')
                return
        new_course = Course(type_id, name, subcategory_id)
        new_course.mark_new()
        UnitOfWork.get_current().commit()
        self.courses.append(new_course)
        return new_course

    def get_category_by_id(self, category_id):
        for category in self.categories:
            if category.id == category_id:
                return category
        logger.msg('Такой категории не существует!')

    def get_subcategory_by_id(self, subcategory_id):
        for subcategory in self.subcategories:
            if subcategory.id == subcategory_id:
                return subcategory
        logger.msg('Такой подкатегории не существует!')

    def get_course_by_id(self, course_id):
        for course in self.courses:
            if course.id == course_id:
                return course
        logger.msg('Такого курса не существует!')

    def get_student_by_id(self, student_id):
        for student in self.students:
            if student.id == student_id:
                return student
        logger.msg('Такого студента не существует!')

    def add_student(self, course, student):
        new_record = CoursesStudents(course.id, student.id)

        email_notifier = EmailNotifier()
        sms_notifier = SmsNotifier()
        course.attach(email_notifier)
        course.attach(sms_notifier)
        course.add_student(student)

        new_record.mark_new()
        UnitOfWork.get_current().commit()

    def add_copy_course(self, copy_course):
        copy_course.mark_new()
        UnitOfWork.get_current().commit()
