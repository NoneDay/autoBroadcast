import os,sys,json
sys.path.append(os.path.realpath(os.curdir))
sys.path.append(os.path.realpath(os.curdir+"/../"))

from hnclic import glb
from hnclic.tasks import load_all_data
import time

t1 = time.time()
 
with glb.db_connect() as conn:
    with conn.cursor(as_dict=True) as cursor:
        cursor.execute('SELECT * FROM zhanbao_tbl WHERE id=4894 ')
        row = cursor.fetchone()
        upload_path=f"{glb.config['UPLOAD_FOLDER']}\\{row['worker_no']}\\{row['id']}"
        result=load_all_data(json.loads(row['config_txt']),row['id'],upload_path=upload_path,userid=row['worker_no'])

#r1 = add.delay(1, 2)
r_list = [result]
for r in r_list:
    while not r.ready():
        pass
    print(r.result)

t2 = time.time()

print('共耗时：%s' % str(t2-t1))