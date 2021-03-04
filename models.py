from abc import ABC

from patterns.prototype import PrototypeMixin

from patterns.observer import Subject, Observer

from log_settings import Log, ConsoleLog, FileLog

logger = Log(ConsoleLog(), 'main_log')
# logger = Log(FileLog(), 'main_log')


class User(ABC):
    def __init__(self, name, surname):
        self.name = name
        self.surname = surname


class Teacher(User):
    pass


class Student(User):
    auto_id = 0

    def __init__(self, name, surname):
        super().__init__(name, surname)
        self.courses = list()
        self.id = Student.auto_id
        Student.auto_id += 1


class UserFactory:
    user_types = {
        'teacher': Teacher,
        'student': Student,
    }

    @classmethod
    def create_user(cls, type, name, surname):
        return cls.user_types[type](name, surname)


class Category:
    auto_id = 0

    def __init__(self, name):
        self.name = name
        self.subcategories_set = set()
        self.id = Category.auto_id
        Category.auto_id += 1

    def course_count(self):
        result = 0
        for subcategory in self.subcategories_set:
            result += len(subcategory.courses_set)
        return result


class SubCategory:
    auto_id = 0

    def __init__(self, name, category):
        self.name = name
        self.courses_set = set()
        self.category = category
        self.category.subcategories_set.add(self)
        self.id = Category.auto_id
        Category.auto_id += 1

    def course_count(self):
        return len(self.courses_set)


class Course(PrototypeMixin, Subject):
    auto_id = 0

    def __init__(self, type, course_name, subcategory):
        super().__init__()
        self.type = type
        self.name = course_name
        self.subcategory = subcategory
        self.students = list()
        self.subcategory.courses_set.add(self)
        self.id = Course.auto_id
        Course.auto_id += 1

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


class CourseInteractive(Course):
    auto_id = 0

    def __init__(self, type, course_name, subcategory):
        super().__init__(type, course_name, subcategory)
        self.id = CourseInteractive.auto_id
        CourseInteractive.auto_id += 1


class CourseRecord(Course):
    auto_id = 0

    def __init__(self, type, course_name, subcategory):
        super().__init__(type, course_name, subcategory)
        self.id = CourseInteractive.auto_id
        CourseInteractive.auto_id += 1


class CourseWebinar(Course):
    auto_id = 0

    def __init__(self, type, course_name, subcategory):
        super().__init__(type, course_name, subcategory)
        self.id = CourseInteractive.auto_id
        CourseInteractive.auto_id += 1


class CourseFactory:
    course_types = {
        'interactive': CourseInteractive,
        'record': CourseRecord,
        'webinar': CourseWebinar,
    }

    @classmethod
    def create_course(cls, type, name, category):
        return cls.course_types[type](type, name, category)


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

    def create_subcategory(self, name, category):
        for subcategory in self.subcategories:
            if subcategory.name == name:
                logger.msg('Такая подкатегория уже существует!')
                return
        new_subcat = SubCategory(name, category)
        self.subcategories.append(new_subcat)
        return new_subcat

    def create_course(self, type, name, subcategory):
        for course in self.courses:
            if course.name == name and course.subcategory.name == subcategory.name:
                logger.msg(f'Внимание! такой курс уже существует в подкатегории {course.subcategory.name}.')
                return
        new_course = CourseFactory.create_course(type, name, subcategory)
        email_notifier = EmailNotifier()
        sms_notifier = SmsNotifier()
        new_course.attach(email_notifier)
        new_course.attach(sms_notifier)
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


def fill_with_objects(site):
    """Создать объекты категорий и курсов этих категорий."""
    course_types = list(CourseFactory.course_types.keys())
    catalog = [['Программирование', [['Python', [['Основы Питона', course_types[0]], ['Алгоритмы', course_types[2]],
                                                 ['Клиент-серверные приложения', course_types[2]]]],
                                     ['JavaScript',
                                      [['Основы JS', course_types[1]], ['Продвинутый JS', course_types[2]]]],
                                     ['MySql',
                                      [['PostgreSql', course_types[2]], ['Не реляционные БД', course_types[2]]]]]],
               ['Дизайн', [['Веб-дизайн', [['Основы Adobe Photoshop', course_types[0]],
                                           ['Adobe Illustrator для дизайнеров', course_types[2]]]],
                           ['Дизайн жилых интерьеров',
                            [['Основы ArchiCAD', course_types[1]], ['Основы Adobe Photoshop', course_types[0]],
                             ['Adobe Illustrator для дизайнеров', course_types[2]]]]]]
               ]

    for category, subcategories in catalog:
        cat_obj = site.create_category(category)
        for subcategory, courses in subcategories:
            subcat_obj = site.create_subcategory(subcategory, cat_obj)
            [site.create_course(course[1], course[0], subcat_obj) for course in courses]


if __name__ == '__main__':
    site = TrainingSite()
    fill_with_objects(site)
