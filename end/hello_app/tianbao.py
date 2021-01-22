from datetime import datetime
import requests,os,sys, traceback
from flask import Flask, render_template, request,session,flash,make_response,redirect,send_from_directory,session,Blueprint,url_for
from hello_app import app
from hnclic import convert_main as ce
import json
from werkzeug.utils import secure_filename
import pymssql
import numpy as np
import pandas as pd
import decimal

tb = Blueprint('tb', __name__, template_folder='templates')

@tb.before_request
def is_login():
    if request.path.startswith("/tb/login") or request.path.startswith("/static") or request.path.startswith("/api/"):
        return None
    if not session.get("userid"):
        return render_template("my_login.html",url_prefix='/tb')
        #return url_for("mg.login_form")
    #session.permanent = True
    #app.permanent_session_lifetime = timedelta(minutes=10)

@tb.route("/")
def home():
    return render_template("tianbao_home.html",userInfo=session['userInfo'],url_prefix='/tb')

@tb.route("/login/", methods=['GET', 'POST'])
def login():
    if not request.form['userid']:
        redirect("/login_form")
    userid,password=request.form['userid'],request.form['password']
    #r_json=requests.post(app.config['yzl_auth'],{'userid':userid,'password':password,'attrib':'mobile,phone,mail'}).json()
    r_json={'errcode': 0, 'errmsg': '认证成功', 'userid': 'xxxxxxxxxxx', 'username': 'xxxxxx', 'userAttrtibute': {'mail': '笑嘻嘻@wo.cn', 'displayName': 'cccc', 'mobile': 'xxxxxx', 'pwdLastSet': 'xxxxxxxxxxxxxx'}}
    r_json['branch_no']='410881'
    if r_json['errcode']==0:
        session['userid']=userid
        session['old_userid']=userid
        session['userInfo']=r_json
    return r_json

import pandasql
@tb.route("/queryData", methods=['GET', 'POST'])
def queryData():#rpd_id,branch_name,strat_date,end_date,branch_no
    if request.method=='GET':
        param={"rpt_id":int(request.args['rpt_id']),"worker_no":session['userid'],
                "branch_no":session['userInfo']['branch_no'],
                "b_date":'2019-12-01',"e_date":datetime.today().strftime("%Y-%m-%d")
            }
    else:
        param={"rpt_id":int(request.json['rpt_id']),"branch_no":request.json['branch_no'],
                "b_date":request.json['b_date'],"e_date":request.json['e_date']
            }
    with app.config['db_connect']() as conn:
        with conn.cursor(as_dict=True) as cursor:
            (rpt_define,ret_sql)=list_history(cursor,param)
            if(None==request.args.get('mx')):
                cursor.execute(ret_sql, param)                
            else:
                cursor.execute("select * from #temp_b", param)
            ret_df_detail={'columns':list([x[0] for x in cursor.description]),
                            'rpt_define':rpt_define,
                            'data':cursor.fetchall()}
                            
            if(request.args.get('xlsx','')=='group'):
                def list_group(p):
                    return ['河南','郑州','洛阳','开封','焦作','南阳']
                def groupby(p):
                    return pandasql.sqldf(ret_sql.replace('#temp_b','ttt').replace('b.branch_no=%(branch_no)s',f"b.branch_name='{p}'")
                                    ,{'branch_bridge':branch_bridge,'ttt': ret_df_detail})[col_order]
                
                data=pandasql.sqldf(ret_sql.replace('#temp_b','ttt').replace('b.branch_no=%(branch_no)s',"b.branch_no='410000'")
                                    ,{'branch_bridge':branch_bridge,'ttt': ret_df_detail})[col_order]
                ce.convert_file_for_xlsx("C:/Users/lzm/Desktop/tjc_output.xlsx","C:/Users/lzm/Desktop/tjc.xlsx",{'c':data}
                    ,appendFunDict={'list_group':list_group,'groupby':groupby})
    if request.method=='GET':
        return render_template("tb_query.html",
            t_json=ret_df_detail,
            date=datetime.today(),
            param=param,        
            url_prefix='/tb')
    else:
        return {'errcode':0,'data':ret_df_detail}

