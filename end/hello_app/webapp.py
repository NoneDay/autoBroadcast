#import nest_asyncio
#nest_asyncio.apply()
#
#from gevent import monkey
## 猴子补丁，将之前代码当中所有不契合协程的代码修改为契合
#monkey.patch_all()
# Entry point for the application.
import flask,os,sys
sys.path.append(os.path.realpath(os.curdir))
from hello_app import app
import _mssql,pymssql    
import datetime
import json,requests
from hnclic import convert_main as ce,glb
import views,tianbao,user
import decimal
import numpy as np


class DecimalDateEncoder(json.JSONEncoder):  
    def default(self, obj):  
        if isinstance(obj, decimal.Decimal):
            return round(float(obj),2)
        elif isinstance(obj, datetime.datetime):  
            return obj.strftime('%Y-%m-%d %H:%M:%S')  
        elif isinstance(obj, datetime.date):  
            return obj.strftime("%Y-%m-%d")  
        elif isinstance(obj, (np.int_, np.intc, np.intp, np.int8,
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


app.config["JSON_AS_ASCII"]=False
app.json_encoder = DecimalDateEncoder

app.secret_key = os.urandom(24)

#app.jinja_env.auto_reload=True

app.register_blueprint(views.mg, url_prefix='/mg')
app.register_blueprint(tianbao.tb, url_prefix='/tb')
app.static_url_path="/static"
app.static_folder= "..\\..\\front\\dist"
glb.start_scheduler()
################################

#app.config['wx_friendList']=requests.get("http://127.0.0.1:10001/allUserInfo").json()
#requests.post("http://127.0.0.1:10001/sendMessage",data='{"wxid":"flydao3000","content":"wx开始了"}'.encode('utf-8'))
def penevt_main():
    from gevent.pywsgi import WSGIServer
    server = WSGIServer(('0.0.0.0', 5050 if glb.is_test else 5000), app)
    server.serve_forever()
    #app.run(host='0.0.0.0')
def twisted_main():
    # https://blog.csdn.net/bamboo_2001/article/details/108243592 windows下使用Twisted发布flask应用
    global app
    from twisted.web.server import Site
    from twisted.web.wsgi import WSGIResource
    from twisted.internet import reactor
    from twisted.python import log
    log.startLogging(sys.stdout)
    resource=WSGIResource(reactor,reactor.getThreadPool(),app)
    reactor.suggestThreadPoolSize(100)
    site=Site(resource)
    reactor.listenTCP(5050 if glb.is_test else 5000, site)
    
    reactor.run()

# set PYTHONPATH=F:\autoBroadcast-master\end\;twistd -n web --port tcp:5000 --wsgi hello_app.webapp.app 
if __name__ == '__main__':    
    
    #wx_receive_message()
    if glb.is_test==True:
        penevt_main()
    else:
        twisted_main()
