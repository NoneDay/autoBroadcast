import os,sys,json
sys.path.append(os.path.realpath(os.curdir))
sys.path.append(os.path.realpath(os.curdir+"/../"))

from hnclic import glb
from hnclic.tasks import load_all_data
import time

t1 = time.time()
def test():
    with glb.db_connect() as conn:
        with conn.cursor(as_dict=True) as cursor:
            cursor.execute('SELECT * FROM zhanbao_tbl WHERE id=6817  ')
            row = cursor.fetchone()
            upload_path=f"{glb.config['UPLOAD_FOLDER']}\\{row['worker_no']}\\{row['id']}"
            return load_all_data.delay(json.loads(row['config_txt']),row['id'],upload_path=upload_path,userid=row['worker_no'])

result=test()
#r1 = add.delay(1, 2)
r_list = [result]
for r in r_list:
    while not r.ready():
        pass
    print(r.result)

t2 = time.time()

print('共耗时：%s' % str(t2-t1))