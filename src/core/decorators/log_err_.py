import datetime
import functools
import logging

# Set up logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)

formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

ch = logging.StreamHandler()
ch.setFormatter(formatter)
logger.addHandler(ch)


def log_err_(title, content):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as err:
                logger.info("Resonse Err: %s", err)
                message = {
                    "Timestamp": datetime.datetime.now(),
                    "Content": {"Title": title, "Content": content, "IsError": False},
                    "MessageType": "error",
                }
                logger.error(message)
                raise

        return wrapper

    return decorator
