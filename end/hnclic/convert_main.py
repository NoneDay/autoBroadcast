import sys, os, zipfile,re, requests,shutil,json,glob
sys.path.append(os.path.realpath(os.curdir+"/hello_app/"))
sys.path.append(os.path.realpath(os.curdir+"/hnclic/"))
sys.path.append(os.path.realpath(os.curdir+"/data_adapter/"))
from bs4 import BeautifulSoup
import lxml
import lxml.html
import threading
import numpy as np
import pandas as pd
import pandasql,excel2img
from numpy import nan as NaN
from functools import reduce
import jinja2,datetime,chardet,time,traceback,locale,copy
from pptx import Presentation
from pptx.enum.shapes import MSO_SHAPE_TYPE#MSO_SHAPE_TYPE.EMBEDDED_OLE_OBJECT
import comtypes.client
from openpyxl.formula.translate import Translator
from openpyxl  import load_workbook
import asyncio
import aiohttp
import yaml
from handle_file import convert_file_for_xlsx,convert_file_for_txt,convert_file_for_pptx,convert_html
from utils import get_jinja2_Environment,is_number,guess_col_names,exec_template
import data_adapter
import colorama 
import glb

'''
“在Windows里，time.strftime使用C运行时的多字节字符串函数strftime，
这个函数必须先根据当前locale配置来编码格式化字符串（使用PyUnicode_EncodeLocale）。”
如果不设置好locale的话，根据默认的"C" locale，底层的wcstombs函数会使用latin-1编码（单字节编码）
来编码格式化字符串，然后导致题主提供的多字节编码的字符串在编码时出错。
'''
locale.setlocale(locale.LC_CTYPE, 'chinese')
#显示所有列
pd.set_option('display.max_columns', None)

#显示所有行
pd.set_option('display.max_rows', None)
pd.set_option('display.width', None)
pd.options.display.float_format = '{:.2f}'.format


def func_time(func):
    def inner(*args,**kw):
        start_time = time.time()
        ret=func(*args,**kw)
        end_time = time.time()
        print(str(func)+'函数运行时间为：'+str(end_time-start_time)+'s')
        return ret
    return inner

def pd_read_csv(url):
    with open(url, 'rb') as f:
        data = f.read()
        f_charInfo=chardet.detect(data)                
    try:
        return pd.read_csv(url,encoding=f_charInfo['encoding'])
    except:
        return pd.read_csv(url,encoding='gb2312')
    #return pd.read_csv(url,encoding=f_charInfo['encoding'])

def load_from_file(url,d_p):
    ret=dict()
    if(os.path.isfile(url)):
        if url.find(".xlsx")>0:
            data=pd.read_excel(url)
            data[data.columns[0]]=data[data.columns[0]].astype(str)
        else:
            with open(url, 'rb') as f:
                data = f.read()
                f_charInfo=chardet.detect(data)                
            data=pd_read_csv(url)
            data[data.columns[0]]=data[data.columns[0]].astype(str)
        if (len(d_p)==0):
            d_p.append({"t": "html","start": "1","end": "10000","columns": "auto","view_columns": "","sort": "","name": "修改这里",'data_is_json':True})
        for p in d_p:
            p['data_is_json']=True
            ret[p['name']]={'data':data,'p':p,'header':data.columns.to_list(),"data_from":{'ds':d_p}}
        return ret
    raise Exception(url +'不存在')

