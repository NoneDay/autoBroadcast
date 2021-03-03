from datetime import datetime
import requests,os,sys, traceback
from flask import Flask, render_template, request,session,flash,make_response,redirect,send_from_directory,session,Blueprint,url_for,jsonify
from flask import  has_request_context, copy_current_request_context
from hello_app import app
from hnclic import convert_main as ce,glb
import json,asyncio
from werkzeug.utils import secure_filename
import pymssql
from data_adapter.DataInterface import DataInterface
import hnclic.tasks
import pandas as pd
from functools import wraps
from concurrent.futures import Future, ThreadPoolExecutor

mg = Blueprint('mg', __name__, template_folder='templates')

def run_async(func):
    @wraps(func)
    def _wrapper(*args, **kwargs):
        call_result = Future()
        def _run():
            loop = asyncio.new_event_loop()
            try:
                result = loop.run_until_complete(func(*args, **kwargs))
            except Exception as error:
                call_result.set_exception(error)
            else:
                call_result.set_result(result)
            finally:
                loop.close()
 
        loop_executor = ThreadPoolExecutor(max_workers=1)
        if has_request_context():
            _run = copy_current_request_context(_run)
        loop_future = loop_executor.submit(_run)
        loop_future.result()
        return call_result.result()
    return _wrapper

@mg.route("/chg/<int:id>")
def chg(id):
    if(session['old_userid']==glb.ini['user_login']['test_user']):
        session['userid']=id
        return f"当前用户已修改为{id}"
    return "你没有权限！"

@mg.errorhandler(500)
def errorhandler_500(error):
    exc_type, exc_value, exc_traceback = sys.exc_info() # most recent (if any) by default
    traceback_details = {
                "errcode":1,
                'filename': exc_traceback.tb_frame.f_code.co_filename,
                'lineno' : exc_traceback.tb_lineno,
                'name'  : exc_traceback.tb_frame.f_code.co_name,
                'type'  : exc_type.__name__,
                'message' : str(exc_value), # or see traceback._some_str()
                }        
    resp = make_response(jsonify(traceback_details), 500)
    return resp

@mg.route("/initDatafrom/", methods=['GET', 'POST'])
@run_async
async def initDatafrom():
    data_from=request.json['data_from']        
    if data_from['type']=="file":
        upload_path=glb.user_report_upload_path(request.json['curr_report_id']  )
        filename=os.path.join(upload_path, data_from['url'])
        ret=ce.load_from_file(filename,[])
        data_from={**data_from,**ret['修改这里']['data_from']}
    else:
        ret= await ce.load_from_url2(data_from,{},0,session['userid'])
    return {
            'data_from':data_from
            ,"ds_dict":{k:v['data'] for (k,v) in ret.items()}
            ,'df_arr':[ x for x in ret ]
            }
if glb.is_test:
    @mg.route("/getOneDsDataHtmlTable/", methods=['GET', 'POST'])
    @run_async
    async def getOneDsDataHtmlTable():
        config_data=request.json['config_data']
        df_arr,ds_dict= await load_one_data(config_data,request.json['cur_config'],request.json.get('param'),request.json['curr_report_id'])        
        return {
                'config_data':config_data
                ,"ds_dict":ds_dict
                ,'df_arr':df_arr
                }

    async def load_one_data(config_data,data_from,param,curr_report_id):
        glb.redis.sadd("zb:executing",curr_report_id)
        try:
            ds_dict= await ce.load_all_data(config_data,curr_report_id,upload_path=glb.user_report_upload_path(curr_report_id),userid=session['userid'])
            #ds_dict=ce.load_all_data(config_data,curr_report_id,upload_path=glb.user_report_upload_path(curr_report_id),userid=session['userid'])
            df_arr=[]
            ret={}
            for k,v in ds_dict.items():
                if isinstance(v,pd.DataFrame):
                    ret[k]=v.to_json(orient='split',force_ascii=False) #
                    df_arr.append(k)
                elif k[:2]!='__':
                    ret[k]=v
            return df_arr,ret
        finally:
            glb.redis.srem("zb:executing",curr_report_id)

    @mg.route("/files_template_exec/<int:id>", methods=['GET', 'POST'])    
    @run_async
    async def files_template_exec(id):
        ret_files=[]
        config_data=request.json['config_data']
        glb.redis.sadd("zb:executing",id)
        try:
            ret_files,tpl_results,all_files=await ce.files_template_exec(id,config_data,session['userid'] ,glb.config['UPLOAD_FOLDER'])
            return jsonify({"code":0,'message' :'成功生成','ret_files':ret_files,"tpl_results":tpl_results,"all_files":all_files})
        finally:
            glb.redis.srem("zb:executing",id)
