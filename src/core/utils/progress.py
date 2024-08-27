from functools import wraps

from tqdm import tqdm


def with_progress_bar(func):
    @wraps(func)
    def wrapper(iterable, *args, **kwargs):
        with tqdm(iterable, desc=f"Processing {func.__name__}") as t:
            return func(t, *args, **kwargs)

    return wrapper
