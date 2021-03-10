from abc import ABC, abstractmethod
import sqlite3
from models import Category, SubCategory, Course, Student, CoursesType, CoursesStudents

connection = sqlite3.connect('database.sqlite')


class RecordNotFoundException(Exception):
    def __init__(self, message):
        super().__init__(f'Ошибка поиска данных БД: {message}')


class CreateException(Exception):
    def __init__(self, message):
        super().__init__(f'Ошибка добавления данных в БД: {message}')


class UpdateException(Exception):
    def __init__(self, message):
        super().__init__(f'Ошибка обновления данных БД: {message}')


class DeleteException(Exception):
    def __init__(self, message):
        super().__init__(f'Ошибка удаления из БД: {message}')


class BaseMapper(ABC):

    @abstractmethod
    def get_all_records(self):
        pass

    @abstractmethod
    def find_by_id(self, id):
        pass

    @abstractmethod
    def insert(self, obj):
        pass

    @abstractmethod
    def update(self, obj):
        pass

    @abstractmethod
    def delete(self, obj):
        pass


class IdentityMap:
    object_map = {}

    @classmethod
    def add_object(cls, obj):
        if obj.other_id not in cls.object_map.keys():
            cls.object_map[obj.other_id] = obj

    @classmethod
    def get_object(cls, key):
        if key in cls.object_map.keys():
            return cls.object_map[key]
        else:
            return None


