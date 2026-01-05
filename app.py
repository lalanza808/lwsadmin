from logging.config import dictConfig
from lwsadmin.factory import create_app

app = create_app()

dictConfig({
    "version": 1,
    "disable_existing_loggers": True,
    "formatters": {
        "default": {
            "format": "[%(asctime)s] %(levelname)s in %(module)s: %(message)s",
        },
        "access": {
            "format": "%(message)s",
        }
    },
    "handlers": {
        "console": {
            "level": "INFO",
            "class": "logging.StreamHandler",
            "formatter": "default",
            "stream": "ext://sys.stdout",
        }
    },
    "loggers": {
        "gunicorn.error": {
            "handlers": ["console"] if app.debug else ["console"],
            "level": "INFO",
            "propagate": False,
        },
        "gunicorn.access": {
            "handlers": ["console"] if app.debug else ["console"],
            "level": "INFO",
            "propagate": False,
        }
    },
    "root": {
        "level": "DEBUG" if app.debug else "INFO",
        "handlers": ["console"] if app.debug else ["console"],
    }
})

if __name__ == "__main__":
    app.run()