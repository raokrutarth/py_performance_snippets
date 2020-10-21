from typing import List
from timeit import timeit
import functools
import sys
from fastapi.security import HTTPBearer
import resource
from pprint import pformat
import logging
from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient
from starlette.requests import Request

logging.basicConfig(level=logging.INFO)


PAYLOAD = "A0000b"  # dummy payload to create memory ops
PAYLOAD_REPLICATION = 50000  # number of time the payload is replicated
NUM_CALLS = 1000  # number of times the target function is called by timeit

"""
    Sending param through a class
"""


class MyClass(HTTPBearer):

    def __init__(self, n: int):
        super().__init__()
        self.n = n

    def dependency(self, request: Request) -> List[str]:
        # making sure we can extract the HTTP request object from the endpoint call.
        assert isinstance(request, Request)

        return [PAYLOAD for _ in range(self.n)]


"""
    Sending param though a kwarg and decorator
"""


def decorator_with_arg(n: int):

    def decorator(func):

        @functools.wraps(func)
        def wrapper_decorator(*args, **kwargs):
            kwargs["my_param"] = [PAYLOAD for _ in range(n)]

            # making sure we can extract the HTTP request object from the endpoint call.
            assert isinstance(args["request"], Request)

            return func(*args, **kwargs)
        return wrapper_decorator

    return decorator


"""
    Target functions that do the same thing withing a fastapi app.
"""


def test_app() -> TestClient:
    """
        Sample REST application that uses FastAPI Dependency injection
        and a decorator prerequisite to provide different endpoints for
        testing performance.
    """
    app = FastAPI()

    @app.get("/object")
    async def get_new_obj_per_call(
        my_param: List[str] = Depends(MyClass(PAYLOAD_REPLICATION).dependency),
    ):
        assert len(my_param) == PAYLOAD_REPLICATION
        r = [x.lower() for x in my_param]
        return r

    @app.get("/decorator")
    @decorator_with_arg(PAYLOAD_REPLICATION)
    async def get_decorator_per_call(**kwargs):
        my_param = kwargs["my_param"]
        assert len(my_param) == PAYLOAD_REPLICATION
        r = [x.lower() for x in my_param]
        return r

    return TestClient(app)


client = test_app()


def test1():
    client.get("/object")


def test2():
    client.get("/decorator")


if __name__ == '__main__':

    gc_config = 'import gc; gc.enable()'  # timeit disables GC so neeed to re-enable it

    if sys.argv[1] == '1':
        logging.info("[+] Running object/per call test.")
        execution_time = timeit("test1()", setup=gc_config, number=NUM_CALLS, globals=globals())
    else:
        logging.info("[+] Running decorator per call test.")
        execution_time = timeit("test2()", setup=gc_config, number=NUM_CALLS, globals=globals())

    # log peak main memory usage
    peak_rss = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    logging.info(f"Peak RSS memory usage: {pformat(peak_rss)} kB")

    # log execution time
    logging.info(f"Execution time for {NUM_CALLS} calls: {execution_time}s")
