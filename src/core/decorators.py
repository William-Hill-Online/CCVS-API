# from https://www.calazan.com/retry-decorator-for-python-3/
import time
from functools import wraps


def retry(exceptions, timeout=6000, delay=3, backoff=2, logger=None):
    """
    Retry calling the decorated function using an exponential backoff.

    Args:
        exceptions: The exception to check. may be a tuple of
            exceptions to check.
        timeout: Timeout in seconds.
        delay: Initial delay between retries in seconds.
        backoff: Backoff multiplier (e.g. value of 2 will double the delay
            each retry).
        logger: Logger to use. If None, print.
    """

    def deco_retry(f):
        @wraps(f)
        def f_retry(*args, **kwargs):
            time_running = 0
            while timeout >= time_running:
                try:
                    return f(*args, **kwargs)
                except exceptions as err:
                    msg = f'{err}, Retrying in {delay} seconds...'
                    if logger:
                        logger.warning(msg)
                    time.sleep(delay)
                    time_running += delay
            return f(*args, **kwargs)

        return f_retry  # true decorator

    return deco_retry
