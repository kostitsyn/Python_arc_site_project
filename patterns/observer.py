from abc import ABC, abstractmethod


class Subject(ABC):
    def __init__(self):
        self._observers = list()

    @abstractmethod
    def attach(self, observer):
        pass

    @abstractmethod
    def detach(self, observer):
        pass

    @abstractmethod
    def notify(self):
        pass


class Observer(ABC):

    @abstractmethod
    def update(self, subject):
        pass
