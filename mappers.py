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


class UnitOfWork:
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
            item_id, item = item[0], item[1:]
            category_obj = Category(*item)
            category_obj.id = item_id
            obj_list.append(category_obj)
        return obj_list

    def find_by_id(self, id):
        item_obj = UnitOfWork.get_object(f'{self.tablename}_{id}')
        if not item_obj:
            statement = f"SELECT name FROM {self.tablename} WHERE id=?"
            self.cursor.execute(statement, (id,))
            result = self.cursor.fetchone()
            if result:
                item_obj = Category(*result)
                item_obj.id = id
                item_obj.other_id = f'{self.tablename}_{id}'
                UnitOfWork.add_object(item_obj)
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

            statement = f'SELECT name FROM categories WHERE id=?'
            self.cursor.execute(statement, (category_id,))
            get_category_result = self.cursor.fetchone()
            category_obj = Category(*get_category_result)

            subcat_obj = SubCategory(name, category_id)
            subcat_obj.id = item_id
            subcat_obj.category = category_obj

            statement = f'SELECT * FROM courses WHERE subcategory_id=?'
            self.cursor.execute(statement, (item_id,))
            get_courses_result = self.cursor.fetchall()
            for data in get_courses_result:
                course_obj = Course(*data[1:])
                subcat_obj.courses_list.append(course_obj)
            obj_list.append(subcat_obj)
        return obj_list

    def find_by_id(self, id):
        item_obj = UnitOfWork.get_object(f'{self.tablename}_{id}')
        if not item_obj:
            statement = f"SELECT name FROM {self.tablename} WHERE id=?"
            self.cursor.execute(statement, (id,))
            result = self.cursor.fetchone()
            if result:
                item_obj = SubCategory(*result)
                item_obj.id = id
                item_obj.other_id = f'{self.tablename}_{id}'
                UnitOfWork.add_object(item_obj)
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

            statement = f'SELECT name FROM courses_type WHERE id=?'
            self.cursor.execute(statement, (type_id,))
            get_type_result = self.cursor.fetchone()
            type_obj = CoursesType(*get_type_result)

            statement = f'SELECT name, category_id FROM subcategories WHERE id=?'
            self.cursor.execute(statement, (subcategory_id,))
            get_subcat_result = self.cursor.fetchone()
            subcat_obj = SubCategory(*get_subcat_result)

            category_id = get_subcat_result[1]

            statement = f'SELECT name FROM categories WHERE id=?'
            self.cursor.execute(statement, (category_id,))
            get_category_result = self.cursor.fetchone()
            category_obj = Category(*get_category_result)

            course_obj = Course(type_id, name, subcategory_id)
            course_obj.id = item_id
            course_obj.type = type_obj
            course_obj.subcategory = subcat_obj
            course_obj.subcategory.category = category_obj
            obj_list.append(course_obj)
        return obj_list

    def find_by_id(self, id):
        item_obj = UnitOfWork.get_object(f'{self.tablename}_{id}')
        if not item_obj:
            statement = f"SELECT type_id, name, subcategory_id FROM {self.tablename} WHERE id=?"
            self.cursor.execute(statement, (id,))
            result = self.cursor.fetchone()
            if result:
                item_obj = Course(*result)
                item_obj.id = id
                item_obj.other_id = f'{self.tablename}_{id}'
                UnitOfWork.add_object(item_obj)
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
            student_obj = Student(name, surname)
            student_obj.id = item_id

            statement = f"SELECT (SELECT type_id FROM courses WHERE courses.id = courses_students.course_id) AS type_id, " \
                        f"(SELECT name FROM courses WHERE courses.id = courses_students.course_id) AS name, " \
                        f"(SELECT subcategory_id FROM courses WHERE courses.id = courses_students.course_id) AS subcategory_id " \
                        f"FROM courses_students WHERE student_id=?"
            self.cursor.execute(statement, (item_id,))
            get_records_result = self.cursor.fetchall()
            for data in get_records_result:
                course_obj = Course(*data)
                student_obj.courses.append(course_obj)
            obj_list.append(student_obj)
        return obj_list

    def find_by_id(self, id):
        item_obj = UnitOfWork.get_object(f'{self.tablename}_{id}')
        if not item_obj:
            statement = f"SELECT name, surname FROM {self.tablename} WHERE id=?"
            self.cursor.execute(statement, (id,))
            result = self.cursor.fetchone()
            if result:
                item_obj = Student(*result)
                item_obj.id = id
                item_obj.other_id = f'{self.tablename}_{id}'
                UnitOfWork.add_object(item_obj)
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
            course_type_obj = CoursesType(name)
            course_type_obj.id = item_id
            obj_list.append(course_type_obj)
        return obj_list

    def find_by_id(self, id):
        item_obj = UnitOfWork.get_object(f'{self.tablename}_{id}')
        if not item_obj:
            statement = f"SELECT name FROM {self.tablename} WHERE id=?"
            self.cursor.execute(statement, (id,))
            result = self.cursor.fetchone()
            if result:
                item_obj = CoursesType(*result)
                item_obj.id = id
                item_obj.other_id = f'{self.tablename}_{id}'
                UnitOfWork.add_object(item_obj)
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
            course_student_obj = CoursesStudents(course_id, student_id)
            course_student_obj.id = item_id
            obj_list.append(course_student_obj)
        return obj_list

    def find_by_id(self, id):
        item_obj = UnitOfWork.get_object(f'{self.tablename}_{id}')
        if not item_obj:
            statement = f"SELECT course_id, student_id FROM {self.tablename} WHERE id=?"
            self.cursor.execute(statement, (id,))
            result = self.cursor.fetchone()
            if result:
                item_obj = CoursesStudents(*result)
                item_obj.id = id
                item_obj.other_id = f'{self.tablename}_{id}'
                UnitOfWork.add_object(item_obj)
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