async def load_from_url2(data_from=None,config_data=None,upload_path=None,userid=None,user_input_form_data=None):
    '''
    data_from 某网址下的取数逻辑总汇
    user_input_form_data 实际传过来的参数
    d_p_1={'t':'json','name':'b','pattern':'#reportDivaaa1thetable tr','start':'reportDivaaa1_data={"rows":','end':"/*-end-*/"}
    d_p_2={'t':'html','name':'a','pattern':'#reportDivmainthetable tr','start':4,'end':18}
    针对t:html 的end,+4 表示需要4行,不带+号的4 ，表示第4行，负数表示从后面开始倒数几行，如果为空，表示全部，最多100万行
    '''
    adapter=data_adapter.get(data_from,userid)
    await adapter.load_data_from_url(config_data.get('form_input',{}),user_input_form_data)
    #    if soup is not None and isinstance(soup,BeautifulSoup):
    #        soup.decompose()
    #        soup=None
    print("成功")
    ret=dict()
    for p in data_from['ds']:
        resultModel,header,data,json_props=adapter.load_data_for_p(p)
        if resultModel=="TableModel":
            data=pd.DataFrame(data,columns=header)
        elif resultModel=="JsonModel":
            data=pd.DataFrame(data)[json_props] #按json_props中指定的顺序重排
            data.columns=header#按header重设列名
            if 'id' in json_props:
                data=data.drop(['id'], axis=1)
        else:
            raise RuntimeError("适配接口只能返回TableModel或者JsonModel。请联系管理员修改程序")
        #删除NULL列
        if adapter.dropNaNColumn:
            data=data.replace('',NaN).dropna(axis = 1, how = "all")
            header=list(data.columns)
        #缺省列名为：s+数字
        if isinstance(p['view_columns'],str):
            data.columns=header if p['columns']=='' or p['columns'].startswith("auto") else [('s'+str(x) if is_number(x) else x) for x in range(len(data.loc[0]))]
            view_columns=str.strip(p['view_columns'])
            if view_columns!="" :
                view_set=set(view_columns.split(',') )
                data_set=set(data.columns)
                if len(view_set- data_set )>0:
                    raise RuntimeError(f"{p['name']}以下列已经被删除：{str(view_set- data_set)}。新增的列:{str(data_set - set(p['old_columns']))} " )
                data=data[[ (data.columns[int(x)] if x.isdigit() else x) for x in view_columns.split(',')]]
        if isinstance(p['view_columns'],list):
            if len(p['view_columns'])!=0 :
                data=data[p['view_columns']]

        key_column=p.get('key_column')
        if key_column is None:
            for key in data.columns :
                if str(data[key].dtype)=='object' and  len(data[key].unique())==len(data):
                    key_column=key
                    break
        if key_column is None:
            key_column=data.columns[0]
        if key_column not in data.columns:
            raise Exception(f"{p['name']}的关键字{key_column} 不在可视列表中！通常是原始报表的列名被修改了，你可以在《查看列名》的地方，将主键选为key，清空《最终数据整理》中的信息，重新执行就可以了。")
        p['key_column']=key_column
        data=data[(data[key_column]!='') & (data[key_column].isnull()==False)].reset_index(drop=True)
        data=data.replace('','None')#先删除主键为空的情况，然后其他为字符串空替换为None
        if p.get("backup",'').strip()!='':
                rptid=os.path.realpath(upload_path).split("\\")[-1]
                bak_file=os.path.realpath(os.path.join(upload_path+"../../../过往数据/", f"{rptid}_{p['name']}"))
                if os.path.exists(f"{bak_file}_上次.json"):
                    os.remove(f"{bak_file}_上次.json")
                if os.path.exists(f"{bak_file}_上次_new.json"):
                    os.rename(f"{bak_file}_上次_new.json",f"{bak_file}_上次.json")
                cur_bak_list=sorted(glob.glob(f"{bak_file}*"),key=os.path.getmtime)
                cur_bak_list=[x for x in cur_bak_list if x!=f"{bak_file}_上次_new.json"]
                if len(cur_bak_list)!=0:#只记当天的增量
                    if (datetime.datetime.now() - datetime.datetime.fromtimestamp(os.path.getmtime(cur_bak_list[-1]) )).days ==0:
                        shutil.copyfile( cur_bak_list[-1] , f"{bak_file}_上次_new.json")
                for one_file in cur_bak_list: #删除 超过8天的历史数据
                    if (datetime.datetime.now() - datetime.datetime.fromtimestamp(os.path.getmtime(one_file) )).days >9:
                        os.remove(one_file)
                #if datetime.date.today()==one['from'][2:8]:#备份当前数据
                with open(f"{bak_file}_{datetime.date.today().isoformat()}.json", 'w') as f:
                    f.write(data.to_json(orient='records',force_ascii=False))
                #data.to_csv(f"{bak_file}.csv",index=False)
        p['old_columns']=header

        ret[p['name']]={'data':data,'p':p,'header':header,'form_input':data_from['form_input'],"data_from":data_from}            
    adapter=None
    return ret

