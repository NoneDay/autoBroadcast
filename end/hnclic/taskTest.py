import os,sys
sys.path.append(os.path.realpath(os.curdir))
sys.path.append(os.path.realpath(os.curdir+"/../"))

from hnclic.tasks import add,zb_execute
import time

t1 = time.time()

r1 = add.delay(1, 2)
r2 = add.delay(2, 4)
r3 = add.delay(3, 6)
r4 = add.delay(4, 8)
r5 = add.delay(5, 10)
r6=zb_execute.delay(4180)
r_list = [r1, r2, r3, r4, r5,r6]
for r in r_list:
    while not r.ready():
        pass
    print(r.result)

t2 = time.time()

print('共耗时：%s' % str(t2-t1))