class Filler:
    @classmethod
    def fill_category_with_subcat(cls, category_obj, cursor):
        statement = f'SELECT * FROM subcategories WHERE category_id=?'
        cursor.execute(statement, (category_obj.id,))
        subcategories_result = cursor.fetchall()
        for data in subcategories_result:
            subcat_obj = IdentityMap.get_object(f'subcategories_{data[0]}')

            if subcat_obj and not len(subcat_obj.courses_list):
                Filler.fill_subcategory_with_courses(subcat_obj, cursor)

            if not subcat_obj:
                subcat_obj = SubCategory(*data[1:])
                subcat_obj.id = data[0]
                subcat_obj.other_id = f'subcategories_{data[0]}'
                IdentityMap.add_object(subcat_obj)
                Filler.fill_subcategory_with_courses(subcat_obj, cursor)
            id_list = [obj.id for obj in category_obj.subcategories_list]
            if subcat_obj.id not in id_list:
                category_obj.subcategories_list.append(subcat_obj)

    @classmethod
    def fill_subcategory_with_courses(cls, subcat_obj, cursor):
        statement = f'SELECT * FROM courses WHERE subcategory_id=?'
        cursor.execute(statement, (subcat_obj.id,))
        courses_result = cursor.fetchall()
        for data in courses_result:
            course_obj = IdentityMap.get_object(f'courses_{data[0]}')

            if course_obj and not len(course_obj.students):
                Filler.fill_course_with_students(course_obj, cursor)

            if not course_obj:
                course_obj = Course(*data[1:])
                course_obj.id = data[0]
                course_obj.other_id = f'courses_{data[0]}'
                IdentityMap.add_object(course_obj)
                Filler.fill_course_with_students(course_obj, cursor)
            id_list = [obj.id for obj in subcat_obj.courses_list]
            if course_obj.id not in id_list:
                subcat_obj.courses_list.append(course_obj)

    @classmethod
    def fill_course_with_students(cls, course_obj, cursor):
        statement = f"SELECT (SELECT id FROM students WHERE students.id = courses_students.student_id) AS id, " \
                    f"(SELECT name FROM students WHERE students.id = courses_students.student_id) AS name, " \
                    f"(SELECT surname FROM students WHERE students.id = courses_students.student_id) AS surname " \
                    f"FROM courses_students WHERE course_id=?"

        cursor.execute(statement, (course_obj.id,))
        students_result = cursor.fetchall()
        for data in students_result:
            student_obj = IdentityMap.get_object(f'students_{data[0]}')
            if not student_obj:
                student_obj = Student(*data[1:])
                student_obj.id = data[0]
                student_obj.other_id = f'students_{data[0]}'
                IdentityMap.add_object(student_obj)
            id_list = [obj.id for obj in course_obj.students]
            if student_obj.id not in id_list:
                course_obj.students.append(student_obj)

    @classmethod
    def fill_student_with_courses(cls, student_obj, cursor):
        statement = f"SELECT (SELECT id FROM courses WHERE courses.id = courses_students.course_id) AS id, " \
                    f"(SELECT type_id FROM courses WHERE courses.id = courses_students.course_id) AS type_id, " \
                    f"(SELECT name FROM courses WHERE courses.id = courses_students.course_id) AS name, " \
                    f"(SELECT subcategory_id FROM courses WHERE courses.id = courses_students.course_id) AS subcategory_id " \
                    f"FROM courses_students WHERE student_id=?"
        cursor.execute(statement, (student_obj.id,))
        courses_result = cursor.fetchall()
        for data in courses_result:
            course_obj = IdentityMap.get_object(f'courses_{data[0]}')
            if not course_obj:
                course_obj = Course(*data[1:])
                course_obj.id = data[0]
                course_obj.other_id = f'courses_{data[0]}'
                IdentityMap.add_object(course_obj)
            id_list = [obj.id for obj in student_obj.courses]
            if course_obj.id not in id_list:
                student_obj.courses.append(course_obj)

    @classmethod
    def set_subcat_on_course(cls, course_obj, cursor):
        subcat_obj = IdentityMap.get_object(f'subcategories_{course_obj.subcategory_id}')
        if subcat_obj and not hasattr(subcat_obj, 'category'):
            Filler.set_category_on_subcat(subcat_obj, cursor)
        if not subcat_obj:
            statement = f'SELECT * FROM subcategories WHERE id=?'
            cursor.execute(statement, (course_obj.subcategory_id,))
            subcat_result = cursor.fetchone()
            subcat_obj = SubCategory(*subcat_result[1:])
            subcat_obj.id = subcat_result[0]
            subcat_obj.other_id = f'subcategories_{course_obj.subcategory_id}'
            IdentityMap.add_object(subcat_obj)
        course_obj.subcategory = subcat_obj

    @classmethod
    def set_type_on_course(cls, course_obj, cursor):
        type_obj = IdentityMap.get_object(f'courses_type_{course_obj.type_id}')
        if not type_obj:
            statement = f'SELECT * FROM courses_type WHERE id=?'
            cursor.execute(statement, (course_obj.type_id,))
            type_result = cursor.fetchone()
            type_obj = CoursesType(*type_result[1:])
            type_obj.id = type_result[0]
            type_obj.other_id = f'courses_type_{course_obj.type_id}'
            IdentityMap.add_object(type_obj)
        course_obj.type = type_obj

    @classmethod
    def set_category_on_subcat(cls, subcat_obj, cursor):
        category_obj = IdentityMap.get_object(f'categories_{subcat_obj.category_id}')
        if not category_obj:
            statement = f'SELECT * FROM categories WHERE id=?'
            cursor.execute(statement, (subcat_obj.category_id,))
            category_result = cursor.fetchone()
            category_obj = Category(*category_result[1:])
            category_obj.id = category_result[0]
            category_obj.other_id = f'categories_{subcat_obj.category_id}'
            IdentityMap.add_object(category_obj)
        subcat_obj.category = category_obj