@tb.route("/save_tianbao_define", methods=['POST'])
def save_tianbao_define():
    define=request.json['content']
    define['rpt_type']=','.join(define['rpt_type'])
    define['rpt_content']=json.dumps(define['rpt_content'])
    with app.config['db_connect']() as conn:
        with conn.cursor(as_dict=True) as cursor:
            if define['id']==0:
                cursor.execute("""
                insert into tianbao_define(worker_no,start_date,end_date,rpt_type,rpt_content,create_time,title) 
                values
                (%(worker_no)s,%(start_date)s,%(end_date)s,%(rpt_type)s,%(rpt_content)s,getdate(),%(title)s)
                """,define
                )
                define['id']=int(cursor.lastrowid)
            else:
                cursor.execute("""
                update  tianbao_define 
                set worker_no=%(worker_no)s,start_date=%(start_date)s,end_date=%(end_date)s,
                rpt_type=%(rpt_type)s,rpt_content=%(rpt_content)s,create_time=%(create_time)s,title=%(title)s
                where id=%(id)s
                """,define
                )
            conn.commit()
            return {'errcode':0,'errmsg':f'success','id':define['id']}

@tb.route("/load_tianbao_define/<int:id>", methods=['GET', 'POST'])
def load_tianbao_define(id):
    param={"rpt_id":id,"worker_no":session['userid'],
            "branch_no":session['userInfo']['branch_no'],
            "b_date":datetime.today().strftime("%Y-%m-%d"),"e_date":datetime.today().strftime("%Y-%m-%d")
        }
    with app.config['db_connect']() as conn:
        with conn.cursor(as_dict=True) as cursor:
            cursor.execute('''SELECT * FROM [dbo].[tianbao_branch_grant] where prio_branch_no= 
            (SELECT branch_no FROM [dbo].[tianbao_branch_grant] WHERE rpt_id=%(rpt_id)d and worker_no=%(worker_no)s)'''
                        , param)
            branch_grants=cursor.fetchall()

            if(param['rpt_id']==0):
                return render_template("edit_tianbao_define.html",
                    t_json={'id': 0, 'worker_no':session['userid'] , "branch_no":session['userInfo']['branch_no'],
                    'create_time': None, 'rpt_content': [], 
                    'rpt_type': [], 'start_date':'', 'end_date': '', 'title': '', 'rpt_type_name': ''}
                    ,date=datetime.today(),
                    param=param,
                    branch_grants=branch_grants,
                    url_prefix='/tb')
                    
            cursor.execute('SELECT * FROM tianbao_define WHERE id=%d', int(param['rpt_id']))
            ret=cursor.fetchone()
            ret['rpt_content']=json.loads(ret['rpt_content'])
            ret["branch_no"]=session['userInfo']['branch_no']
            ret['rpt_type_name']='每个('+ret['rpt_type']+')只能填写一次(多次填写将覆盖已有数据)，非基层机构只能查看汇总'            
            ret['rpt_type']=ret['rpt_type'].split(',')
            #return json.dumps({'branch_grants':branch_grants,'define':ret},ensure_ascii=False)
            return render_template("edit_tianbao_define.html",
                t_json=ret,date=datetime.today(),
                param=param,
                branch_grants=branch_grants,
                url_prefix='/tb')


@tb.route("/tianbao_content", methods=['GET', 'POST'])
def tianbao_content():
    if request.method=='GET':
        param={"rpt_id":int(request.args['rpt_id']),"worker_no":session['userid'],
                "branch_no":session['userInfo']['branch_no'],
                "b_date":datetime.today().strftime("%Y-%m-%d"),"e_date":datetime.today().strftime("%Y-%m-%d")
            }
    else:
        param={"rpt_id":1,"worker_no":session['userid'],
                "branch_no":session['userInfo']['branch_no'],
                "b_date":'2019-01-01',"e_date":'2019-12-31'
            }
    
    with app.config['db_connect']() as conn:
        with conn.cursor(as_dict=True) as cursor:
            
            cursor.execute('''SELECT * FROM [dbo].[tianbao_branch_grant] WHERE rpt_id=%(rpt_id)d and worker_no=%(worker_no)s'''
                        , param)
            workForbranch=cursor.fetchall()
            if len(workForbranch)==0:
                return "您没有对该填报的操作权限"
           
            workForbranch=workForbranch[0]
            session['userInfo']['branch_no']=workForbranch['branch_no']
            cursor.execute('''SELECT * FROM [dbo].[tianbao_branch_grant] where prio_branch_no in 
            (SELECT branch_no FROM [dbo].[tianbao_branch_grant] WHERE rpt_id=%(rpt_id)d and worker_no=%(worker_no)s)'''
                        , param)
            branch_grants=cursor.fetchall()
            param['branch_no']=workForbranch['branch_no']
            (ret,ret_sql)=list_history(cursor,param)#取历史数据，当天数据
            cursor.execute("SELECT * FROM #temp_b")
            ret_df_detail=cursor.fetchall()
            
            #ret['rpt_content']=json.loads(ret['rpt_content'])
            ret['rpt_type_name']='每个('+ret['rpt_type']+')只能填写一次(多次填写将覆盖已有数据)，非基层机构只能查看汇总'
            #json.dumps(ret,ensure_ascii=False)
            return render_template("tb_content_more_lines.html",
                t_json=ret,date=datetime.today(),
                param=param,
                curr_data=ret_df_detail,
                branch_grants=branch_grants,
                workForbranch=workForbranch,
                url_prefix='/tb')

