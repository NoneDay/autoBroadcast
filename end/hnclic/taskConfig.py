from datetime import timedelta
BROKER_URL = 'redis://127.0.0.1:6379' # 使用Redis作为消息代理

CELERY_RESULT_BACKEND = 'redis://127.0.0.1:6379/2' # 把任务结果存在了Redis

CELERY_TASK_SERIALIZER = 'msgpack' # 任务序列化和反序列化使用msgpack方案

CELERY_RESULT_SERIALIZER = 'json' # 读取任务结果一般性能要求不高，所以使用了可读性更好的JSON

CELERY_TASK_RESULT_EXPIRES = 60 * 60 * 24 # 任务过期时间

CELERYD_CONCURRENCY = 20  # 并发worker数
CELERYD_FORCE_EXECV = True    # 非常重要,有些情况下可以防止死锁
 
CELERYD_PREFETCH_MULTIPLIER = 1
 
CELERYD_MAX_TASKS_PER_CHILD = 100 # 每个worker最多执行万100个任务就会被销毁，可防止内存泄露
# CELERYD_TASK_TIME_LIMIT = 60    # 单个任务的运行时间不超过此值，否则会被SIGKILL 信号杀死 
# BROKER_TRANSPORT_OPTIONS = {'visibility_timeout': 90}
# 任务发出后，经过一段时间还未收到acknowledge , 就将任务重新交给其他worker执行
CELERY_DISABLE_RATE_LIMITS = True   

CELERY_ACCEPT_CONTENT = ['json', 'msgpack'] # 指定接受的内容类型

#CELERY_BEAT_SCHEDULER = 'redisbeat.RedisScheduler'
#CELERY_REDIS_SCHEDULER_URL = 'redis://127.0.0.1:6379/1'
#CELERY_REDIS_SCHEDULER_KEY = 'celery:beat:order_tasks'
