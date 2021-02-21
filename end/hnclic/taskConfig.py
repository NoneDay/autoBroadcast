from datetime import timedelta
# Register your new serializer methods into kombu
from kombu.serialization import register
import json
from datetime import datetime
from time import mktime
import numpy as np

class MyEncoder(json.JSONEncoder):   
    def default(self, obj):
        if isinstance(obj, (np.int_, np.intc, np.intp, np.int8,
                            np.int16, np.int32, np.int64, np.uint8,
                            np.uint16, np.uint32, np.uint64)):
            return int(obj)

        elif isinstance(obj, (np.float_, np.float16, np.float32, np.float64)):
            return float(obj)

        elif isinstance(obj, (np.complex_, np.complex64, np.complex128)):
            return {'real': obj.real, 'imag': obj.imag}

        elif isinstance(obj, (np.ndarray,)):
            return obj.tolist()

        elif isinstance(obj, (np.bool_)):
            return bool(obj)

        elif isinstance(obj, (np.void)): 
            return None
        return json.JSONEncoder.default(self, obj)

# Encoder function      
def my_dumps(obj):
    return json.dumps(obj, cls=MyEncoder)

register('myjson', my_dumps, json.loads, 
    content_type='application/x-myjson',
    content_encoding='utf-8') 

# Tell celery to use your new serializer:


BROKER_URL = 'redis://127.0.0.1:6379' # 使用Redis作为消息代理

CELERY_RESULT_BACKEND = 'redis://127.0.0.1:6379/2' # 把任务结果存在了Redis

CELERY_TASK_SERIALIZER = 'myjson' # 任务序列化和反序列化使用msgpack方案

CELERY_RESULT_SERIALIZER = 'myjson' # 读取任务结果一般性能要求不高，所以使用了可读性更好的JSON

CELERY_TASK_RESULT_EXPIRES = 60 * 60 * 24 # 任务过期时间

CELERYD_CONCURRENCY = 20  # 并发worker数
CELERYD_FORCE_EXECV = True    # 非常重要,有些情况下可以防止死锁
 
CELERYD_PREFETCH_MULTIPLIER = 1
 
CELERYD_MAX_TASKS_PER_CHILD = 100 # 每个worker最多执行万100个任务就会被销毁，可防止内存泄露
# CELERYD_TASK_TIME_LIMIT = 60    # 单个任务的运行时间不超过此值，否则会被SIGKILL 信号杀死 
# BROKER_TRANSPORT_OPTIONS = {'visibility_timeout': 90}
# 任务发出后，经过一段时间还未收到acknowledge , 就将任务重新交给其他worker执行
CELERY_DISABLE_RATE_LIMITS = True   

CELERY_ACCEPT_CONTENT = ['myjson'] # 指定接受的内容类型

#CELERY_BEAT_SCHEDULER = 'redisbeat.RedisScheduler'
#CELERY_REDIS_SCHEDULER_URL = 'redis://127.0.0.1:6379/1'
#CELERY_REDIS_SCHEDULER_KEY = 'celery:beat:order_tasks'
