import os,json,requests,sys,re
sys.path.append(os.path.realpath(os.curdir))
from datetime import datetime
from flask import request
import pymssql,asyncio
from queue import Queue
from hnclic import convert_main as ce
from apscheduler.schedulers.background import BackgroundScheduler#,AsyncIOScheduler
from redis import StrictRedis, ConnectionPool
import qywx
import hnclic.tasks

def is_debug():
    gettrace = getattr(sys, 'gettrace', None)
    if gettrace is None:
        return False
    elif gettrace():
        return True
    else:
        return False

is_test=is_debug()

from configobj import ConfigObj 
if(is_test):
    ini = ConfigObj("setting.test.ini",encoding='UTF8')
else:
    ini = ConfigObj("setting.ini",encoding='UTF8')

__pool = ConnectionPool(host=ini['redis']['host'], port=ini['redis']['port'], db=ini['redis']['db'], password=ini['redis']['password'])
redis = StrictRedis(connection_pool=__pool)
__pool3 = ConnectionPool(host=ini['redis']['host'], port=ini['redis']['port'], db=3, password=ini['redis']['password'])
redis3 = StrictRedis(connection_pool=__pool3)

_qywx=qywx.Qywx(corpid=ini['qywx']['corpid'],corpsecret=ini['qywx']['corpsecret'],is_log=False,log_path=ini['qywx']['log_path'],redis=redis)



def _sendWxMessage(res):
    """
    1.本接口通过判断管理员是否拥有发送者账号的管理权限进行权限校验。
    如果是职场群，发送者账号是职场主管的账号
    如果是团队群，发送者账号是团队主管的账号
    如果是普通(自建)群，发送者账号是群主的账号
    2.针对不同类型群所使用的群关联信息也不相同。
    如果是职场群，使用职场号(opt=1, opt_number=职场号)
    如果是团队群，使用团队主管账号(opt=1, opt_number=团队主管账号)
    如果是普通(自建)群，使用群主账号(opt=1, opt_number=群主账号)

    http://yzl.hn.clic/yzl/imSendMessage 用户验证参数  userid password  其他参数   opt：必须 1:职场群 2:团队群 3:普通群
    opt_number: 必须 opt 1-职场号 2-团队主管uid 3-普通群群号（群号为１开头）
    force_to: 可选 ["ALL"]-@所有人  ["uid1","uid2"..]-成员列表，仅针对文本消息提供@功能
    type：必须，0 表示文本消息, 1 表示图片
    body: 必须，最大长度4000字符，JSONString格式。type为0时-"{\"msg\":\"xxx\"}" type为1时-上传多媒体文件接口返回的body内容  

    http://yzl.hn.clic/yzl/SendNewsMessage 用户验证参数  userid password  
    其他参数   touser 发给谁
    title  标题
    desc  描述
    msg   内容
    msgurl  url
    如果post 图像或者html文件 则 发送为图文消息  否则 发送为文本消息
    """
    wxid=res['wxid']
    if wxid is None or wxid.strip()=='':
        return    
    content=res['content']
    if wxid.startswith("qywx:"):
        if res["type"]=="sendMessage":
            _qywx.send_msg_message(content,touser=wxid[5:])
        elif  res["type"]=="sendImage":
            _qywx.send_image_message(content,touser=wxid[5:])
        elif  res["type"]=="sendFile":
            _qywx.send_file_message(content,touser=wxid[5:])
    elif wxid.startswith("yzl:"):
        if res['type']=="sendMessage":
            #云助理开发环境
            res=requests.post(ini['yzl']['url'],
                    data={"userid":ini['yzl']['userid'],
                    "pwd":ini['yzl']['pwd'],
                    "opt":3,
                    "opt_number":wxid[4:],
                    "type":0,
                    "msg":content # .replace("%",'%25'),
                    })
            print(res.text)
        elif res['type']=="sendImage":
            with open(content,'rb') as f:
                data = f.read()
            files ={'image':('20200528143836.png',data,'application/octet-stream')}
            #files ={'image':('20200528143836.png',open('F:\\hello_flask\\文档/微信图片_20200528143836.png','rb'),'application/octet-stream')}
            res=requests.post(ini['yzl']['url'],params={"userid":ini['yzl']['userid'],"pwd":ini['yzl']['pwd'],"opt":3,"opt_number":wxid[4:],"type":1},files=files)
            print(res)
    
    elif wxid.startswith("yfw:"):
        if res['type']=="sendMessage":
            #云助理开发环境
            requests.post(ini['yfw']['url'],params={"userid":ini['yfw']['userid'],"pwd":ini['yfw']['userid'],"touser":wxid[4:],"msg":content,"title":"战报推送"})
        elif res['type']=="sendImage":
            with open(content,'rb') as f:
                data = f.read()
            files ={'image':('20200528143836.png',data,'application/octet-stream')}
            #files ={'image':('20200528143836.png',open('F:\\hello_flask\\文档/微信图片_20200528143836.png','rb'),'application/octet-stream')}
            res=requests.post(ini['yfw']['url'],params={"userid":ini['yfw']['userid'],"pwd":ini['yfw']['userid'],"touser":wxid[4:],"title":"战报推送"},files=files)
    else:
        pass
        #msg=f'{{"wxid":"{wxid}","content":"{content}"}}'
        #msg=json.dumps(msg)[1:-1].encode().decode('unicode_escape').encode('utf-8','surrogatepass')
        #requests.post(f"http://localhost:10001/{res['type']}",data=msg)

