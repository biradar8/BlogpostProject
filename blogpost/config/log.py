from logging.config import dictConfig

from blogpost.config.settings import DevConfig, config


def configure_logging():
    dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "console_formatter": {
                    "class": "logging.Formatter",
                    "format": "%(levelname)s:     %(message)s",
                },
                "file_formatter": {
                    "class": "logging.Formatter",
                    "datefmt": "%Y-%m-%dT%H:%M:%S",
                    "format": "%(levelname)-8s | %(asctime)-20s | %(name)-20s | Line:%(lineno)-3d | %(message)s",
                },
            },
            "handlers": {
                "console": {
                    "class": "logging.StreamHandler",
                    "level": "DEBUG",
                    "formatter": "console_formatter",
                },
                "file_handler": {
                    "class": "logging.FileHandler",
                    "level": "DEBUG",
                    "formatter": "file_formatter",
                    "filename": "blogpost/api.log",
                },
            },
            "loggers": {
                "uvicorn": {"handlers": ["console", "file_handler"], "level": "INFO"},
                "blogpost": {
                    "handlers": ["console", "file_handler"],
                    "level": "INFO",
                    "propagate": False,
                },
                "blogpost.auth.router": {
                    "handlers": ["console", "file_handler"],
                    "level": "DEBUG" if isinstance(config, DevConfig) else "INFO",
                    "propagate": False,
                },
                "blogpost.auth.utils": {
                    "handlers": ["console", "file_handler"],
                    "level": "DEBUG" if isinstance(config, DevConfig) else "INFO",
                    "propagate": False,
                },
                "blogpost.config.settings": {
                    "handlers": ["console", "file_handler"],
                    "level": "DEBUG" if isinstance(config, DevConfig) else "INFO",
                    "propagate": False,
                },
                "blogpost.posts.router": {
                    "handlers": ["console", "file_handler"],
                    "level": "DEBUG" if isinstance(config, DevConfig) else "INFO",
                    "propagate": False,
                },
            },
            "root": {"handlers": ["console", "file_handler"], "level": "INFO"},
        }
    )