else:
    @mg.route("/getOneDsDataHtmlTable/", methods=['GET', 'POST'])
    @run_async
    async def getOneDsDataHtmlTable():
        config_data=request.json['config_data']
        df_arr,ds_dict= await load_one_data(config_data,request.json['cur_config'],request.json.get('param'),request.json['curr_report_id'])        
        return {
                'config_data':config_data
                ,"ds_dict":ds_dict
                ,'df_arr':df_arr
                }

    async def load_one_data(config_data,data_from,param,curr_report_id):
        glb.redis.sadd("zb:executing",curr_report_id)
        try:
            async_result= hnclic.tasks.load_all_data.delay(config_data,curr_report_id,upload_path=glb.user_report_upload_path(curr_report_id),userid=session['userid'])
            # _,ds_dict,ret_config_data=await async_result.get()
            while not async_result.ready():
                await asyncio.sleep(0.1)
            if async_result.status=='FAILURE':
                raise RuntimeError(async_result.traceback.replace('\n','<br>\n'))            
            
            df_arr,ds_dict,ret_config_data= async_result.result
            config_data.update(ret_config_data)            
            return df_arr,ds_dict
        finally:
            glb.redis.srem("zb:executing",curr_report_id)

    @mg.route("/files_template_exec/<int:id>", methods=['GET', 'POST'])
    @run_async
    async def files_template_exec(id):
        ret_files=[]
        config_data=request.json['config_data']
        glb.redis.sadd("zb:executing",id)
        try:
            task_result= hnclic.tasks.files_template_exec.delay(id,config_data,session['userid'] ,glb.config['UPLOAD_FOLDER'])
            while not task_result.ready():
                await asyncio.sleep(0.1)
            if task_result.status=='FAILURE':
                raise RuntimeError(task_result.traceback.replace('\n','<br>\n'))            
            all_files=None
            ret_files,tpl_results,all_files=task_result.result
            return jsonify({"code":0,'message' :'成功生成','ret_files':ret_files,"tpl_results":tpl_results,"all_files":all_files})
        finally:
            glb.redis.srem("zb:executing",id) 


@mg.route("/ReportDefine/get/<int:id>")
def ReportDefine_get(id):
    my_path=glb.user_report_upload_path(id)
    my_file_list=[ {'name':x,'url':f'/mg/file/download/{id}/{x}'}  for x in (os.listdir(my_path) if os.path.exists(my_path) else [])]
    with glb.db_connect() as conn:
        with conn.cursor(as_dict=True) as cursor:
            cursor.execute('SELECT * FROM zhanbao_tbl WHERE id=%d', id)
            ret=cursor.fetchone()
            ret['fileList']=my_file_list
            return json.dumps(ret,ensure_ascii=False)

@mg.route("/ReportDefine/edit/<int:id>")
def ReportDefine_edit(id):
    app.jinja_env.cache.clear()
    return render_template('edit_template_config.html',report_id=id,url_prefix='/mg')

@mg.route("/ReportDefine/list")
def ReportDefine_list():
    with glb.db_connect() as conn:
        with conn.cursor(as_dict=True) as cursor:
            cursor.execute('SELECT id,report_name label FROM zhanbao_tbl WHERE worker_no=%s', session['userid'])
            ret=cursor.fetchall()
            return json.dumps(ret,ensure_ascii=False)

