import os
import sys

from celery import Celery
from celery.schedules import crontab
from django.conf import settings

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "nexify.settings")
BROKER_BACKEND = settings.CELERY_BROKER_URL

if "test" in sys.argv[1:]:
    BROKER_BACKEND = "memory://localhost"

app = Celery(
    "nexify",
    broker=BROKER_BACKEND,
    backend="redis://",
    include=["nexify.application.post.tasks"],
    task_acks_late=True,
    task_acks_on_failure_or_timeout=False,
    task_reject_on_worker_lost=True,
)

app.config_from_object("django.conf:settings")
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)

app.conf.beat_schedule = {
    "daily_post_recommendations_ist": {
        "task": "nexify.application.post.tasks.create_post_recommendations",
        "schedule": crontab(minute=30, hour=4),
    }
}

if __name__ == "__main__":
    app.start()