class CategoryMapper(BaseMapper):

    def __init__(self, connection):
        self.connection = connection
        self.cursor = connection.cursor()
        self.tablename = 'categories'

    def get_all_records(self):
        statement = f'SELECT * FROM {self.tablename}'
        self.cursor.execute(statement)
        obj_list = []
        result = self.cursor.fetchall()
        for item in result:
            item_id, item = item
            category_obj = IdentityMap.get_object(f'{self.tablename}_{item_id}')
            if category_obj and not len(category_obj.subcategories_list):
                Filler.fill_category_with_subcat(category_obj, self.cursor)
            if not category_obj:
                category_obj = Category(item)
                category_obj.id = item_id

                Filler.fill_category_with_subcat(category_obj, self.cursor)

                category_obj.other_id = f'{self.tablename}_{item_id}'
                IdentityMap.add_object(category_obj)
            obj_list.append(category_obj)
        return obj_list

    def find_by_id(self, id):
        item_obj = IdentityMap.get_object(f'{self.tablename}_{id}')
        if not item_obj:
            statement = f"SELECT name FROM {self.tablename} WHERE id=?"
            self.cursor.execute(statement, (id,))
            result = self.cursor.fetchone()
            if result:
                item_obj = Category(*result)
                item_obj.id = id
                item_obj.other_id = f'{self.tablename}_{id}'
                IdentityMap.add_object(item_obj)
            else:
                raise RecordNotFoundException(f'Категория с id={id} не найдена!')
        return item_obj

    def insert(self, obj):
        statement = f"INSERT INTO {self.tablename} (name) VALUES (?)"
        self.cursor.execute(statement, (obj.name,))
        try:
            self.connection.commit()
        except Exception as e:
            raise CreateException(e.args)

    def update(self, obj):
        statement = f"UPDATE {self.tablename} SET name=? WHERE id=?"
        self.cursor.execute(statement, (obj.name, obj.id))
        try:
            self.connection.commit()
        except Exception as e:
            raise UpdateException(e.args)

    def delete(self, obj):
        statement = f"DELETE FROM {self.tablename} WHERE id=?"
        self.cursor.execute(statement, (obj.id,))
        try:
            self.connection.commit()
        except Exception as e:
            raise DeleteException(e.args)


class SubCategoryMapper(BaseMapper):

    def __init__(self, connection):
        self.connection = connection
        self.cursor = connection.cursor()
        self.tablename = 'subcategories'

    def get_all_records(self):
        statement = f'SELECT * FROM {self.tablename}'
        self.cursor.execute(statement)
        obj_list = []
        result = self.cursor.fetchall()
        for item in result:
            item_id, name, category_id = item
            subcat_obj = IdentityMap.get_object(f'{self.tablename}_{item_id}')
            if subcat_obj and not len(subcat_obj.courses_list):
                Filler.fill_subcategory_with_courses(subcat_obj, self.cursor)
            if subcat_obj and not hasattr(subcat_obj, 'category'):
                Filler.set_category_on_subcat(subcat_obj, self.cursor)
            if not subcat_obj:
                subcat_obj = SubCategory(name, category_id)
                subcat_obj.id = item_id

                category_obj = IdentityMap.get_object(f'categories_{category_id}')
                if category_obj and not len(category_obj.subcategories_list):
                    Filler.fill_category_with_subcat(category_obj, self.cursor)
                if not category_obj:
                    statement = f'SELECT name FROM categories WHERE id=?'
                    self.cursor.execute(statement, (category_id,))
                    category_result = self.cursor.fetchone()
                    category_obj = Category(*category_result)
                    category_obj.id = category_id

                    Filler.fill_category_with_subcat(category_obj, self.cursor)

                    category_obj.other_id = f'categories_{category_id}'
                    IdentityMap.add_object(category_obj)
                subcat_obj.category = category_obj

                Filler.fill_subcategory_with_courses(subcat_obj, self.cursor)
                subcat_obj.other_id = f'{self.tablename}_{item_id}'
                IdentityMap.add_object(subcat_obj)
            obj_list.append(subcat_obj)
        return obj_list

    def find_by_id(self, id):
        item_obj = IdentityMap.get_object(f'{self.tablename}_{id}')
        if not item_obj:
            statement = f"SELECT name FROM {self.tablename} WHERE id=?"
            self.cursor.execute(statement, (id,))
            result = self.cursor.fetchone()
            if result:
                item_obj = SubCategory(*result)
                item_obj.id = id
                item_obj.other_id = f'{self.tablename}_{id}'
                IdentityMap.add_object(item_obj)
            else:
                raise RecordNotFoundException(f'Подкатегория с id={id} не найдена!')
        return item_obj

    def insert(self, obj):
        statement = f"INSERT INTO {self.tablename} (name, category_id) VALUES (?, ?)"
        self.cursor.execute(statement, (obj.name, obj.category_id))
        try:
            self.connection.commit()
        except Exception as e:
            raise CreateException(e.args)

    def update(self, obj):
        statement = f"UPDATE {self.tablename} SET name=? WHERE id=?"
        self.cursor.execute(statement, (obj.name, obj.id))
        try:
            self.connection.commit()
        except Exception as e:
            raise UpdateException(e.args)

    def delete(self, obj):
        statement = f"DELETE FROM {self.tablename} WHERE id=?"
        self.cursor.execute(statement, (obj.id,))
        try:
            self.connection.commit()
        except Exception as e:
            raise DeleteException(e.args)