class TestQueue():
    def put(self,res):
        _sendWxMessage(res)
    def sendMessage(self):
        pass

class PyQueue():
    def __init__(self, *args, **kwargs):
        self.q=Queue()
    def put(self,res):
        self.q.put(res)
        if is_test and isinstance(scheduler, RedisScheduler)==False:
            self.sendMessage()
    def sendMessage(self):
        if self.q.empty():
            return
        res=self.q.get_nowait()
        _sendWxMessage(res)
        self.q.task_done()

class RedisQueue():
    def put(self,res):
        if is_test:
            redis.hincrby("zb:tj",res['type'])
            _sendWxMessage(res)
        else:
            redis.lpush("zb:wx_queue",json.dumps(res))
    def sendMessage(self):
        aaa=redis.rpop("zb:wx_queue")
        if aaa is None:
            return
        res=json.loads(aaa.decode()) 
        wxid=res['wxid']
        redis.hincrby("zb:tj",res['type'])
        _sendWxMessage(res)

config={}
config['UPLOAD_FOLDER'] = ini['file']['UPLOAD_FOLDER']
config['ALLOWED_EXTENSIONS'] = {'txt', 'html', 'xlsx','pptx','csv','md'}
config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024 #上传文件大小限制

def test_env():
    if is_test:
        def user_login():
            userid,password=request.json['username'],request.json['password']
            return json.loads(ini['user_login']['test_user_json'] )
        def user_verify():
            token=request.headers.get("Authorization")
            if(token==None):
                return {"errcode":-1,"errmsg":"缺失Token"}
            return json.loads(ini['user_login']['test_user_json'] )
        return (TestQueue(),user_login,user_verify)
    else:
        def user_login():
            userid,password=request.json['username'],request.json['password']
            return requests.post(ini['user_login']['login_url'],{'userid':userid,'password':password,'attrib':'mobile,phone,mail'}).json()
        def user_verify():
            token=request.headers.get("Authorization")
            if(token==None):
                return {"errcode":-1,"errmsg":"缺失Token"}
            return requests.post(ini['user_login']['verify_url'],data={'access_token':token[len('Bearer '):]}).json()
        return (RedisQueue(),user_login,user_verify)

msg_queue,user_login,user_verify=test_env()

def db_connect():
    db_str=ini['db']
    return pymssql.connect(server=db_str['server'],port=db_str['port'],user=db_str['user'], password=db_str['password'],database=db_str['database'])

def user_report_upload_path(curr_report_id,created=False)->str:
    with db_connect() as conn:
        with conn.cursor(as_dict=True) as cursor:
            cursor.execute('SELECT worker_no  FROM zhanbao_tbl WHERE id=%d', curr_report_id)
            userid=cursor.fetchone()['worker_no']
            ret=f"{config['UPLOAD_FOLDER']}\\{userid}\\{curr_report_id}"
            if not os.path.exists(ret) and created:
                os.makedirs(ret)
            return ret