def appendData_and_execLastSql(one_ds,ret,upload_path):
    k=one_ds['name']
    v=ret[k]

    key_column=one_ds.get('key_column')
    if key_column is None:
        for key in v['data'].columns :
            if str(v['data'][key].dtype)=='object' and  len(v['data'][key].unique())==len(v['data']):
                key_column=key
                break
    if key_column is None:
        key_column=v['data'].columns[0]
    one_ds['key_column']=key_column
    
    #t_append=v['p'].get('append')
    #if t_append is not None  and isinstance( t_append,dict):
    #    v['p']['append']=[t_append,]
    for one in v['p'].get('append',list()):
        if one.get('from','')=='':
            continue
        elif one['from'].find(".xlsx")>0:
            data=pd.read_excel(os.path.join(upload_path, one['from']))
            data[data.columns[0]]=data[data.columns[0]].astype(str)
        elif one['from'].find(".csv")>0:
            data=pd_read_csv(os.path.join(upload_path, one['from']))
        elif one['from']=='上次' or one['from'][0:2]=='备份':#备份22时05分
            other=one['from'].split(":")
            backup_name=other[1] if len(other)>1 else k
            rptid=os.path.realpath(upload_path).split("\\")[-1]
            qushu_date=datetime.date.today()+datetime.timedelta(days=-1)
            if one['from']=='上次' or one['from']=='备份上次' :
                bak_file=os.path.realpath(os.path.join(upload_path+"../../../过往数据/", f"{rptid}_{backup_name}_上次"))
            else:
                bak_file=os.path.realpath(os.path.join(upload_path+"../../../过往数据/", f"{rptid}_{backup_name}_{qushu_date.isoformat()}"))
            if os.path.exists(f"{bak_file}.json"):
                with open(f"{bak_file}.json", 'r') as f:
                    data = f.read()
                    data=pd.read_json(data)
            elif not os.path.exists(f"{bak_file}.csv"):
                data=pd.DataFrame(columns=v['data'].columns)
            else:
                data=pd_read_csv(f"{bak_file}.csv")
        elif ret.get(one['from']):
                data=ret.get(one['from'])['data']
        else:
            continue
        if one['from']=='上次' or one['from'].startswith('备份'):
            right_key_column=key_column
            data=data[data[key_column]!='']
        else:
            right_key_column=data.columns[0]
        data=data[(data[right_key_column]!='') & (data[right_key_column].isnull()==False)].reset_index(drop=True)
        data[right_key_column]=data[right_key_column].astype(str)
        if len(data[right_key_column].unique())!=len(data):
            raise Exception(f"数据集【{v['p']['name']}】 的合并数据集【{one['from']}】的[{right_key_column}]列数据不唯一！")

        v['data']=v['data'].merge(data,how ="left", left_on=key_column, right_on=right_key_column,suffixes=('', f"_{one['from']}")).fillna(0)
        v['p']['appended_cloumns']=v['data'].columns.values.tolist()

    data=v['data']
    if v['p'].get('data_is_json',False)==False:
        start_number=False
        for x in data.columns:#尽可能的将关键字列之后的数据设置为float类型
            if x==one_ds['key_column']:
                start_number=True
                continue
            if start_number==False:
                continue
            if data[x].dtype.name=='object':
                try:
                    data[x]=data[x].astype(int)
                except:
                    try:
                        data[x]=data[x].astype(float)
                    except:
                        pass
                    pass
    
    sql=v['p'].get('sql','').strip()
    if sql!="" :
        exec_sql=exec_template(None,sql,[])
        data=pandasql.sqldf(exec_sql,dict({key:value['data'] for key,value in ret.items()}))
    if(v['p'].get('vis_sql_conf') is not None and v['p']['vis_sql_conf'].get('expr','').strip()!=''):
        data=eval(k+v['p']['vis_sql_conf']['expr'],{k:data})
    v['data']=data.round(2)
    v['p']['last_columns']=data.columns.values.tolist()    