class CourseMapper(BaseMapper):

    def __init__(self, connection):
        self.connection = connection
        self.cursor = connection.cursor()
        self.tablename = 'courses'

    def get_all_records(self):
        statement = f'SELECT * FROM {self.tablename}'
        self.cursor.execute(statement)
        obj_list = []
        result = self.cursor.fetchall()
        for item in result:
            item_id, type_id, name, subcategory_id = item

            course_obj = IdentityMap.get_object(f'{self.tablename}_{item_id}')

            if course_obj and not hasattr(course_obj, 'type'):
                Filler.set_type_on_course(course_obj, self.cursor)

            if course_obj and not hasattr(course_obj, 'subcategory'):
                Filler.set_subcat_on_course(course_obj, self.cursor)

            if not course_obj:
                course_obj = Course(type_id, name, subcategory_id)
                course_obj.id = item_id

                subcat_obj = IdentityMap.get_object(f'subcategories_{subcategory_id}')

                if subcat_obj and not hasattr(subcat_obj, 'category'):
                    Filler.set_category_on_subcat(subcat_obj, self.cursor)

                if not subcat_obj:
                    statement = f'SELECT * FROM subcategories WHERE id=?'
                    self.cursor.execute(statement, (subcategory_id,))
                    subcat_result = self.cursor.fetchone()
                    subcat_obj = SubCategory(*subcat_result[1:])
                    subcat_obj.id = subcat_result[0]
                    subcat_obj.other_id = f'subcategories_{subcategory_id}'
                    Filler.set_category_on_subcat(subcat_obj, self.cursor)
                    IdentityMap.add_object(subcat_obj)

                Filler.set_type_on_course(course_obj, self.cursor)
                Filler.set_subcat_on_course(course_obj, self.cursor)

                course_obj.other_id = f'{self.tablename}_{item_id}'
                IdentityMap.add_object(course_obj)

            obj_list.append(course_obj)
        return obj_list

    def find_by_id(self, id):
        item_obj = IdentityMap.get_object(f'{self.tablename}_{id}')
        if not item_obj:
            statement = f"SELECT type_id, name, subcategory_id FROM {self.tablename} WHERE id=?"
            self.cursor.execute(statement, (id,))
            result = self.cursor.fetchone()
            if result:
                item_obj = Course(*result)
                item_obj.id = id
                item_obj.other_id = f'{self.tablename}_{id}'
                IdentityMap.add_object(item_obj)
            else:
                raise RecordNotFoundException(f'Курс с id={id} не найден!')
        return item_obj

    def insert(self, obj):
        statement = f"INSERT INTO {self.tablename} (type_id, name, subcategory_id) VALUES (?, ?, ?)"
        self.cursor.execute(statement, (obj.type_id, obj.name, obj.subcategory_id))
        try:
            self.connection.commit()
        except Exception as e:
            raise CreateException(e.args)

    def update(self, obj):
        statement = f"UPDATE {self.tablename} SET name=? WHERE id=?"
        self.cursor.execute(statement, (obj.name, obj.id))
        try:
            self.connection.commit()
        except Exception as e:
            raise UpdateException(e.args)

    def delete(self, obj):
        statement = f"DELETE FROM {self.tablename} WHERE id=?"
        self.cursor.execute(statement, (obj.id,))
        try:
            self.connection.commit()
        except Exception as e:
            raise DeleteException(e.args)