@mg.route("/ReportDefine/save/<int:id>",methods=['POST'])
def ReportDefine_save(id):
    lastrowid=id
     
    cron_str=request.json.get('cron_str','')
    if cron_str is None:
        cron_str=''
    cron_start=request.json.get('cron_start',0)
    if cron_start is None:
        cron_start=0
    
    if cron_str.startswith("*") or cron_str.startswith("* *"):
        return {'message':'设置的定时会太频繁执行，请修改,前两位不要是: * *！','errcode':-1}
    data={'config_data':json.dumps(request.json['config_data'],ensure_ascii=False), 
                'userid':session['userid'],'id':id,'report_name':request.json['report_name'], 
                'cron_str':cron_str,'cron_start':int(cron_start),
                }
    with glb.db_connect() as conn:
        with conn.cursor() as cursor:
            if id==0:
                cursor.execute('insert into zhanbao_tbl(config_txt,worker_no,report_name,cron_str,cron_start) '
                                +'values(%(config_data)s, %(userid)s,%(report_name)s,%(cron_str)s,%(cron_start)s)',
                    data)
                lastrowid=cursor.lastrowid
            else:
                cursor.execute('update zhanbao_tbl set config_txt=%(config_data)s,report_name=%(report_name)s,'+
                'cron_str=%(cron_str)s,cron_start=%(cron_start)d'+
                'WHERE id=%(id)d and worker_no=%(userid)s',data)
            conn.commit()
    #id,cron_str,cron_start,config_data,userid
    glb.update_scheduler(id,cron_str,data['cron_start'],request.json['config_data'],session['userid'],request.json['report_name'])
    return {'errcode':0,'message':'更新成功！','lastrowid':int(str(lastrowid)),'report_name':request.json['report_name']}

#-----------------------------------------------

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in glb.config['ALLOWED_EXTENSIONS']

@mg.route("/file/posts/<int:id>",methods=['POST'])
def upload_file(id):
    if 0==id:
        return  jsonify(errcode=-1,message='先保存配置再上传文件')
    if 'file' not in request.files:
        flash('No file part')
        return  jsonify(errcode=-1,message='No file part')
    file = request.files['file']
    if file.filename == '':
        flash('No selected file')
        return  jsonify(errcode=-1,message='No selected file')
    if file and allowed_file(file.filename):
        from werkzeug.utils import secure_filename
        filename = file.filename#secure_filename(file.filename)
        filename =os.path.join(glb.user_report_upload_path(id,created=True), filename)
        file.save(filename)
        fsize = os.path.getsize(filename)
        if( fsize>10* 1024 * 1024 ):
            os.remove(filename)
            return  jsonify(errcode=-1,message="上传失败，文件大小超过500K")
        return  jsonify(errcode=0,message="上传成功")
    else:
        return jsonify(errcode=-1,message="没有该文件，或文件名后缀不正确。应该为:"+str(glb.config['ALLOWED_EXTENSIONS']))

@mg.route("/file/download_t/<int:id>/<filename>",methods=['get'])
def download_file_t(id,filename):
    return send_from_directory(f"{glb.config['UPLOAD_FOLDER']}/tmp/{id}" , filename,as_attachment=True)

@mg.route("/file/download/<int:id>/<filename>",methods=['get'])
def download_file(id,filename):
    return send_from_directory(glb.user_report_upload_path(id), filename,as_attachment=True)

@mg.route("/image_file/<int:id>/<filename>",methods=['get'])
def image_file(id,filename):
    return send_from_directory(f"{glb.config['UPLOAD_FOLDER']}/tmp/{id}", filename)

@mg.route("/file/remove/<int:id>/<filename>",methods=['post'])
def remove_file(id,filename):
    import os
    file_path=glb.user_report_upload_path(id)
    file=os.path.join(file_path, filename)
    if os.path.realpath(file).startswith(file_path):
        os.remove(file)
        return {'errcode': 0, 'message': '删除成功'}
    else:
        return {'errcode': 1, 'message': '非法删除'}

