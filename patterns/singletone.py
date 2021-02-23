class Singletone(type):
    _instances = []
    _names = []

    def __call__(cls, *args, **kwargs):
        name = args[0]

        if name not in cls._names:
            instance = super().__call__(*args, **kwargs)
            cls._names.append(name)
            cls._instances.append(instance)
            return instance
        else:
            for instance in cls._instances:
                if instance.name == name:
                    return instance


class Log(metaclass=Singletone):
    def __init__(self, name):
        self.name = name

    def msg(self, text):
        print(f'Лог сообщение: {text}')


# if __name__ == '__main__':
#     test1 = Log('name_1')
#     test2 = Log('name_2')
#     test3 = Log('name_1')
#     print(test1 is test2)  # False
#     print(test3 is test2)  # False
#     print(test1 is test3)  # True




