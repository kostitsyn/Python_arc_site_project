PRAGMA foreign_keys=on;
BEGIN TRANSACTION;

DROP TABLE IF EXISTS categories;
CREATE TABLE categories (id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL UNIQUE, name VARCHAR (32));

DROP TABLE IF EXISTS subcategories;
CREATE TABLE subcategories (id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL UNIQUE,
                                          name VARCHAR (32),
                                          category_id INT UNSIGNED,
                                          FOREIGN KEY (category_id) REFERENCES categories(id));

DROP TABLE IF EXISTS courses_type;
CREATE TABLE courses_type (id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL UNIQUE, name VARCHAR (32));
INSERT INTO courses_type (name) VALUES ('interactive');
INSERT INTO courses_type (name) VALUES ('record');
INSERT INTO courses_type (name) VALUES ('webinar');

DROP TABLE IF EXISTS courses;
CREATE TABLE courses (id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL UNIQUE,
                                    type_id INT UNSIGNED,
                                    name VARCHAR (32),
                                    subcategory_id INT UNSIGNED,
                                    FOREIGN KEY (subcategory_id) REFERENCES subcategories(id),
                                    FOREIGN KEY (type_id) REFERENCES courses_type(id));

DROP TABLE IF EXISTS students;
CREATE TABLE students (id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL UNIQUE,
                                     name VARCHAR (32),
                                     surname VARCHAR (32));

DROP TABLE IF EXISTS courses_students;
CREATE TABLE courses_students (id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL UNIQUE,
                               course_id INT UNSIGNED,
                               student_id INT UNSIGNED,
                               FOREIGN KEY (course_id) REFERENCES courses(id),
                               FOREIGN KEY (student_id) REFERENCES students(id)
                               );

COMMIT TRANSACTION;