@func_time
async def load_all_data(config_data,id,appendFunDict=None,upload_path=None,userid=None,user_input_form_data=None):
    print(threading.currentThread().name)
    ret={}
    start_time = time.time()
    cur_time=time.strftime("%H时%M分")
    #取html和csv中的数据
    tasks=[]
    #loop = asyncio.get_event_loop()
    async def _inner_task(ret):
        for one in config_data['data_from']:
            if one['type']=='sql' or one['url'].startswith('结果://'):
                continue        
            elif one['type']=='file':
                filename=os.path.join(upload_path, one['url'])
                ret={**ret,**load_from_file(filename,one['ds'])}
                continue
            #elif one['type'] in ['json','html']:
            tasks.append(load_from_url2(one,config_data,upload_path,userid,user_input_form_data=user_input_form_data))
        return await asyncio.gather(*tasks,return_exceptions=True),ret
        #status_list = loop.run_until_complete(asyncio.gather(*tasks))
    #https://yanbin.blog/how-flask-work-with-asyncio/#more-10368 关于flask中的异步，这里讲的比较详细
    #status_list,ret=asyncio.run(_inner_task(ret)) 
    status_list,ret=await _inner_task(ret)
    
    for t in status_list:
        if isinstance(t,dict):
            ret={**ret,**t}  
        if isinstance(t,Exception):
            raise t
    print(colorama.Fore.RED+  f"全部取数结束，用时： {time.time()-start_time}")
    #用已定义的全局参数，覆盖所有子取数的参数合集
    form_input={}
    for one in config_data['data_from']:
        form_input={**form_input,** {x['name']:x['value'] for x in one['form_input']} }
    form_input={**form_input,** {x['name']:x['value'] for x in config_data['form_input']} } 
    config_data['form_input']=[{'name':k,'value':v} for (k,v) in form_input.items()]

    #追加数据到html数据中，一般是csv或备份或其他数据集
    for one_data_from in config_data['data_from']:
        if one_data_from['url'].startswith('结果://') or one_data_from['type']=='sql':
            continue        
        for one_ds in one_data_from['ds']:
            appendData_and_execLastSql(one_ds,ret,upload_path)
    print(f"appendData_and_execLastSql，用时： {time.time()-start_time}")
    #计算单独config_data中的sql语句
    for one_data_from in config_data['data_from']:
        if one_data_from['type']!='sql':
            continue
        for one_ds in one_data_from['ds']:
            sql_data=pd.DataFrame()
            for one in one_ds.get('append',[]):
                if one['from'].find(".csv")>0:
                    data=pd_read_csv(os.path.join(upload_path, one['from']))
                elif ret.get(one['from']):
                        data=ret.get(one['from'])['data']
                else:
                    continue
                if sql_data.empty:
                    sql_data=data
                    continue
                sql_data=sql_data.merge(data,how ="left", left_on=sql_data.columns[0], right_on=data.columns[0],suffixes=('', f"_{one['from']}")).fillna(0)
            one['appended_cloumns']=sql_data.columns.values.tolist()
            ret[one_ds['name']]={'data':sql_data.round(2)}

            sql=one_ds.get('sql','').strip()
            if sql!="" :
                exec_sql=exec_template(None,sql,[])
                sql_data=pandasql.sqldf(exec_sql,dict({key:value['data'] for key,value in ret.items()}))
            one_ds['appended_cloumns']=one['appended_cloumns']
            one_ds['last_columns']=sql_data.columns.values.tolist()
            ret[one_ds['name']]={'data':sql_data,'header':sql_data.columns.to_list(),
                'header':sql_data.columns.values.tolist(),
                'p':one_ds
                }
       
    #排序
    for k,v in ret.items():
        data=v['data']
        sort_name=str.strip(v['p']['sort'])
        if sort_name!="" :
            if isinstance(sort_name,int) or is_number(str(sort_name)):
                sort_name=data.columns[int(sort_name)]
                data=data.sort_values(sort_name,ascending= False).reset_index(drop=True)
            else:
                data[[ sort_name]]=data[[sort_name]].astype(float)
                data=data.sort_values(by=sort_name,ascending= False).reset_index(drop=True)
        v['data']=data
    print(f"排序后，用时： {time.time()-start_time}")
    ds_dict={k:v['data'] for k,v in ret.items()}
    if(config_data.get("vars") is not None):#先计算所有不是依赖excel结果的变量，这样在excel中就也可以使用变量了
        for one_var in config_data["vars"]:
            if(ds_dict.get(one_var["name"]) is not None):
                raise SyntaxError(f'变量名字<{one_var["name"]}>已被使用：')
            # 表示的就是当前变量引用的不是excel结果。
            if ds_dict.get(one_var["ds"]) is None:
                continue
            try:
                exec(one_var["name"]+"="+one_var["last_statement"],ds_dict)
                val= ds_dict[one_var["name"]]
                if isinstance(val , float):
                    val=round(val,2)
                    if float(val)-int(val)==0:
                        val=int(val)
                    ds_dict[one_var["name"]] =val  
            except SyntaxError as e:
                raise SyntaxError(f'变量<{one_var["name"]}>定义语法错误：'+str(e))
            except Exception as e:
                raise SyntaxError(f'变量<{one_var["name"]}>定义语法错误：'+str(e))
            
    print(f"变量后，用时： {time.time()-start_time}")
    ret_files=[]
    result=''
    
    out_file=f"{upload_path}/../../tmp/{id}/"
    if os.path.exists(out_file):
        shutil.rmtree(out_file)
    os.makedirs(out_file)
    print(f"rm后，用时： {time.time()-start_time}")
    # 为了能直接引用模板结果，先按模板生成结果


    for one_part in config_data.get('template_output_act',[]):
        if one_part["canOutput"]=="false":
            continue
        one_file=one_part["file"]
        template_file=f"{upload_path}/{one_file}"            
        if not os.path.exists(template_file):
            ret_files.append({'name':one_file,'errcode':'1','message' :'无此文件，请详细检查文件名','url':''})
            continue
        out_file=f"{upload_path}/../../tmp/{id}/{one_file}"
        if(one_file[-4:]=='pptx' ):            
            loopForDS=one_part.get("loopForDS",'').strip()
            if loopForDS=='':
                convert_file_for_pptx(out_file,template_file,ds_dict)
            else:
                t_ds_dict=ds_dict.copy()
                for idx,row in ds_dict[loopForDS ].iterrows():
                    t_ds_dict["_loop_"]=row
                    t_ds_dict["_idx_"]=idx            
                    convert_file_for_pptx(out_file,template_file,t_ds_dict)
        elif(one_file[-4:]=='xlsx' ):
                convert_file_for_xlsx(out_file,template_file,ds_dict, appendFunDict=appendFunDict)
        ret_files.append({'name':one_file,'errcode':'0','message' :'成功生成','url':f'/mg/file/download_t/{id}/{one_file}'})
    print(f"模板后，用时： {time.time()-start_time}")
    for data_from in config_data['data_from']:
        if not data_from['url'].startswith('结果://'):
            continue
        wb = load_workbook(f"{upload_path}/../../tmp/{id}/{data_from['url'][len('结果://'):]}",data_only=True)
        try:
            if len(wb.defined_names.definedName)==0:
                continue
            if data_from['ds'] is None or len(data_from['ds'])==0:
                data_from['ds']=[{"t": "json","pattern": wb.defined_names.definedName[0].name,"end": '',
                        "start": '',"columns": "auto","view_columns": "","sort": "","name": "修改这里",
                        "old_columns":[]}]
            for one_ds in data_from['ds']:
                has_define=False
                for my_range in wb.defined_names.definedName:
                    if my_range.name != one_ds['pattern']:
                        continue
                    has_define=True
                    for title, coord in my_range.destinations: # returns a generator of (worksheet title, cell range) tuples
                        ws = wb[title]
                        cell_ranges=ws[coord]
                        col_nums=cell_ranges[-1][-1].column -cell_ranges[0][0].column +1 
                        row_nums=cell_ranges[-1][-1].row -cell_ranges[0][0].row +1
                        excel_results= [[None] * col_nums for i in range(row_nums)]
                        for row in cell_ranges:
                            for cell in row:
                                if cell.value is None:
                                    continue
                                for one_merged_cell in ws.merged_cells:
                                    if cell.row == one_merged_cell.min_row  and cell.column ==one_merged_cell.min_col :
                                        for i_row in range(one_merged_cell.max_row-one_merged_cell.min_row +1):
                                            for i_col in range(one_merged_cell.max_col-one_merged_cell.min_col+1 ):
                                                excel_results[i_row + cell.row - cell_ranges[0][0].row][i_col+cell.column -cell_ranges[0][0].column]=cell.value
                                        continue
                                excel_results[cell.row - cell_ranges[0][0].row][cell.column -cell_ranges[0][0].column]=cell.value
                        header,end_line=guess_col_names(excel_results,"auto")
                        data=pd.DataFrame(excel_results[end_line:],columns=header)
                        ret[one_ds['name']]={'data':data,'header':header,'p':one_ds}
                        
                        one_ds['last_columns']=header
                        one_ds['old_columns']=header
                        appendData_and_execLastSql(one_ds,ret,upload_path)
                        ds_dict[one_ds['name']]=ret[one_ds['name']]['data'] # 添加到变量表中
                        break
                if has_define==False:
                    raise Exception(data_from['url'] +'，不存在名称：'+one_ds['pattern'])
        finally:
            wb.close()
            wb=None
    return ds_dict

