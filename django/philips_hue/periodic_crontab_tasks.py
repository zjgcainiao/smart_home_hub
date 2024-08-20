from django_celery_beat.models import PeriodicTask, CrontabSchedule
from django.utils.timezone import now
import json

# Define your schedules here


def create_periodic_tasks():
    # Create or get a crontab schedule
    crontab_schedule, _ = CrontabSchedule.objects.get_or_create(
        minute='0',
        hour='7',
        day_of_week='*',  # Every day of the week
        day_of_month='*',
        month_of_year='*',
    )

    # Define task with the schedule
    task_name = 'run_save_light_task_every_day'
    task, created = PeriodicTask.objects.get_or_create(
        crontab=crontab_schedule,
        name=task_name,
        task='philips_hue.tasks.save_lights_task',
        # args and kwargs are json, args is a list, kwargs is a dict
        args=json.dumps([]),  # Example: json.dumps([arg1, arg2])
        kwargs=json.dumps({}),  # Example: json.dumps({'kwarg1': value1})
        defaults={'start_time': now()}
    )

    if created:
        print(f'Task {task_name} created')
    else:
        print(f'Task {task_name} already exists')
