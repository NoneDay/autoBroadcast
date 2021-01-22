from celery import Celery
from redisbeat.scheduler import RedisScheduler
from datetime import timedelta
from celery.schedules import crontab

zbTaskApp = Celery('Zhanbao', include=['hnclic.tasks'])
zbTaskApp.config_from_object('hnclic.taskConfig')

#celery -A hnclic.taskMain worker --loglevel=info -P eventlet
if __name__ == '__main__':
    #app.start()

    schduler = RedisScheduler(app=app)
    schduler.add(**{
        'name': 'sub-perminute',
        'task': 'proj.tasks.add',
        'schedule': timedelta(seconds=3),
        'args': (3, 12)
    })
