
from celery import Celery
from settings import CELERY_BROKER_URL, CELERY_BACKEND

# Initialize an instance of Celery
tasks_app = Celery('tasks', broker=CELERY_BROKER_URL,
                   backend=CELERY_BACKEND)

tasks_app.conf.update(
    # enable STARTED status for celery task
    # needed to know if a task exists
    task_track_started=True,
    # result_expires=3600,
)