@mg.route("/getLoginGetDataTemplate", methods=['GET'])
def getLoginGetDataTemplate():
    all_sys=None
    with glb.db_connect() as conn:
        with conn.cursor(as_dict=True) as cursor:
            if glb.ini['user_login']['test_user']==session['userid']:
                cursor.execute('SELECT * FROM sys_register')
                all_sys=cursor.fetchall()
            cursor.execute('SELECT * FROM login_tbl WHERE worker_no=%s', session['userid'])
            login_tbl=cursor.fetchall()
    return {'errcode':0,
        'sys_register':all_sys if all_sys is not None else [],
        'parsers':list([x[:-3] for x in os.listdir("./data_adapter/") if x[-3:]=='.py' and x!='__init__.py' and x!='DataInterface.py' ] ),
        'login_tbl':login_tbl}

@mg.route("/login_tbl/", methods=['POST'])
@run_async
async def login_tbl():
    data=request.json
    data['userid']=session['userid']
    di=DataInterface(None,session['userid'],glb.getSysRegister(data['sys_name']),data)
    cookies,login_headers=await di.login_check()
    with glb.db_connect() as conn:
        with conn.cursor(as_dict=True) as cursor:
            cursor.execute(""" MERGE INTO [login_tbl] t 
                USING (VALUES (%(sys_name)s,%(username)s,%(password)s,%(userid)s)) 
                    AS s(sys_name,username,password,worker_no) 
                    ON (t.[sys_name]=s.[sys_name] and t.worker_no=s.worker_no)
                    WHEN MATCHED THEN  UPDATE SET [username]=%(username)s,[password]=%(password)s 
                    WHEN NOT MATCHED THEN    INSERT (sys_name,username,password,worker_no)           
                    VALUES(%(sys_name)s,%(username)s,%(password)s,%(userid)s);""",
                data)
            conn.commit()
    return jsonify(errcode=0,)
    
@mg.route("/sys_register/<action>", methods=['POST'])
def sys_register(action):
    if glb.ini['user_login']['test_user']!=session['userid']:
        return {'errcode': 1, 'message': '你没有权限修改配置'}
    data=json.loads(json.dumps(request.json))
    data['worker_no']=session['userid']
    data['json_txt']=json.dumps(request.json,ensure_ascii=False)
    with glb.db_connect() as conn:
        with conn.cursor(as_dict=True) as cursor:
            if action=="delete":
                cursor.execute("delete from sys_register where id=%d",data['id'])
                conn.commit()
                glb.redis.hdel("zb:sys_register",data['name'])
                del glb.login_getData_template_dict[data['name']]
                return jsonify(errcode=0,)
            if data.get('id') is None or data['id']==0:
                cursor.execute("""INSERT INTO [dbo].[sys_register]([name],worker_no,[type],json_txt)
                    VALUES (%(name)s,%(worker_no)s,%(type)s,%(json_txt)s)""", {
                        'name':data['name'],
                        'worker_no':data['worker_no'],
                        'type':data['type'],
                        'json_txt':data['json_txt']
                    })
                conn.commit()
                data['id']=cursor.lastrowid
                glb.redis.hset("zb:sys_register",data['name'],data['json_txt'])
                glb.login_getData_template_dict[data['name']]=json.loads(data['json_txt'])
                return jsonify(errcode=0,id=cursor.lastrowid)
            else:
                cursor.execute(""" update [sys_register] set
                    name=%(name)s,worker_no=%(worker_no)s
                    ,type=%(type)s
                    ,json_txt=%(json_txt)s where id=%(id)d
                    """,{
                        'name':data['name'],
                        'worker_no':data['worker_no'],
                        'type':data['type'],
                        'json_txt':data['json_txt'],
                        'id':data['id']
                    } )
                conn.commit()
                glb.redis.hset("zb:sys_register",data['name'],data['json_txt'])
                glb.login_getData_template_dict[data['name']]=json.loads(data['json_txt'])
                return jsonify(errcode=0,)

#########################
#f"{glb.config['UPLOAD_FOLDER']}/{session['userid']}/tmp"
# 
# ##########################

@app.route("/")
def index():
    return redirect("/static/index.html")

@app.route("/zb/update_title",methods=['post'])
def update_title():
    with glb.db_connect() as conn:
        with conn.cursor(as_dict=True) as cursor:
            params= {**request.json}
            params['worker_no']=session['userid']
            cursor.execute('update zhanbao_tbl set report_name=%(label)s where id=%(id)s',
                            {'label':request.json['label'],'id':request.json['id']})
            conn.commit()
            return {'code':0,'message':""}

