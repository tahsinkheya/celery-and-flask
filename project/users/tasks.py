from celery import shared_task
from celery.signals import task_postrun

@shared_task
def divide(x, y):
    from celery.contrib import rdb
    rdb.set_trace()
    import time
    time.sleep(5)
    return x / y

@shared_task
def sample_task(email):
    from project.users.views import api_call
    api_call(email)

@shared_task(bind=True)
def task_process_notification(self):
    try:
        if not random.choice([0, 1]):
            # mimic random error
            raise Exception()

        # this would block the I/O
        requests.post('https://httpbin.org/delay/5')
    except Exception as e:
        logger.error('exception raised, it would be retry after 5 seconds')
        raise self.retry(exc=e, countdown=5)

#will be called after each Celery task is executed,
@task_postrun.connect
def task_postrun_handler(task_id, **kwargs):
    from project.users.events import update_celery_task_status
    update_celery_task_status(task_id)