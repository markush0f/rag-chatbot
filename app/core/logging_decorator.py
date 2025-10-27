import logging
import time
from functools import wraps

logger = logging.getLogger("app")


def log_function_execution(level: str = "INFO"):
    """
    Decorator for logging execution details of a single function or method.
    Logs function name, args, execution time, and exceptions.
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            log_func = getattr(logger, level.lower(), logger.info)
            func_name = f"{func.__module__}.{func.__qualname__}"

            # Log start
            log_func(
                f"Executing: {func_name} args={args[1:] if len(args) > 1 else args}, kwargs={kwargs}"
            )
            start_time = time.perf_counter()

            try:
                result = func(*args, **kwargs)
                elapsed = (time.perf_counter() - start_time) * 1000

                # Log successful completion
                log_func(f"✅ {func_name} completed in {elapsed:.2f} ms")
                return result

            except Exception as e:
                elapsed = (time.perf_counter() - start_time) * 1000

                # Log exception
                logger.exception(f"Error in {func_name} after {elapsed:.2f} ms: {e}")
                raise

        return wrapper

    return decorator


def log_class_methods(level: str = "INFO"):
    """
    Class decorator that automatically applies logging to all public methods.
    It wraps every callable attribute of the class except private or magic methods.
    """

    def decorator(cls):
        for attr_name, attr_value in cls.__dict__.items():
            # Skip private or magic methods
            if attr_name.startswith("_") or not callable(attr_value):
                continue

            @wraps(attr_value)
            def wrapper(self, *args, __method=attr_value, __name=attr_name, **kwargs):
                log_func = getattr(logger, level.lower(), logger.info)
                func_name = f"{cls.__module__}.{cls.__name__}.{__name}"

                # Log start
                log_func(f"Executing: {func_name} args={args}, kwargs={kwargs}")
                start_time = time.perf_counter()

                try:
                    result = __method(self, *args, **kwargs)
                    elapsed = (time.perf_counter() - start_time) * 1000

                    # Log successful completion
                    log_func(f"{func_name} completed in {elapsed:.2f} ms")
                    return result

                except Exception as e:
                    elapsed = (time.perf_counter() - start_time) * 1000

                    # Log exception
                    logger.exception(
                        f"Error in {func_name} after {elapsed:.2f} ms: {e}"
                    )
                    raise

            setattr(cls, attr_name, wrapper)

        return cls

    return decorator
