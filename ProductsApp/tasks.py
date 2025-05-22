# app_name/tasks.py
from celery import shared_task
import time

@shared_task
def sleep():
    for i in range(10):
        print(f"sleep >>>>> {i}")
        time.sleep(1)
