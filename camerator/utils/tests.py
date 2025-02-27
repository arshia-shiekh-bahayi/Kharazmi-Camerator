import threading
from datetime import datetime


class MockableDatetime(datetime):
    """Create a subclass of python's built-in datetime, so we can mock it"""

    pass


def test_concurrently(times):
    """
    Add this decorator to small pieces of code that you want to test concurrently to make sure they don't raise
    exceptions when run at the same time.  E.g., some Django views that do a SELECT and then a subsequent INSERT might
    fail when the INSERT assumes that the data has not changed since the SELECT.
    """

    def test_concurrently_decorator(test_func):
        def wrapper(*args, **kwargs):
            exceptions = []

            def call_test_func():
                try:
                    test_func(*args, **kwargs)
                except Exception as e:
                    exceptions.append(e)
                    raise

            threads = []
            for i in range(times):
                threads.append(threading.Thread(target=call_test_func))
            for t in threads:
                t.start()
            for t in threads:
                t.join()
            if exceptions:
                raise Exception(
                    f"test_concurrently intercepted {len(exceptions)} exceptions: {exceptions}"
                )

        return wrapper

    return test_concurrently_decorator