async def files_template_exec(id,config_data,userid,app_save_path,appendFunDict=None,wx_queue=None):
    '''
    生成模板文件
    '''
    if wx_queue is None:
        wx_queue=glb.msg_queue
    upload_path=f"{app_save_path}\\{userid}\\{id}"
    ds_dict=await load_all_data(config_data,id,appendFunDict,upload_path=upload_path,userid=userid)
    #ds_dict={**{k:v['data'] for k,v in ret_dataset.items()},**ds_dict}
    
    if(config_data.get("vars") is not None):
        for one_var in config_data["vars"]:
            # 只计算没有计算过的变量
            if(ds_dict.get(one_var["name"]) is not None):
                continue
            try:
                exec(one_var["name"] +"="+one_var["last_statement"],ds_dict)
                val= ds_dict[one_var["name"]]
                if isinstance(val , float):
                    val=round(val,2)
                    if float(val)-int(val)==0:
                        val=int(val)
                    ds_dict[one_var["name"]]=val
                
            except SyntaxError as e:
                raise SyntaxError(f'变量<{one_var["name"]}>定义语法错误：'+e.text)
            except Exception as e:
                raise SyntaxError(f'变量<{one_var["name"]}>定义语法错误：'+str(e))
            


    ret_files=[]
    result=''

    for one_part in config_data.get('template_output_act',[]):
        if one_part["canOutput"]=="false":
            continue
        one_file=one_part["file"]
        template_file=f"{upload_path}/{one_file}"            
        if not os.path.exists(template_file):
            ret_files.append({'name':one_file,'errcode':'1','message' :'无此文件，请详细检查文件名','url':''})
            continue
        out_file=f"{upload_path}/../../tmp/{id}/{one_file}"
        if(one_file[-4:]=='pptx' ):
            out_file=out_file.replace("\\","/")                  
            for wx_user in one_part["wx_msg"].strip().split(",")  :
                for one_img in glob.glob(out_file[:-5]+"_*/*.JPG"):
                    one_img=one_img.replace("\\","/")
                    wx_queue.put({'type':'sendImage',"wxid":wx_user,"content":one_img})
            for wx_user in one_part["wx_file"].strip().split(","):
                wx_queue.put({'type':'sendFile',"wxid":wx_user,"content":out_file})        
        elif(one_file[-4:]=='xlsx' ):
                out_file=out_file.replace("\\","/")
                for wx_user in one_part["wx_msg"].strip().split(","):
                    for one_img in glob.glob(out_file+"*.png"):
                        one_img=one_img.replace("\\","/")
                        wx_queue.put({'type':'sendImage',"wxid":wx_user,"content":one_img})
                for wx_user in one_part["wx_file"].strip().split(","):
                    wx_queue.put({'type':'sendFile',"wxid":wx_user,"content":out_file})
        elif(one_file[-3:]=='txt' ):
                message=convert_file_for_txt(out_file,template_file,ds_dict)
                out_file=out_file.replace("\\","/")
                for wx_user in one_part["wx_file"].strip().split(","):
                    wx_queue.put({'type':'sendFile',"wxid":wx_user,"content":out_file})
                #神奇的作用，emoji可以发送到微信中了
                #message=json.dumps(message)[1:-1].encode().decode('unicode_escape') 
                for wx_user in one_part["wx_msg"].strip().split(","):
                    wx_queue.put({'type':'sendMessage',"wxid":wx_user,"content":message})
        ret_files.append({'name':one_file,'errcode':'0','message' :'成功生成','url':f'/mg/file/download_t/{id}/{one_file}'})

    tpl_results=[]

    def loop_one_txt(one_part,t_ds_dict,idx=0):
        expr_html=lxml.html.fromstring(one_part['txt']).text_content()
        if expr_html.startswith("http"):
            last_append=datetime.datetime.now().strftime("%#d%#H%#M%S")
            txt_tpl=f"http://hnapp.e-chinalife.com/weixin2/RedirctHandler2.aspx/637A7394-C8FE-4A8B-9D3A-7E7ADA492CE4/a{id}_{last_append}_{idx}.html"
            convert_html(f"{upload_path}/../../tmp/html/a{id}_{last_append}_{idx}.html",expr_html.getText(),t_ds_dict)
        else:
            txt_tpl=exec_template(None,expr_html,t_ds_dict) 
        tpl_results.append({'name': one_part['name'],"result":txt_tpl.replace('\n','\n<br>'),
            "img": 'https://gw.alipayobjects.com/zos/rmsportal/WdGqmHpayyMjiEhcKoVE.png'}
        )
        message=txt_tpl#json.dumps(txt_tpl)[1:-1].encode().decode('unicode_escape')
        for wx_user in one_part.get("wx_msg",'').strip().split(","):
            if wx_user.strip()!='':
                wx_queue.put({'type':'sendMessage',"wxid":wx_user,"content":message})

    
    for one_part in config_data.get('text_tpls',[]):
        t_ds_dict=ds_dict.copy()
        loopForDS=one_part.get("loopForDS",'').strip()
        if loopForDS=='':
            loop_one_txt(one_part,t_ds_dict)
        else:
            for idx,row in ds_dict[loopForDS ].iterrows():
                t_ds_dict["_loop_"]=row
                t_ds_dict["_idx_"]=idx+1
                loop_one_txt(one_part,t_ds_dict,idx)

    out_files=f"{upload_path}/../../tmp/{id}/"
    if os.path.exists(out_files):
        out_files=os.listdir(out_files)

    return ret_files,tpl_results,out_files

