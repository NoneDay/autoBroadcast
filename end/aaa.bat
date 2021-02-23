conda activate my_flask2

start /b celery -A hnclic.taskMain beat -l info
start /b celery -A hnclic.taskMain worker --pool=solo --loglevel=info -n worker1@%h
start /b celery -A hnclic.taskMain worker --pool=solo --loglevel=info -n worker2@%h
start /b celery -A hnclic.taskMain worker --pool=solo --loglevel=info -n worker3@%h
start /b celery -A hnclic.taskMain worker --pool=solo --loglevel=info -n worker4@%h


start /b celery flower -A hnclic.taskMain

start /b python ./hello_app/webapp.py