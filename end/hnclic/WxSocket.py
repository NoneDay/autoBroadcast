################################
import websocket,time, threading
import json,requests

def on_message(ws, message):
    # print(ws)
    print(message)
    t_json=json.loads(message)
    content=t_json.get('content','')
    if content.startswith("id") or content.count("邀请你加入了群聊")>0:
        wxid=t_json['wxid']
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
    ws.run_forever()

def wx_receive_message():
    websocket.enableTrace(True)
    ws = websocket.WebSocketApp("ws://127.0.0.1:10001",
                                on_message=on_message,
                                on_error=on_error,
                                on_close=on_close)
    t = threading.Thread(target=start_websock, name='LoopThread',args=(ws,))
    t.start()
    t.join()
wx_receive_message()    