if __name__ == '__main__':
    import glb
    import objgraph  
    import gc,tracemalloc
    tracemalloc.start()
    b_snapshot = tracemalloc.take_snapshot()
    for i in range(10):
        with glb.db_connect() as conn:
            with conn.cursor(as_dict=True) as cursor:
                cursor.execute("SELECT * FROM zhanbao_tbl WHERE  id=4274 order by id asc")
                row = cursor.fetchone()
                while row:
                    b1_snapshot = tracemalloc.take_snapshot()
                    try:
                        print('worker_no:'+ row['worker_no']+"\t"+ str(row['id']) +"     "+ str(tracemalloc.get_traced_memory()))
                        files_template_exec(row['id'],json.loads(row['config_txt']),row['worker_no'],glb.config['UPLOAD_FOLDER'] ,wx_queue=glb.msg_queue)  
                        print("====================================")
                        print('worker_no:'+ row['worker_no']+"\t"+ str(row['id']) +"     "+ str(tracemalloc.get_traced_memory()))
                        print("====================================")
                        snapshot2 = tracemalloc.take_snapshot()
                        top_stats = snapshot2.compare_to(b1_snapshot, 'lineno')
                        for stat in top_stats[:10]:
                            print(stat)
                        print("====================================")
                    except Exception as e:
                        print(e)
                    row = cursor.fetchone()
        gc.collect() 
        objgraph.show_most_common_types(limit=5)   
    ### 打印出对象数目最多的 50 个类型信息  
    gc.collect()    
    #_main()
