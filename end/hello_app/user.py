from datetime import datetime
import requests,os,sys, traceback
from flask import Flask, render_template, request,session,flash,make_response,redirect,send_from_directory,session,Blueprint,url_for,jsonify
from hello_app import app
from hnclic import convert_main as ce,glb
import json
from werkzeug.utils import secure_filename
import pymssql
from pathlib import Path
from handle_file import is_number
@app.route("/user/info")
@app.route("/user/getUserInfo")
def user_info():
    r_json=session['userInfo']
    with glb.db_connect() as conn:
        with conn.cursor(as_dict=True) as cursor:
            cursor.execute('SELECT id,report_name,pid,is_catalog FROM zhanbao_tbl WHERE worker_no=%s  order by xuhao asc', session['userid'])
            ret=cursor.fetchall()
    r_json['roles']=['Admin','Vistor']
    
    r_json['menus']=[ {'path':f'/zb/zb/{x["id"]}','icon': 'list',
                    'title': x["report_name"], 'id': x["id"],'pid':x["pid"]
                    ,"is_catalog":x['is_catalog']
                    } 
                    for x in ret]
    r_json['name']=r_json['username']
    r_json['userInfo']= {
                'username': session['userid'],
                'name': r_json['username'],
                'avatar': 'https://gitee.com/uploads/61/632261_smallweigit.jpg',
            }
    r_json['permission']=[
                'sys_crud_btn_add',
                'sys_crud_btn_export',
                'sys_menu_btn_add',
                'sys_menu_btn_edit',
                'sys_menu_btn_del',
                'sys_role_btn1',
                'sys_role_btn2',
            ]
    if glb.ini['user_login']['test_user']==session['userid']:
        r_json['permission'].append('sys_register')
    r_json['canReadSys']=glb.getSysByUser(session['userid'])
    return json.dumps({"code":0,"data":r_json})

@app.route("/user/getTopMenu")
def getTopMenu():
    return jsonify({'data':
        [   
            {'label': "战报管理",'path': "/wel/index",'icon': 'el-icon-document', 'parentId': 0,'meta': {'edit': True,'prefix':"zb"}},
            {'label': "报表平台",'icon': 'el-icon-document','path': "/wel/index", 'parentId': 1,'meta': {'edit': False,'prefix':"zb"}},
            #{'label': "测试",'icon': 'el-icon-document','path': "/rpt-list/index",'parentId': 2},
            #{'label': "更多",'icon': 'el-icon-document','path': "/wel/dashboard",'meta': {'menu': False},'parentId': 3}
        ]
        }
    )

@app.route("/user/getMenu/<parentId>", methods=['GET','POST'])
def getMenu(parentId):

    if(parentId=='0'):
        with glb.db_connect() as conn:
            with conn.cursor(as_dict=True) as cursor:
                cursor.execute('SELECT id,report_name,isnull(pid,0) pid,is_catalog FROM zhanbao_tbl WHERE worker_no=%s  order by xuhao asc', session['userid'])
                ret=cursor.fetchall()
        ret=[ {'path':f'/zb/zb/{x["id"]}','icon': 'el-icon-document',
                'component': 'views/zhanbao/zb_index',
                'label': x["report_name"], 
                'id': x["id"],'pid':x["pid"],
                "is_catalog":x['is_catalog'],'meta':{'id':x["id"],'keepAlive': True}
                }
            for x in ret]
    elif parentId=='1':
        with glb.db_connect() as conn:
            with conn.cursor(as_dict=True) as cursor:#.encode('latin-1').decode('gbk')
                cursor.execute("""SELECT m.id, m.name label, m.parent_id pid, m.url res_url, m.icon
FROM [10.20.54.104].localapp.dbo.protal_sys_menu m
LEFT JOIN [10.20.54.104].localapp.dbo.protal_sys_role_menu rm ON (rm.menu_id = m.id)
LEFT JOIN [10.20.54.104].localapp.dbo.protal_sys_user_role ur ON (ur.role_id = rm.role_id)
LEFT JOIN [10.20.54.104].localapp.dbo.protal_sys_user u ON (u.id = ur.user_id)
WHERE u.name = %s""",session['userid'])
                ret=cursor.fetchall()
        ret=[ {'path':x["res_url"] if x["res_url"] != None else "",'icon': 'el-icon-document-copy',
            'label': x["label"].encode('latin-1').decode('gbk'), 'id': x["id"],'pid':x["pid"],
                'meta':{'id':x["id"],'isTab':False}
                }
            for x in ret]
    elif parentId=='2' and session['userid']=='14100298':
        ret=[{'label': "报表目录",'icon': 'el-icon-document','path': "/rpt-list/index"}]       
    else:
        ret=[]
    return  jsonify(data=ret)