class StudentMapper(BaseMapper):

    def __init__(self, connection):
        self.connection = connection
        self.cursor = connection.cursor()
        self.tablename = 'students'

    def get_all_records(self):
        statement = f'SELECT * FROM {self.tablename}'
        self.cursor.execute(statement)
        obj_list = []
        result = self.cursor.fetchall()
        for item in result:
            item_id, name, surname = item

            student_obj = IdentityMap.get_object(f'{self.tablename}_{item_id}')
            if student_obj and not len(student_obj.courses):
                Filler.fill_student_with_courses(student_obj, self.cursor)
            if not student_obj:
                student_obj = Student(name, surname)
                student_obj.id = item_id
                Filler.fill_student_with_courses(student_obj, self.cursor)
                student_obj.other_id = f'{self.tablename}_{item_id}'
                IdentityMap.add_object(student_obj)
            obj_list.append(student_obj)
        return obj_list

    def find_by_id(self, id):
        item_obj = IdentityMap.get_object(f'{self.tablename}_{id}')
        if not item_obj:
            statement = f"SELECT name, surname FROM {self.tablename} WHERE id=?"
            self.cursor.execute(statement, (id,))
            result = self.cursor.fetchone()
            if result:
                item_obj = Student(*result)
                item_obj.id = id
                item_obj.other_id = f'{self.tablename}_{id}'
                IdentityMap.add_object(item_obj)
            else:
                raise RecordNotFoundException(f'Студент с id={id} не найден!')
        return item_obj

    def insert(self, obj):
        statement = f"INSERT INTO {self.tablename} (name, surname) VALUES (?, ?)"
        self.cursor.execute(statement, (obj.name, obj.surname))
        try:
            self.connection.commit()
        except Exception as e:
            raise CreateException(e.args)

    def update(self, obj):
        statement = f"UPDATE {self.tablename} SET name=?, surname=? WHERE id=?"
        self.cursor.execute(statement, (obj.name, obj.surname, obj.id))
        try:
            self.connection.commit()
        except Exception as e:
            raise UpdateException(e.args)

    def delete(self, obj):
        statement = f"DELETE FROM {self.tablename} WHERE id=?"
        self.cursor.execute(statement, (obj.id,))
        try:
            self.connection.commit()
        except Exception as e:
            raise DeleteException(e.args)


class CourseTypeMapper(BaseMapper):

    def __init__(self, connection):
        self.connection = connection
        self.cursor = connection.cursor()
        self.tablename = 'courses_type'

    def get_all_records(self):
        statement = f'SELECT * FROM {self.tablename}'
        self.cursor.execute(statement)
        obj_list = []
        result = self.cursor.fetchall()
        for item in result:
            item_id, name = item

            course_type_obj = IdentityMap.get_object(f'{self.tablename}_{item_id}')
            if not course_type_obj:
                course_type_obj = CoursesType(name)
                course_type_obj.id = item_id
                course_type_obj.other_id = f'{self.tablename}_{item_id}'
                IdentityMap.add_object(course_type_obj)
            obj_list.append(course_type_obj)
        return obj_list

    def find_by_id(self, id):
        item_obj = IdentityMap.get_object(f'{self.tablename}_{id}')
        if not item_obj:
            statement = f"SELECT name FROM {self.tablename} WHERE id=?"
            self.cursor.execute(statement, (id,))
            result = self.cursor.fetchone()
            if result:
                item_obj = CoursesType(*result)
                item_obj.id = id
                item_obj.other_id = f'{self.tablename}_{id}'
                IdentityMap.add_object(item_obj)
            else:
                raise RecordNotFoundException(f'Тип курса с id={id} не найден!')
        return item_obj

    def insert(self, obj):
        statement = f"INSERT INTO {self.tablename} (name) VALUES (?)"
        self.cursor.execute(statement, (obj.name,))
        try:
            self.connection.commit()
        except Exception as e:
            raise CreateException(e.args)

    def update(self, obj):
        statement = f"UPDATE {self.tablename} SET name=? WHERE id=?"
        self.cursor.execute(statement, (obj.name, obj.id))
        try:
            self.connection.commit()
        except Exception as e:
            raise UpdateException(e.args)

    def delete(self, obj):
        statement = f"DELETE FROM {self.tablename} WHERE id=?"
        self.cursor.execute(statement, (obj.id,))
        try:
            self.connection.commit()
        except Exception as e:
            raise DeleteException(e.args)


