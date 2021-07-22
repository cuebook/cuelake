import os
from django.conf import settings
from celery import Celery
from genie.routineTasks import orphanJobsChecker

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "app.settings")

app = Celery("app", broker=settings.REDIS_BROKER_URL)

app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()

# @app.on_after_configure.connect
# def setup_periodic_tasks(sender, **kwargs):
#     sender.add_periodic_task(30.0, orphanJobsChecker.s(), name='Orphan Jobs Checker')

@app.task(bind=True)
def debug_task(self):
    """
    Celery debug task
    """
    print(f"Request: {self.request!r}")