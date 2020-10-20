from typing import List
from timeit import timeit
import functools
import sys
from fastapi.security import HTTPBearer
import resource
import tracemalloc
from pprint import pformat
import logging


logging.basicConfig(level=logging.INFO)


PAYLOAD = "A0000b"
PAYLOAD_REPLICATION = 50000  # number of time the payload is replicated
NUM_CALLS = 50000  # number of times the target function is called by timeit

"""
    Sending param through a class
"""


class MyClass(HTTPBearer):

    def __init__(self):
        super().__init__()

    def foo(self, n: int):
        return [PAYLOAD for _ in range(n)]


"""
    Sending param though a kwarg and decorator
"""


def decorator_with_arg(n: int):

    def decorator(func):
        @functools.wraps(func)
        def wrapper_decorator(*args, **kwargs):
            kwargs["my_param"] = [PAYLOAD for _ in range(n)]
            return func(*args, **kwargs)
        return wrapper_decorator

    return decorator


"""
    Target functions that do the same thing.
"""


def my_target_func1(my_param: List[str] = MyClass().foo(PAYLOAD_REPLICATION)):
    assert len(my_param) == PAYLOAD_REPLICATION
    a = map(str.lower, my_param)
    return a


@decorator_with_arg(n=PAYLOAD_REPLICATION)
def my_target_func2(my_param: List[str]):
    assert len(my_param) == PAYLOAD_REPLICATION
    a = map(str.lower, my_param)
    return a


def test1():
    my_target_func1()


def test2():
    my_target_func2()


if __name__ == '__main__':

    gc_config = 'import gc; gc.enable()'  # timeit disables GC so neeed to re-enable it

    if sys.argv[1] == '1':
        logging.info("[+] Running object/per call test.")
        execution_time = timeit("test1()", setup=gc_config, number=NUM_CALLS, globals=globals())
    else:
        logging.info("[+] Running decorator per call test.")
        execution_time = timeit("test2()", setup=gc_config, number=NUM_CALLS, globals=globals())

    peak_rss = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    logging.info(f"Peak RSS memory usage: {pformat(peak_rss)} kB")

    # log execution time
    logging.info(f"Execution time for {NUM_CALLS} calls: {execution_time}s")
