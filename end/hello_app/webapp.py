# Entry point for the application.
import flask,os,sys
sys.path.append(os.path.realpath(os.curdir))
from hello_app import app
import _mssql,pymssql    
from datetime import datetime
import json,requests
from hnclic import convert_main as ce,glb
import views,tianbao,user
import decimal

class DecimalDateEncoder(json.JSONEncoder):  
    def default(self, obj):  
        if isinstance(obj, decimal.Decimal):
            return round(float(obj),2)
        elif isinstance(obj, datetime.datetime):  
            return obj.strftime('%Y-%m-%d %H:%M:%S')  
        elif isinstance(obj, date):  
            return obj.strftime("%Y-%m-%d")  
        else:  
            return json.JSONEncoder.default(self, obj) 


app.config["JSON_AS_ASCII"]=False
app.json_encoder = DecimalDateEncoder

app.secret_key = os.urandom(24)

app.jinja_env.auto_reload=True

app.register_blueprint(views.mg, url_prefix='/mg')
app.register_blueprint(tianbao.tb, url_prefix='/tb')
################################

#app.config['wx_friendList']=requests.get("http://127.0.0.1:10001/allUserInfo").json()
#requests.post("http://127.0.0.1:10001/sendMessage",data='{"wxid":"flydao3000","content":"wx开始了"}'.encode('utf-8'))

if __name__ == '__main__':    

    glb.start_scheduler()
    #wx_receive_message()
    app.static_url_path="/static"
    app.static_folder= "..\\dist"

    from gevent import pywsgi
    server = pywsgi.WSGIServer(('0.0.0.0', 5050 if glb.is_test else 5000), app)
    server.serve_forever()
    #app.run(host='0.0.0.0')