@app.route("/zb/create_one",methods=['post'])
def create_one():
    with glb.db_connect() as conn:
        with conn.cursor(as_dict=True) as cursor:
            pid=request.json.get('id',0)
            cursor.execute('insert into zhanbao_tbl(worker_no,report_name,is_catalog,pid,config_txt,cron_start) ' + \
                'values(%(worker_no)s,%(label)s,%(is_catalog)d,%(pid)d,\'{"data_from": [],"fileList": [ ],"output": [ ],"form_input": [ ] }\',0)',
                            {'label':request.json['label'],
                            'worker_no':session['userid'],
                            'is_catalog':request.json['type']=="Catalog",
                            'pid':pid
                            })
            id=cursor.lastrowid
            conn.commit()
            return {'path':f'/zb/zb/{id}','icon': 'list','label': request.json['label'], 
                'id': id,'pid':pid,'is_catalog':request.json['type']=="Catalog"
                }

@app.route("/zb/delete_one",methods=['post'])
def delete_one():
    glb.update_scheduler(request.json['id'],'0',None,None,None,None)
    with glb.db_connect() as conn:
        with conn.cursor(as_dict=True) as cursor:
            cursor.execute('delete from zhanbao_tbl where worker_no=%(worker_no)s and id=%(id)d',
                            {'worker_no':session['userid'],
                            'id':request.json['id']
                            })
            conn.commit()
            return {'code':0,'message':'success' }

@app.route("/zb/move_one",methods=['post'])
def move_one():
    #draggingID:draggingNode.data.id,dropID:dropNode.data.id,dropType
    params= {**request.json}
    params['worker_no']=session['userid']
    with glb.db_connect() as conn:
        with conn.cursor(as_dict=True) as cursor:
            if request.json["dropType"]=="inner":
                cursor.execute('update zhanbao_tbl set pid=%(dropID)s where id=%(draggingID)s',params)
            elif request.json["dropType"]=="before":
                cursor.execute('''
                update zhanbao_tbl set pid=(select pid from zhanbao_tbl where id=%(dropID)s) where id=%(draggingID)s
                update zhanbao_tbl set xuhao=(select xuhao+1 from zhanbao_tbl where id=%(dropID)s) where id=%(draggingID)s
                ;with aaa as(
                select pid,id,xuhao,row_number() over(partition by pid order by xuhao) rn from zhanbao_tbl
                where worker_no=%(worker_no)s
                )
                update aaa set xuhao=rn
                update zhanbao_tbl set xuhao=xuhao-1 where worker_no=%(worker_no)s and xuhao<=(select xuhao from zhanbao_tbl where worker_no=%(worker_no)s and id=%(draggingID)s )
                update zhanbao_tbl set xuhao=(select xuhao+1 from zhanbao_tbl where worker_no=%(worker_no)s and id=%(draggingID)s ) where worker_no=%(worker_no)s
                and id=%(dropID)s''',params)
            elif request.json["dropType"]=="after":
                cursor.execute('''
                update zhanbao_tbl set pid=(select pid from zhanbao_tbl where id=%(dropID)s) where id=%(draggingID)s
                update zhanbao_tbl set xuhao=(select xuhao+1 from zhanbao_tbl where id=%(dropID)s) where id=%(draggingID)s
                ;with aaa as(
                select pid,id,xuhao,row_number() over(partition by pid order by xuhao) rn from zhanbao_tbl
                where worker_no=%(worker_no)s
                )
                update aaa set xuhao=rn
                update zhanbao_tbl set xuhao=xuhao+1 where worker_no=%(worker_no)s and xuhao>=(select xuhao from zhanbao_tbl where worker_no=%(worker_no)s and id=%(draggingID)s )
                update zhanbao_tbl set xuhao=(select xuhao-1 from zhanbao_tbl where worker_no=%(worker_no)s and id=%(draggingID)s ) where worker_no=%(worker_no)s
                and id=%(dropID)s''',params)
            conn.commit()
            return {'code':0,'message':""}

