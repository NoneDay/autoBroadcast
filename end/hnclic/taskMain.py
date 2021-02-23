# import gevent.monkey
# monkey.patch_all()

from celery import Celery
# from redisbeat.scheduler import RedisScheduler
from datetime import timedelta
from celery.schedules import crontab

zbTaskApp = Celery('Zhanbao', include=['hnclic.tasks'])
zbTaskApp.config_from_object('hnclic.taskConfig')

# start /b celery -A hnclic.taskMain worker --pool=solo --loglevel=info -n worker1@%h -E
# start /b celery -A hnclic.taskMain worker -P celery_pool_asyncio:TaskPool --loglevel=info -n worker2@%h
# start /b celery -A hnclic.taskMain worker -P eventlet --loglevel=info -n worker3@%h
# start /b celery -A hnclic.taskMain worker --pool=prefork --loglevel=info -n worker4@%h
# start /b flower --broker=redis://127.0.0.1:6379
# 
# -P eventlet

# flower -A hnclic.taskMain worker --pool=solo --loglevel=info 

if __name__ == '__main__':
    app.start()

    #schduler = RedisScheduler(app=app)
    #schduler.add(**{
    #    'name': 'sub-perminute',
    #    'task': 'proj.tasks.add',
    #    'schedule': timedelta(seconds=3),
    #    'args': (3, 12)
    #})
