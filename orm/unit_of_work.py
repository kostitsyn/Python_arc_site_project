import threading


class UnitOfWork:
    current = threading.local()

    def __init__(self):
        self.new_objects = []
        self.dirty_objects = []
        self.remove_objects = []

    def set_mapper_registry(self, MapperRegistry):
        self.MapperRegistry = MapperRegistry

    def register_new(self, obj):
        self.new_objects.append(obj)

    def register_dirty(self, obj):
        self.dirty_objects.append(obj)

    def register_removed(self, obj):
        self.remove_objects.append(obj)

    def insert_new(self):
        for obj in self.new_objects:
            self.MapperRegistry.get_mapper(obj).insert(obj)
        self.new_objects.clear()

    def update_dirty(self):
        for obj in self.dirty_objects:
            self.MapperRegistry.get_mapper(obj).update(obj)
        self.new_objects.clear()

    def delete_removed(self):
        for obj in self.remove_objects:
            self.MapperRegistry.get_mapper(obj).delete(obj)
        self.new_objects.clear()

    def commit(self):
        self.insert_new()
        self.update_dirty()
        self.delete_removed()

    @staticmethod
    def new_current():
        UnitOfWork.set_current(UnitOfWork())

    @classmethod
    def set_current(cls, unit_of_work):
        cls.current.unit_of_work = unit_of_work

    @classmethod
    def get_current(cls):
        return cls.current.unit_of_work


class DomainObject:

    def mark_new(self):
        UnitOfWork.get_current().register_new(self)

    def mark_dirty(self):
        UnitOfWork.get_current().register_dirty(self)

    def register_dirty(self):
        UnitOfWork.get_current().register_removed(self)