import objgraph,time
import gc,tracemalloc
tracemalloc.start()
b_snapshot = tracemalloc.take_snapshot()

@app.route("/zb/info_s",methods=['get'])
def get_info_s():
    b_snapshot = tracemalloc.take_snapshot()
    return  jsonify(text="ok")

@app.route("/zb/info",methods=['get'])
def get_info():
    gc.collect()
    snapshot2 = tracemalloc.take_snapshot()
    with open("flaskMemoy.log", 'a+') as f:
        f.write("====================================")
        f.write(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
        
        f.write("\n")
        top_stats = snapshot2.compare_to(b_snapshot, 'lineno')
        for stat in top_stats[:10]:
            f.write(str(stat))
            f.write("\n")
        f.write("====================================")
        f.write("\n")
        objgraph.show_most_common_types(limit=5,file=f)
        f.write("====================================")
        f.write("\n")
    return  jsonify(text="ok")

@app.route('/h5/<name>',methods=['get'])
def h5(name):
    _real_path=os.path.realpath(glb.config['UPLOAD_FOLDER']+f"/tmp/html/{name}")
    if False==_real_path.startswith(os.path.realpath(glb.config['UPLOAD_FOLDER']+f"/tmp/html/")):
        return "非法路径！你被记入黑名单！"
    else:
        with open(_real_path,encoding='utf8') as f:
            s=f.read()
            f.close()
        return s

@app.route("/api/raw/<int:id>/<rawtype>/<ds_names>")
@run_async
async def raw_get(id,rawtype,ds_names):
    glb.redis.hincrby("zb:tj",'api')
    ds_names=ds_names.split(',')
    cur=None
    with glb.db_connect() as conn:
        with conn.cursor(as_dict=True) as cursor:
            cursor.execute('SELECT * FROM zhanbao_tbl WHERE id=%s', id)
            config_data= json.loads(cursor.fetchone()['config_txt'])
    #for one_data_from in json.loads(cur_row['config_txt'])['data_from'] for one on one_data_from['ds'] is one['name'] in ds_names
    user_input_form_data={**request.args,**request.form}
    # ds_dict= ce.load_all_data(config_data,id,args=args,upload_path=glb.user_report_upload_path(id),userid=glb.ini['user_login']['test_user'])

    async_result= hnclic.tasks.load_all_data.delay(config_data,id,
                                    user_input_form_data=user_input_form_data,
                                    upload_path=glb.user_report_upload_path(id),
                                    userid=glb.ini['user_login']['test_user'])
    # _,ds_dict,ret_config_data=await async_result.get()
    while not async_result.ready():
        await asyncio.sleep(0.1)
    if async_result.status=='FAILURE':
        raise RuntimeError(async_result.traceback.replace('\n','<br>\n'))            
    
    _,ds_dict,ret_config_data= async_result.result

    ret_dict=dict({key:value for key,value in ds_dict.items() if key in ds_names})
    rawtype=rawtype.split(":")
    ret_str='{"errcode":0,"message":"success",'
    if rawtype[0]=='json':
        '''json的格式如下
        split ，样式为 {index -> [index], columns -> [columns], data -> [values]}
        records ，样式为[{column -> value}, … , {column -> value}]
        index ，样式为 {index -> {column -> value}}
        columns ，样式为 {index -> {column -> value}}
        values ，数组样式
        table ，样式为{‘schema': {schema}, ‘data': {data}}，和records类似
        '''
        json_type='records'
        if len(rawtype)==2 :
            if rawtype[1] in "split,records,index,columns,values,table":
                json_type=rawtype[1]
            else:
                return '{"errcode":1,"message":"json选择的类型不正确，应该是下面之一： split,records,index,columns,values,table"}'
        for key,value in ret_dict.items():
            ret=json.loads(value)
            ret_str=ret_str+'\n"' + key+'":' + pd.DataFrame(ret["data"],columns=ret["columns"]).to_json(orient=json_type,force_ascii=False)+','
    ret_str=ret_str[:-1]+'}'
    return ret_str        