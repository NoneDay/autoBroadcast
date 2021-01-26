import psutil,time,subprocess,json,requests,datetime
import websocket, threading
import requests,os
from hnclic import glb

redis=glb.redis
#redis.pipeline().set("zb:wx:14100298",1).expire("zb:wx:14100298",60*60*24).execute()

def on_message(ws, message):
    # print(ws)
    print(message)
    t_json=json.loads(message)
    wxid=t_json['wxid']
    redis.pipeline().set(f"zb:wx:{wxid}",1).expire(f"zb:wx:{wxid}",60*60*36).execute()
    
    content=t_json.get('content','')
    if content.startswith("id") or content.count("邀请你加入了群聊")>0:
        
        requests.post(f"http://localhost:10001/sendMessage",
        data=f'{{"wxid":"{wxid}","content":"{wxid}" }}'.encode('utf-8','surrogatepass'))

def on_error(ws, error):
    # print(ws)
    print(error)

def on_close(ws):
    # print(ws)
    print("### closed ###")
    print("reconnect")
    
def start_websock(ws):
    try:
        ws.run_forever()
    except Exception as e:
        print(e)
        wx_receive_message()

def wx_receive_message():
    websocket.enableTrace(True)
    ws = websocket.WebSocketApp("ws://127.0.0.1:10001",
                                on_message=on_message,
                                on_error=on_error,
                                on_close=on_close)
    t = threading.Thread(target=start_websock, name='LoopThread',args=(ws,))
    t.start()
#wx_receive_message()

######################

def list_all_children(parent,all_p=list()):
    #print(parent.cmdline())
    all_p.append(parent)
    for child in parent.children():
        list_all_children(child,all_p)
    
def kill_all(parent,max_limit=0):
    all_p=list()
    list_all_children(parent,all_p)
    max_vms=0
    for one in all_p:
        if psutil.pid_exists(one.pid):
            if max_vms<one.memory_info().vms:
                max_vms=one.memory_info().vms 
    #print(max_vms)
    if max_vms>max_limit:
        #requests.post(f"http://localhost:10001/sendMessage",
        #        data=f'{{"wxid":"flydao3000","content":"当前ID： {str(redis.smembers("zb:executing"))}" }}'
        #        .encode('utf-8','surrogatepass')) 
        #redis.delete("zb:executing")
        for one in all_p:
            if psutil.pid_exists(one.pid):
                one.terminate()
        return True,max_vms
    return False,max_vms

def start_proc():
    zb_dir=os.getcwd()
    zb_exe=f"python {zb_dir}\hello_app\\webapp.py"
    return subprocess.Popen(f"{zb_exe} ", shell=True)

if __name__ == '__main__':
    file_name="proc.pid"
    try:
        if(os.path.exists(file_name)):
            with open(file_name, 'r') as f:
                proc_id = f.read()
                p=psutil.Process(int(proc_id))
                kill_all(p,0)
    except:
        pass
    proc=start_proc()
    p=psutil.Process(proc.pid)

    with open(file_name, 'w') as f:
        f.write( str(proc.pid) )

    time.sleep(10)
    all_p=list_all_children(p)
    while True:
        (is_killed,max_vms)=kill_all(p,max_limit=1024*1024*1024*1)
        if is_killed:
            proc=start_proc()
            p=psutil.Process(proc.pid)
            #requests.post(f"http://localhost:10001/sendMessage",
            #        data=f'{{"wxid":"flydao3000","content":"最大内存{max_vms/1000000}M，重启成功。{str(datetime.datetime.now())}" }}'
            #        .encode('utf-8','surrogatepass'))
        time.sleep(10)