class CoursesStudentsMapper(BaseMapper):

    def __init__(self, connection):
        self.connection = connection
        self.cursor = connection.cursor()
        self.tablename = 'courses_students'

    def get_all_records(self):
        statement = f'SELECT * FROM {self.tablename}'
        self.cursor.execute(statement)
        obj_list = []
        result = self.cursor.fetchall()
        for item in result:
            item_id, course_id, student_id = item

            course_student_obj = IdentityMap.get_object(f'courses_students_{item_id}')
            if not course_student_obj:
                course_student_obj = CoursesStudents(course_id, student_id)
                course_student_obj.id = item_id
                course_student_obj.other_id = f'courses_students_{item_id}'
                IdentityMap.add_object(course_student_obj)
            obj_list.append(course_student_obj)
        return obj_list

    def find_by_id(self, id):
        item_obj = IdentityMap.get_object(f'{self.tablename}_{id}')
        if not item_obj:
            statement = f"SELECT course_id, student_id FROM {self.tablename} WHERE id=?"
            self.cursor.execute(statement, (id,))
            result = self.cursor.fetchone()
            if result:
                item_obj = CoursesStudents(*result)
                item_obj.id = id
                item_obj.other_id = f'{self.tablename}_{id}'
                IdentityMap.add_object(item_obj)
            else:
                raise RecordNotFoundException(f'Данные с id={id} не найдены!')
        return item_obj

    def insert(self, obj):
        statement = f"INSERT INTO {self.tablename} (course_id, student_id) VALUES (?, ?)"
        self.cursor.execute(statement, (obj.course_id, obj.student_id))
        try:
            self.connection.commit()
        except Exception as e:
            raise CreateException(e.args)

    def update(self, obj):
        statement = f"UPDATE {self.tablename} SET course_id=?, student_id=? WHERE id=?"
        self.cursor.execute(statement, (obj.course_id, obj.student_id, obj.id))
        try:
            self.connection.commit()
        except Exception as e:
            raise UpdateException(e.args)

    def delete(self, obj):
        statement = f"DELETE FROM {self.tablename} WHERE id=?"
        self.cursor.execute(statement, (obj.id,))
        try:
            self.connection.commit()
        except Exception as e:
            raise DeleteException(e.args)


class MapperRegistry:
    mappers = {
                  Category: CategoryMapper,
                  SubCategory: SubCategoryMapper,
                  Course: CourseMapper,
                  Student: StudentMapper,
                  CoursesType: CourseTypeMapper,
              }

    @staticmethod
    def get_mapper(obj):
        if isinstance(obj, Category):
            return CategoryMapper(connection)
        elif isinstance(obj, SubCategory):
            return SubCategoryMapper(connection)
        elif isinstance(obj, Course):
            return CourseMapper(connection)
        elif isinstance(obj, Student):
            return StudentMapper(connection)
        elif isinstance(obj, CoursesType):
            return CourseTypeMapper(connection)
        elif isinstance(obj, CoursesStudents):
            return CoursesStudentsMapper(connection)

    @staticmethod
    def get_current_mapper(CurrentClass):
        return MapperRegistry.mappers[CurrentClass](connection)
