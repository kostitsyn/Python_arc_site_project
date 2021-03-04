from datetime import datetime

from abc import ABC, abstractmethod
from patterns.singletone import Singletone


class AbstractLog(ABC):
    @abstractmethod
    def msg(self, text):
        pass


class FileLog(AbstractLog):

    def msg(self, text):
        with open('log_file.txt', 'a', encoding='utf-8') as f:
            f.write(f'{text}\n')


class ConsoleLog(AbstractLog):

    def msg(self, text):
        print(text)


class Log(metaclass=Singletone):

    def __init__(self, strategy, name):
        self._strategy = strategy
        self.name = name

    @property
    def strategy(self):
        return self._strategy

    @strategy.setter
    def strategy(self, strategy):
        self._strategy = strategy

    def msg(self, text):
        self._strategy.msg(f'<--Лог сообщение:--> <-----{text}-----> '
                           f'<--{datetime.now().replace(microsecond=0)}-->')


if __name__ == '__main__':
    test1 = Log(ConsoleLog(), 'name_1')
    test2 = Log(ConsoleLog(), 'name_2')
    test3 = Log(ConsoleLog(), 'name_1')
    print(test1 is test2)
    print(test1 is test3)