@tb.route("/submit_branch_grants",methods=['POST'])
def submit_branch_grants():
    with app.config['db_connect']() as conn:
        with conn.cursor(as_dict=True) as cursor:
            sql="create table #temp_a(branch_no varchar(14),worker_no varchar(255)) ;insert into #temp_a values \n" \
            + str([(x['branch_no'],x['worker_no']) for x in request.json['content']]).replace('None','null')[1:-1] \
            +"\nupdate a set worker_no=b.worker_no from  tianbao_branch_grant a join #temp_a b on a.rpt_id=%(rpt_id)d and a.branch_no=b.branch_no"
            cursor.execute(sql,{'rpt_id':request.json['rpt_id'] })
            lastrowid=cursor.lastrowid
            conn.commit()
    return {'errcode':0,'errmsg':f'success'}

@tb.route("/submit_tianbao_content",methods=['POST'])
def submit_tianbao_content():
    with app.config['db_connect']() as conn:
         with conn.cursor(as_dict=True) as cursor:
            cursor.execute('SELECT * FROM tianbao_define WHERE id=%d', request.json['rpt_id'])
            ret=cursor.fetchone()
            data_json=json.loads(request.json['content'])
            for one_col in json.loads(ret['rpt_content']):
                if(one_col['type']=='int' and not all(map(lambda x: isinstance(x[one_col['name']],int ), data_json))):
                    return {'errcode':1,'errmsg':one_col['name']+' 不是 整数'}
                if(one_col['type'].startswith('decimal') 
                and not all(map(lambda x: isinstance(x[one_col['name']],float ), data_json))
                and not all(map(lambda x: isinstance(x[one_col['name']],int ), data_json))
                ):
                    return {'errcode':1,'errmsg':one_col['name']+'不是 浮点数'}
            matched_str=''
            for one_match in ret['rpt_type'].split(','):
                matched_str=matched_str+ f' and t.{one_match}=s.{one_match} '
                
            cursor.execute(""" MERGE INTO [tianbao_result] t 
USING (VALUES (%(rpt_id)s,%(工号)s,%(机构代码)s,%(填写日期)s,%(write_content)s)) 
            AS s([rpt_id],[工号],[机构代码],[填写日期],[write_content]) 
ON (t.[rpt_id]=s.[rpt_id] __matched__)
WHEN MATCHED THEN 
    UPDATE  
    SET [rpt_id]=%(rpt_id)s
	,[工号]=%(工号)s,[机构代码]=%(机构代码)s,[填写日期]=%(填写日期)s,[write_content]=%(write_content)s         
WHEN NOT MATCHED THEN 
    INSERT ([rpt_id],[工号],[机构代码],[填写日期],[write_content])           
            VALUES(%(rpt_id)s,%(工号)s,%(机构代码)s,%(填写日期)s,%(write_content)s);
                """.replace("__matched__",matched_str),
                {'rpt_id':request.json['rpt_id'] ,
                '工号':session['userid'],
                '机构代码':session['userInfo']['branch_no'],
                '填写日期':str(datetime.today()),
                'write_content':request.json['content']
                }
            )
            lastrowid=cursor.lastrowid
            conn.commit()
            return {'errcode':0,'errmsg':f'success'}

