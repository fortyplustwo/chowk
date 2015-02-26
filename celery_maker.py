from celery import Celery
from settings import CELERY_BROKER_URL

def make_celery():
    '''boilerplate thing from http://flask.pocoo.org/docs/0.10/patterns/celery/ for using celery'''
    celery = Celery('app', broker = CELERY_BROKER_URL)
    TaskBase = celery.Task
    
    '''
    class ContextTask(TaskBase):
        abstract = True
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)

    
    celery.Task = ContextTask
    '''
    return celery

celery = make_celery()