#定时任务，用户定义的战报
def zb_execute(rptid,config_data,userid,report_name=""):
    print(f"start:{rptid}")
    #loop = asyncio.new_event_loop()    
    try:
        redis.sadd("zb:executing",rptid)
        #asyncio.set_event_loop(loop)
        asyncio.run(ce.files_template_exec(rptid,config_data,userid,config['UPLOAD_FOLDER'],wx_queue=msg_queue))
    except Exception as e:
        msg_queue.put({'type':'sendMessage',"wxid":'qywx:'+userid,"content":f"{report_name},执行报错。错误信息："+ str(e)})
        print({'type':'sendMessage',"wxid":'qywx:'+userid,"content":f"{report_name},执行报错。错误信息："+ str(e)})
    finally:
        redis.srem("zb:executing",rptid)
        #loop.close()
    print(f'new Tick! The time is:{datetime.now()} \tuserid:{userid}\trptid={rptid} ')



from apscheduler.executors.pool import ThreadPoolExecutor, ProcessPoolExecutor
scheduler = BackgroundScheduler(#executors = { 'zb_processpool': ProcessPoolExecutor()}
                        )
def start_scheduler():
    # 间隔3秒钟执行一次   秒 分钟 小时 日 月 周 年 * * * * * ?
    #1）Seconds Minutes Hours DayofMonth Month DayofWeek Year
    #2）Seconds Minutes Hours DayofMonth Month DayofWeek
    if(is_test==False):
        
        with db_connect() as conn:
            with conn.cursor(as_dict=True) as cursor:
                cursor.execute('SELECT * FROM zhanbao_tbl WHERE cron_str is not null and cron_start=1 ')
                row = cursor.fetchone()
                while row:
                    if row['cron_str'].count("  ")>0:
                        print(f"{row['id']}的cron 不正确")
                    else:
                        cron_arr=row['cron_str'].split()
                        if len(cron_arr)>5:
                            print(f" start:{row['id']}:{row['cron_str']}")
                            try:
                                scheduler.add_job(hnclic.tasks.zb_execute.delay, 'cron', id=str(row['id']),max_instances=10,#executor="zb_processpool",
                                args=(row['id'],json.loads(row['config_txt']),row['worker_no'],row['report_name']),#
                                day_of_week=cron_arr[5], month=cron_arr[4], day=cron_arr[3],
                                hour=cron_arr[2],minute=cron_arr[1],second=cron_arr[0]
                                )
                            except Exception as e:
                                print(e)
                        else:
                            msg_queue.put({'type':'sendMessage',"wxid":'qywx:'+row['worker_no'],"content":f"{row['report_name']},定时设置不正确。分段长度必须大于5"})
                            print(f"{row['id']}的cron 不正确")
                    row = cursor.fetchone()
        scheduler.add_job(msg_queue.sendMessage,'interval', max_instances=10,seconds=1)
        scheduler.start()

def update_scheduler(id,cron_str,cron_start,config_data,userid,report_name):
    if scheduler.get_job(str(id)):
        scheduler.remove_job(str(id))
    if str(cron_start)=='1':
        cron_arr=cron_str.split()
        if len(cron_arr)>5:
            scheduler.add_job(hnclic.tasks.zb_execute.delay, 'cron', id=str(id),max_instances=1,#executor="zb_processpool",
                args=(id,config_data,userid,report_name),#
                        day_of_week=cron_arr[5], month=cron_arr[4], day=cron_arr[3],
                        hour=cron_arr[2],minute=cron_arr[1],second=cron_arr[0]
                    )
###################################
login_getData_template_dict=dict()

with db_connect() as conn:
    with conn.cursor(as_dict=True) as cursor:
        cursor.execute('SELECT * FROM sys_register')
        allSysRegister=cursor.fetchall()
for idx,one in enumerate(allSysRegister):
    redis.hset("zb:sys_register",one['name'],one['json_txt'])
    login_getData_template_dict[one['name']]={**one,**json.loads(one['json_txt'])}

def getSysRegister(name):
    #result=login_getData_template_dict.get(name)
    #if result is not None:
    #    return result
    result=redis.hget("zb:sys_register",name)
    if result is None:
        with db_connect() as conn:
            with conn.cursor(as_dict=True) as cursor:
                cursor.execute('SELECT * FROM sys_register where name=%s',name)
                result=cursor.fetchone()
                if result is None:
                    return None
                redis.hset("zb:sys_register",result['name'],result['json_txt'])
                result=result['json_txt']
    return json.loads(result)

def getSysByUser(userid):
    ret=[]
    for k,v in login_getData_template_dict.items():
        if re.search(v['allow_userid'],userid):
            ret.append(v)
    return ret


