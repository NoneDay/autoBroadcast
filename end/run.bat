call conda activate my_flask2
start /b celery beat   -A hnclic.taskMain  -l info
start /b celery worker -A hnclic.taskMain --pool=solo --loglevel=info -n worker1@%h
start /b celery worker -A hnclic.taskMain --pool=solo --loglevel=info -n worker2@%h
start /b celery worker -A hnclic.taskMain --pool=solo --loglevel=info -n worker3@%h
start /b celery worker -A hnclic.taskMain --pool=solo --loglevel=info -n worker4@%h
start /b celery flower -A hnclic.taskMain

set PYTHONPATH=E:\智能播报\end\
start /b python ./hello_app/webapp.py
twistd -n web --port tcp:5000 --wsgi hello_app.webapp.app 