import hnclic.tasks 
@app.route("/api/yzl_info", methods=['GET','POST'])
def yzl_info():
    info=request.form.get('info','')
    user_id=request.form.get('user_id','')
    if not info.startswith("@助手"):
        return "回复：不是给我的命令"
    info_arr=info.split()
    if info_arr[1]=='list':
        with glb.db_connect() as conn:
            with conn.cursor(as_dict=True) as cursor:
                cursor.execute('SELECT id,report_name FROM zhanbao_tbl WHERE worker_no=%s and is_catalog=0 order by xuhao asc', user_id)
                ret=cursor.fetchall()
        return '\n'.join([f"{x['id']}_{x['report_name']}" for x in ret])
    if is_number(info_arr[1]):
        with glb.db_connect() as conn:
            with conn.cursor(as_dict=True) as cursor:
                cursor.execute('SELECT config_txt,report_name FROM zhanbao_tbl WHERE worker_no=%(user_id)s and id=%(id)d and is_catalog=0 order by xuhao asc', 
                                {"user_id":user_id,"id":int(info_arr[1])}
                            )
                ret=cursor.fetchone()
        if ret is None:
            return "没有这个ID:"+info_arr[1]
        hnclic.tasks.zb_execute.delay(int(info_arr[1]),json.loads(ret['config_txt']),user_id,ret['report_name'] )
        return ret['report_name']+",已经开始执行"
    return """ @助手 list   可以看到所有自己做的战报ID 和名字
 @助手 战报ID   执行战报
    """

@app.route("/api/raw/<int:id>/<rawtype>/<ds_names>")
def raw_get(id,rawtype,ds_names):
    glb.redis.hincrby("zb:tj",'api')
    ds_names=ds_names.split(',')
    cur=None
    with glb.db_connect() as conn:
        with conn.cursor(as_dict=True) as cursor:
            cursor.execute('SELECT * FROM zhanbao_tbl WHERE id=%s', id)
            config_data= json.loads(cursor.fetchone()['config_txt'])
    #for one_data_from in json.loads(cur_row['config_txt'])['data_from'] for one on one_data_from['ds'] is one['name'] in ds_names
    args={**request.args,**request.form}
    ds_dict=ce.load_all_data(config_data,id,args=args,upload_path=glb.user_report_upload_path(id),userid=glb.ini['user_login']['test_user'])
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
            ret_str=ret_str+'\n"' + key+'":' + value.to_json(orient=json_type,force_ascii=False)+','
    ret_str=ret_str[:-1]+'}'
    return ret_str

#####################################################
# 登录相关
#####################################################
@app.route("/user/login", methods=['POST'])
@app.route("/api/auth/login", methods=['POST'])
def app_login():
    userid,password=request.json['username'],request.json['password']
    r_json=glb.user_login()
    if r_json['errcode']==0:
        session['userid']=userid
        session['old_userid']=userid
        session['userInfo']=r_json
        return {"code":0,"data":r_json['access_token']}
    if glb.is_test:
        return r_json
    else:
        return make_response(jsonify({'code':500,"message":r_json['errmsg']}), 401)

@app.before_request
def app_is_login():
    token=request.headers.get("Authorization")
    if(session.get('userid') is None and token is not None):
        r_json=glb.user_verify()
        if(r_json['errcode']==0):
            if(session.get('userid')==None):
                session['userid']=r_json['userid']
            session['old_userid']=r_json['userid']
            session['userInfo']=r_json
            if(r_json.get('access_token')==None):
                r_json["access_token"]=token
            return None
        return make_response(jsonify({'code':500,"message":r_json['errmsg']}), 401)
    if request.path.startswith("/static") or request.path.startswith("/api/") or request.path.startswith("/h5/") or  ['/','/user/login','/user/logout','/user/refesh'].count(request.path)>0:
        return None
    if session.get('userid') is None :
        return make_response(jsonify({'code':500,"message":"无效或过期"}), 401)

@app.route("/user/refesh", methods=['POST'])
def refeshToken():
    token=request.headers.get('Authorization','Bearer ')
    r_json=glb.user_verify()
    if(r_json['errcode']==0):
        if(r_json.get('access_token')!=None):
            if(session.get('userid')==None):
                session['userid']=r_json['userid']
            session['old_userid']=r_json['userid']
            session['userInfo']=r_json
            return {"code":0,"data":r_json['access_token']}
        elif session.get('userInfo') is not None :
            return {"code":0,"data":session['userInfo']['access_token']}
    return make_response(jsonify({'code':500,"message":"token失效"}), 401)

@app.route("/user/logout", methods=['GET'])
def user_logout():
    #del session['userid']
    return {'code':0,'message':''}
