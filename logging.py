from patterns.singletone import Singletone


class Log(metaclass=Singletone):
    def __init__(self, name):
        self.name = name

    def msg(self, text):
        print(f'<---Лог сообщение:---> <--------{text}-------->')


if __name__ == '__main__':
    test1 = Log('name_1')
    test2 = Log('name_2')
    test3 = Log('name_1')
    print(test1 is test2)
    print(test1 is test3)