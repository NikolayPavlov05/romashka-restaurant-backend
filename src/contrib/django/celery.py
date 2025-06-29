from django.conf import settings
from config.celery import app as celery_app


def celery_task(*args, **opts):
    if queue := opts.get("queue"):
        opts["queue"] = queue if settings.PRODUCTION else "default"
    return celery_app.task(*args, **opts)
