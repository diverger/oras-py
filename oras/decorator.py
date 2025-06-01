__author__ = "Vanessa Sochat"
__copyright__ = "Copyright The ORAS Authors."
__license__ = "Apache-2.0"

import time
from functools import wraps

import requests.exceptions

import oras.auth
from oras.logger import logger


def ensure_container(func):
    """
    Ensure the first argument is a container, and not a string.
    """

    @wraps(func)
    def wrapper(cls, *args, **kwargs):
        if "container" in kwargs:
            kwargs["container"] = cls.get_container(kwargs["container"])
        elif args:
            container = cls.get_container(args[0])
            args = (container, *args[1:])
        return func(cls, *args, **kwargs)

    return wrapper


def ensure_auth(func):
    """
    Ensure authentication is loaded for the container's registry.
    This decorator should be applied after @ensure_container.
    """

    @wraps(func)
    def wrapper(cls, *args, **kwargs):
        # Get the container from the first argument (after ensure_container processing)
        container = None
        if "container" in kwargs:
            container = kwargs["container"]
        elif args:
            container = args[0]

        if container and hasattr(cls, "auth"):
            # Load auth for this specific container's registry without reloading configs
            cls.auth.ensure_auth_for_container(container)

        return func(cls, *args, **kwargs)

    return wrapper


def retry(attempts=5, timeout=2):
    """
    A simple retry decorator
    """

    def decorator(func):
        @wraps(func)
        def inner(*args, **kwargs):
            attempt = 0
            while attempt < attempts:
                try:
                    res = func(*args, **kwargs)
                    if res.status_code == 500:
                        try:
                            msg = res.json()
                            for error in msg.get("errors", []):
                                if isinstance(error, dict) and "message" in error:
                                    logger.error(error["message"])
                        except Exception:
                            pass
                        raise ValueError(f"Issue with {res.request.url}: {res.reason}")
                    return res
                except oras.auth.AuthenticationException as e:
                    raise e
                except requests.exceptions.SSLError:
                    raise
                except Exception as e:
                    sleep = timeout + 3**attempt
                    logger.info(f"Retrying in {sleep} seconds - error: {e}")
                    time.sleep(sleep)
                    attempt += 1
            return func(*args, **kwargs)

        return inner

    return decorator
