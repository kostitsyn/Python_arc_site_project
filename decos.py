from time import time
from log_settings import Log, FileLog, ConsoleLog

logger = Log(ConsoleLog(), 'main_log')


def debug(func):
    def wrapper(*args):
        start = time()
        result = func(*args)
        end = time()
        logger.msg(f"Время выполнения функции {func.__name__}: {round(end - start, 6)} сек")
        return result
    return wrapper