def list_history(cursor,param):
    columns=[]
    not_calc_columns=[]
    number_columns=[]
    text_columns=[]
    not_calc_columns_with_type=[]
    calc_columns=[]
    calc_columns_with_formula=[]
    
    cursor.execute('SELECT * FROM tianbao_define WHERE id=%d', param['rpt_id'])
    ret=cursor.fetchone()
    ret['rpt_content']=json.loads(ret['rpt_content'])

    for one in ret['rpt_content']:
        columns.append(one['name'])
        if one.get('juhe_type','--') !='--':
            number_columns.append(one['name'])

        if one.get('type','--')=='calc':
            calc_columns.append(one['name'])
            calc_columns_with_formula.append(',('+one['formula'] +') '+one['name'])
        else:
            not_calc_columns.append(one['name'])
            not_calc_columns_with_type.append(f"\nalter table #temp_a alter column [{one['name']}] {one['type']}")
    sql=f"""with aaa as(
    Select a.id,a.rpt_id,a.工号,a.机构代码,a.填写日期, b.name,b.stringValue,b.parent_ID
    from [tianbao_result] a  __branch_no__ CROSS APPLY dbo.parseJSON(write_content) AS b
    where a.rpt_id=%(rpt_id)d and  parent_id is not null  and  b.name is not null
        __worker_no__  __date__ 
    )
    SELECT * into #temp_a FROM aaa
    pivot( MAX(stringvalue) FOR name IN({'['+'],['.join(not_calc_columns)+']'})) 
    as pv order by id,parent_id;
    {';'.join(not_calc_columns_with_type).replace('] int;','] decimal(12,2);')}
    ;with bbb as(
    select *{(' '.join(calc_columns_with_formula))}  from #temp_a
    )select id,工号,机构代码,填写日期,{','.join(columns)} into #temp_b from bbb
    drop table #temp_a
    """
    #{';'.join(not_calc_columns_with_type).replace('#temp_a ','#temp_b ').replace('] decimal(12,2);','] float;')}
    #select * from #temp_b
    if param.get('b_date') is not None and  param.get('e_date') is not None :
        sql=sql.replace("__date__"," and a.填写日期>=%(b_date)s  and a.填写日期<=%(e_date)s ")
    else:
        sql=sql.replace("__date__"," ")
    if param.get('worker_no') is not None:
        sql=sql.replace("__worker_no__"," and a.工号=%(worker_no)s ")
    else:
        sql=sql.replace("__worker_no__"," ")
    if param.get('branch_no') is not None:
        sql=sql.replace("__branch_no__","join branch_bridge c on a.机构代码=c.detail_branch and c.branch_no=%(branch_no)s ")
    else:
        sql=sql.replace("__branch_no__"," ")
        
    print(sql)
    cursor.execute(sql,param)
    #cursor.execute("""select """, 1)
    #列顺序
    col_order=['机构代码','单位']\
        +list(map( lambda x:'['+x['name']+']' ,
                    [y for y in ret['rpt_content'] 
                    if y.get('juhe_type','')!='' or y.get('formula','')!='']
                )
            )    
    sql="with aaa as(\nselect b.child_branch 机构代码,b.child_branch_name  单位," \
            + ','.join(map( lambda x: f"{x['juhe_type']}([{x['name']}]) [{x['name']}]", 
                            [y for y in ret['rpt_content'] if y.get('juhe_type','')!='' ]  )) \
            + "\n from #temp_b a "\
            +"\njoin branch_bridge b on a.机构代码 =b.detail_branch and b.branch_no=%(branch_no)s "\
            +"\ngroup by b.child_branch,b.child_branch_name ) "\
            +"\n,bbb as( select *" + ''.join(calc_columns_with_formula) +" from aaa )" \
            +"\n select "+",".join(col_order) +" from bbb order by 机构代码 asc"
    print(sql)
    ret_sql=sql

    return ret,ret_sql
 
def convert_DataFrame(result,columns=None):
    col_list=dict()
    if(len(result)==0):
        return pd.DataFrame(columns=columns)
    for (k,v) in result[0].items():
        if isinstance(v,decimal.Decimal) or isinstance(v,float):
            col_list[k]='float64'
        elif isinstance(v,int):
            col_list[k]='int64'
        else:
            col_list[k]='str'
    return pd.DataFrame(result).astype(col_list)