import sys, os, zipfile,re, requests,shutil,json,glob
sys.path.append(os.path.realpath(os.curdir+"/hello_app/"))
sys.path.append(os.path.realpath(os.curdir+"/hnclic/"))
from bs4 import BeautifulSoup
import lxml
import lxml.html

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
from handle_file import convert_file_for_xlsx,exec_template,convert_file_for_txt,convert_file_for_pptx,convert_html,get_jinja2_Environment,is_number
'''
“在Windows里，time.strftime使用C运行时的多字节字符串函数strftime，
这个函数必须先根据当前locale配置来编码格式化字符串（使用PyUnicode_EncodeLocale）。”
如果不设置好locale的话，根据默认的"C" locale，底层的wcstombs函数会使用latin-1编码（单字节编码）
来编码格式化字符串，然后导致题主提供的多字节编码的字符串在编码时出错。
'''
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
        print(str(func)+'函数运行时间为：',end_time-start_time,'s')
        return ret
    return inner

def pd_read_csv(url):
    try:
        return pd.read_csv(url)
    except:
        return pd.read_csv(url,encoding='gb2312')
    #with open(url, 'rb') as f:
    #    data = f.read()
    #    f_charInfo=chardet.detect(data)                
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

def load_from_url2_forJson(data_from=None,config_data=None,user_input_form_data=None,upload_path=None,userid=None):
    soup_html = BeautifulSoup(test_html,features="lxml")    
    #__expland_merge_cells(soup,p['pattern'])
    text_html=test_string# _load_html_from_url(data_from,config_data,user_input_form_data)
    soup_json =json.loads(text_html) #html_text
    # soup.select("table")[0]['data-url']
    
    form_inputs=''
    if data_from['ds'] is None or len(data_from['ds'])==0:
        data_from['ds']=[{"t": "json","pattern": "rows","end": 10000,"start": 0,
                "columns": "auto","view_columns": "","sort": "","name": "修改这里","old_columns":[]
                }]
        data_from['desc']=""
        data_from['form_input']=''
    ret={}
    for p in data_from['ds']:
        data=pd.DataFrame(soup_json[p['pattern']] if p['pattern']!="" else soup_json)
        #将 json内的 名字转换为 table 内的名字
        data.rename(columns={ x['data-field']:x.text.strip() for x in soup_html.select("table")[0].select("th") },inplace=True) 
        # 按table 内的名字重排
        data = data[ [ x.text.strip() for x in soup_html.select("table")[0].select("th") ] ]
        header=data.columns.to_list()
        #缺省列名为：s+数字
        if isinstance(p['view_columns'],str):
            data.columns=header if p['columns'].startswith("auto") else ['s'+str(x) for x in range(len(data.loc[0]))]
            view_columns=str.strip(p['view_columns'])
            if view_columns!="" :
                data=data[[ (data.columns[int(x)] if x.isdigit() else x) for x in view_columns.split(',')]]
        if isinstance(p['view_columns'],list):
            if len(p['view_columns'])!=0 :
                data=data[p['view_columns']]
        if p.get("backup",'').strip()!='':
                rptid=os.path.realpath(upload_path).split("\\")[-1]
                bak_file=os.path.realpath(os.path.join(upload_path+"../../../过往数据/", f"{rptid}_{p['name']}"))
                #if datetime.date.today()==one['from'][2:8]:#备份当前数据
                data.to_csv(f"{bak_file}_{datetime.date.today().isoformat()}.csv",index=False)
        ret[p['name']]={'data':data,'p':p,'header':header,'form_input':form_inputs,"data_from":data_from}
    return ret

@func_time
async def load_from_url2(data_from=None,config_data=None,user_input_form_data=None,upload_path=None,userid=None):
    '''
    data_from 某网址下的取数逻辑总汇
    user_input_form_data 实际传过来的参数
    d_p_1={'t':'json','name':'b','pattern':'#reportDivaaa1thetable tr','start':'reportDivaaa1_data={"rows":','end':"/*-end-*/"}
    d_p_2={'t':'html','name':'a','pattern':'#reportDivmainthetable tr','start':4,'end':18}
    针对t:html 的end,+4 表示需要4行,不带+号的4 ，表示第4行，负数表示从后面开始倒数几行，如果为空，表示全部，最多100万行
    '''
    for i in range(1,30):
        html_text,response=await _load_html_from_url(data_from,config_data,user_input_form_data,userid)
        if html_text.find("查询报表出错")>=0:
            raise Exception(html_text)
        if(html_text.find('正在刷新缓存，请稍后再试')==-1):
            break
        else:
            print("message:正在刷新缓存，5秒后再试")
            await asyncio.sleep(5)
    if(html_text.find('正在刷新缓存，请稍后再试')>=0):
        raise LoadUrlError('没有正确取到数据，请检查设置，重新查询')
    print("成功")
    start_time = time.time()
    is_cr_json=False
    if response.status!=200:
        raise LoadUrlError(html_text+"\n"+data_from['url'])
    try:
        #if response.content_type== 'application/json'
        try:#新版报表可直接返回json，先按json处理，如果不能处理，就按老版本的方式处理
            soup =json.loads(html_text)
            form_inputs={  x['name']:"默认值" for x in soup['form'] }
            
            #isinstance(soup,dict)
            is_cr_json=True
            if data_from['ds'] is None or len(data_from['ds'])==0:
                if isinstance(soup['data'],list):
                    soup_first_data=soup['data'][0]
                else:
                    soup_first_data=[v for k,v in soup['data'].items() if v['type']!='htmlText'] [0]
                data_from['ds']=[{"t": "json","pattern": soup_first_data['name'],"end": soup_first_data['extend_lines'][1]+1,
                        "start": soup_first_data['colName_lines'][1]+1,"columns": "auto","view_columns": "","sort": "","name": "修改这里",
                        "old_columns": soup_first_data['columns']}]
                data_from['desc']=soup_first_data['title']
                data_from['form_input']=[{'name':k,'value':v} for (k,v) in form_inputs.items()]
        except json.decoder.JSONDecodeError as identifier:
            soup = lxml.html.fromstring(html_text) 
            #查出来取数form所需要的参数，传递给前台设置到config中
            form_inputs={x.attrib['name']:"默认值" for x in soup.xpath('//form/input|//form/select') }
            print(f"{data_from['url']}分析html用时： {time.time()-start_time}")

            if data_from['ds'] is None or len(data_from['ds'])==0:
                t_p,ds_desc=_guess_ds(soup)
                data_from['ds']=[t_p]
                data_from['desc']=ds_desc
                data_from['form_input']=[{'name':k,'value':v} for (k,v) in form_inputs.items()]
            print(f"{data_from['url']}_guess_ds用时： {time.time()-start_time}")
        #使用原先定义的参数设置覆盖缺省的
        form_inputs= {**form_inputs,**{x["name"]:x["value"] for x in data_from['form_input']}}
        data_from['form_input']=[{'name':k,'value':v} for (k,v) in form_inputs.items()]

        pattern_dict={}
        ret=dict()
        for p in data_from['ds']:
            if(data_from['type']=='ZYT'):
                data=pd.DataFrame(data['rows'])
                header=data.columns.to_list()
            elif is_cr_json:
                pattern=p['pattern']
                if pattern.startswith('#'):#兼容老格式，取出核心名字
                    pattern=p['pattern'][10:p['pattern'].find("thetable")]
                if isinstance(soup['data'],list):
                    data=[x for x in soup['data'] if x is not None and x['name']==pattern][0]
                else:
                    data=soup['data'][pattern]
                if data["type"]=="common":
                    start=int(p['start'])
                    end=1000000 if not p['end'] else( int(p['start'])+int(p['end'])   if isinstance(p['end'],str) and p['end'][0]=='+' else int(p['end']))
                    header=data['columns']
                    data=pd.DataFrame(data['tableData'][start:end],columns=header)                
                elif data["type"]=="large":
                    header=data['columns']
                    data=pd.DataFrame(data['data'],columns=header)
                p['data_is_json']=True

            elif p['t']=="json":
                start_pos=re.search(p['start'],html_text).regs[0][1]
                end_pos=re.search("/\*-end-\*/" if p['end']=="/*-end-*/" else p['end'],html_text).regs[0][0]
                try:
                    t_json=json.loads(html_text[start_pos:end_pos].replace("\ufeff",""))
                except json.decoder.JSONDecodeError as identifier: # 解析非标准JSON的Javascript字符串，等同于json.loads(JSON str)
                    t_json=eval( html_text[start_pos:end_pos].replace("\ufeff","") , type('Dummy', (dict,), dict(__getitem__=lambda s, n: n))())
                    #t_json=yaml.load(html_text[start_pos:end_pos].replace("\ufeff",""))
                data=pd.DataFrame(t_json)
                if 'id' in data.columns:
                    data=data.drop(['id'], axis=1)
                new_columns=data.columns.to_list()
                new_columns.sort(key=lambda x:str(len(x))+x)
                data=data[new_columns]
                p['data_is_json']=True
                if not pattern_dict.get(p['pattern']) :
                    pattern_dict[p['pattern']]= __expland_merge_cells(soup,p['pattern'])
                table_lines=pattern_dict[p['pattern']] 
                header,_=__guess_col_names(table_lines,p['columns'])
            elif p['t']=="html":
                if not pattern_dict.get(p['pattern']) :
                    pattern_dict[p['pattern']]= __expland_merge_cells(soup,p['pattern'])
                table_lines=pattern_dict[p['pattern']] 
                start=int(p['start'])
                end= 1000000 if not p['end'] else( int(p['start'])+int(p['end'])   if  p['end'][0]=='+' else int(p['end']))
                data=pd.DataFrame(table_lines[start:end])
                header,_=__guess_col_names(table_lines,p['columns'],start)
                p['data_is_json']=False
            

            #缺省列名为：s+数字
            if isinstance(p['view_columns'],str):
                data.columns=header if p['columns']=='' or p['columns'].startswith("auto") else ['s'+str(x) for x in range(len(data.loc[0]))]
                view_columns=str.strip(p['view_columns'])
                if view_columns!="" :
                    view_set=set(view_columns.split(',') )
                    data_set=set(data.columns)
                    if len(view_set- data_set )>0:
                        raise RuntimeError(f"{p['name']}以下列已经被删除：({str(view_set- data_set)})。新增的列({str(data_set - view_set)} )" )
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
        return ret
    finally:
        if soup is not None and isinstance(soup,BeautifulSoup):
            soup.decompose()
            soup=None

async def _load_html_from_url(data_from=None,config_data=None,user_input_form_data=None,userid=None):
    '''
    data_from 某网址下的取数逻辑总汇
    user_input_form_data 实际传过来的参数
    返回html
    '''
    async with aiohttp.ClientSession() as session:
    #session = requests.session()
        url=data_from['url']
        url=exec_template(None,url,[])

        start_time = time.time()
        cookies={}
        if data_from.get('grant_url') is not None and data_from.get('grant_url').strip()!="" :#授权url，获取cookies ，让取数url带过去
            real_form_data=None if data_from.get('grant_form_input') is None else {x['name']:x['value'] for x in data_from['grant_form_input']}
            async with session.get(data_from['grant_url']) if (real_form_data is None or len(real_form_data) ==0) else session.post(data_from['grant_url'],data=real_form_data) \
                 as text_html:
                cookies=text_html.cookies
    
        args=config_data.get('form_input')
        #设置取数form参数，先用用户传过来的参数覆盖总体的参数，在用总体参数覆盖具体报表的参数
        if user_input_form_data is None:
            user_input_form_data={}
        args={ x['name']: user_input_form_data.get(x['name'],x['value']) for x in config_data.get('form_input') }
        #real_args=dict() if args is None else \
        #    {x['name']:(args.get(x['name'],'默认值')  if x['value']=='默认值' else \
        #                args.get(x['value'][1:-1],'默认值') if x['value'][0]=='{' and x['value'][-1]=='}' else \
        #                x['value'] )\
        #        for x in data_from['form_input'] }
        real_args=dict()
        for x in data_from['form_input']:
            if x['value']=='默认值' and args.get(x['name'],'默认值')!='默认值':
                real_args[x['name']]=args[x['name']]
            else:
                if x['value'].startswith("{{") and x['value'].endswith("}}"):
                    real_args[x['name']]=exec_template(None,x['value'],[])
                else:
                    real_args[x['name']]=x['value']
        
        #将默认值参数去掉
        real_form_data=None if real_args is None else {k:v for (k,v) in real_args.items() if v!='默认值'}
        headers={"needType":"json","worker_no":userid}
    
        async with session.get(url,cookies=cookies,headers=headers) if (real_form_data is None or len(real_form_data) ==0) else session.post(url,data=real_form_data,cookies=cookies,headers=headers) \
            as response:
            end_time = time.time()
            print(f'{url}取数用时： {end_time-start_time}')
            text=await response.text()
            if text.startswith("\ufeff"):
                text=text[1:]
            return text,response#,text_html.content_type,'text/html'

def _guess_ds(soup):
    '''
    自动猜数据定义
    '''
    one_table=[x for x in soup.xpath('//table') if x.attrib.get("id",'').endswith('thetable')][0]
    if one_table.attrib.has_key('data-options'):
        if soup.text_content().find("/*-end-*/")>0:
            t_p={"t": "json","pattern": "#"+one_table.attrib['id'],"start": one_table.attrib['id'][0:-len("thetable")] + "_data={\"rows\":",
                "end": "/*-end-*/","columns": "auto","view_columns": "","sort": "","name": "修改这里",
                "old_columns": []
            }
        else:
            t_p={"t": "json","pattern": "#"+one_table.attrib['id'],"start": one_table.attrib['id'][0:-len("thetable")] + "_data={'total':'\\d+',\\n'rows':",
                "end": "\\n};\\r\\n\\s+allTableArr.push","columns": "auto","view_columns": "","sort": "","name": "修改这里",
                "old_columns": []
            }            
    else:
        t_p={ "t": "html","name": "修改这里","pattern": "#"+one_table.attrib['id'],"sort": "","columns": "auto","view_columns":"","old_columns":[]}
        #,"start": "4","end": "-3"
    table_lines=__expland_merge_cells(soup,t_p['pattern'])
    t_p['old_columns'],_=__guess_col_names(table_lines,t_p['columns'])    
    if t_p['t']=='html':
        start_line,end_line=-1,-1
        for line_no,one_line in enumerate( table_lines):
            if start_line==-1 and any([is_number(x) for x in one_line]):
                start_line=line_no #找到含数字的行作为结束行
            if start_line!=-1 and end_line==-1 and not any([is_number(x) for x in one_line]):
                end_line=line_no #找到含数字的行作为结束行
                break
        t_p['start']=str(start_line)
        t_p['end']=str(end_line-len(table_lines)) if end_line!=-1 else "10000"
    return t_p,(''.join([x.text_content() for x in one_table.cssselect('tr:nth-child(1) td')])) .replace(u'\xa0', u' ').strip()
        


def __expland_merge_cells(soup,h_pattern):
    '''
    将合并单元格展开
    '''
    h_pattern=h_pattern.strip()
    select_result=soup.cssselect(h_pattern)
    if h_pattern.startswith('#'):#easyui的固定行列会导致有多个table，我们将他们的数据按行合并起来
        if len(select_result)>0 and select_result[0].attrib.has_key('data-options'):
            all_heads=[x for x in [__expland_merge_cells(one,'tr') for one in select_result[0].cssselect('thead')] if len(x)>0] #可以排除没有固定列的情况
            return [ [y for x in one_line for y in x] for one_line in [x for x in zip(*all_heads) ] ]
    #如果不是tr结尾，就自动添加一个上去
    if not h_pattern.strip().endswith('tr'):
        h_pattern=h_pattern+' tr'
        select_result=soup.cssselect(h_pattern)
    idex_t=[] #存储每行的展开合并单元格的数据
    lines=len(select_result)
    idex_t=[[]]*lines
    for i_tr, tr in enumerate(select_result):
        lj_col=0
        for td in tr.xpath("th|td"):
            i_col=int(td.attrib.get('colspan','1'))
            i_row=int(td.attrib.get('rowspan','1'))
            #保证有充足的地方存放数据
            for x in range(i_row):
                while len(idex_t[i_tr+x]) < lj_col+i_col : 
                    idex_t[i_tr+x]=idex_t[i_tr+x]+[None]
            for x in range(i_row):
                for y in range(i_col):
                    #保证有充足的地方存放数据
                    try:
                        while(lj_col+y>=len(idex_t[i_tr+x])):
                             idex_t[i_tr+x]=idex_t[i_tr+x]+[None]
                        while(idex_t[i_tr+x][lj_col+y] is not None):#找到第一个None的地方，填充
                            lj_col=lj_col+1
                            while(len(idex_t[i_tr+x]) < lj_col+i_col ):
                                idex_t[i_tr+x]=idex_t[i_tr+x]+[None]
                    except IndexError as e:
                        print(e)
                    #存放数据
                    idex_t[i_tr+x][lj_col+y]="".join(td.text_content().split())#去除特殊字符的专业写法 "".join(str.strip(td.text)) #td.text.split()
            lj_col=lj_col+i_col
    return idex_t

class LoadUrlError(RuntimeError):
    def __init__(self, arg):
        self.args = [arg]


def __guess_col_names(all_lines,rule_str=None,end_line=None):
    '''
    猜测表头。end_line=None:找到含数字的行作为结束行,或找到最后一行结束
    '''
    if(end_line is None):end_line=len(all_lines)
    for line_no,one_line in enumerate( all_lines):
        if any([is_number(x) for x in one_line]):
            end_line=line_no #找到含数字的行作为结束行
            break
    start_line=0
    for x in all_lines[:end_line]:
        t=set(x)
        t.discard('') #前面只有一个cell的行是标题行。我们跳过去
        if len(t)<2:start_line+=1
        else:break
    rule=0
    if rule_str.startswith('auto'):#auto后面跟的数字，表示要去几行合并到一起后的文字作为列名
        rule= end_line-start_line if rule_str=='auto' else int(rule_str[4:]) if is_number(rule_str[4:]) else 1
    try:
        ret=all_lines[end_line-1]
    except:
        raise LoadUrlError('没有正确取到数据，请检查设置，重新查询')
    if rule>0:
        df=pd.DataFrame.from_records(all_lines[end_line-rule:end_line])
        for y in range(df.shape[1]):#列数
            for x in range(df.shape[0]-1):#行数
                if df.loc[x][y]==df.loc[x+1][y]:#去除同一列不同行上下相邻为同值的上一行的数据
                    df.loc[x][y]=''
        ret=df.sum().to_list()
    else :
        if rule<0:
           return all_lines[end_line+rule:end_line]
    def inner_func(x,y,i=0):
        return x+[y] if y not in x else x+[y+str(i)] if (y+str(i)) not in x else inner_func(x,y,i+1)

    return reduce(inner_func, [[], ] + ret) ,end_line #将重复的表头后面加上序号

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

import threading
def load_all_data(config_data,id,appendFunDict=None,args=None,upload_path=None,userid=None):
    print(threading.currentThread().name)
    ret={}
    cur_time=time.strftime("%H时%M分")
    #取html和csv中的数据
    tasks=[]
    #loop = asyncio.get_event_loop()
    async def _inner_task(ret):
        for one in config_data['data_from']:
            if one['url'].startswith('结果://'):
                continue        
            if one['type'] in ['json','html']:
                tasks.append(load_from_url2(one,config_data,args,upload_path,userid))
            #if one['type']=='json':
            #   tasks.append(load_from_url2_forJson(one,config_data,args,upload_path,userid))
            if one['type']=='file':
                filename=os.path.join(upload_path, one['url'])
                ret={**ret,**load_from_file(filename,one['ds'])}
        return await asyncio.gather(*tasks),ret
        #status_list = loop.run_until_complete(asyncio.gather(*tasks))
    try:#https://yanbin.blog/how-flask-work-with-asyncio/#more-10368 关于flask中的异步，这里讲的比较详细
        status_list,ret=asyncio.run(_inner_task(ret)) 
        for t in status_list:
            ret={**ret,**t}  
    finally:
        pass
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
        #ret={**ret,**load_from_exists_df(one['ds'], dict({key:value['data'] for key,value in ret.items()}))}
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

    ds_dict={k:v['data'] for k,v in ret.items()}
    if(config_data.get("vars") is not None):#先计算所有不是依赖excel结果的变量，这样在excel中就也可以使用变量了
        for one_var in config_data["vars"]:
            if(ds_dict.get(one_var["name"]) is not None):
                raise SyntaxError(f'变量名字<{one_var["name"]}>已被使用：')
            if one_var["var_type"]!="detail" or ds_dict.get(one_var["ds"]) is None:
                continue
            try:
                val= eval(one_var["last_statement"],ds_dict)
            except SyntaxError as e:
                raise SyntaxError(f'变量<{one_var["name"]}>定义语法错误：'+e.text)
            except Exception as e:
                raise SyntaxError(f'变量<{one_var["name"]}>定义语法错误：'+str(e))
            
            if isinstance(val , float):
                val=round(val,2)
                if float(val)-int(val)==0:
                    val=int(val)
            ds_dict[one_var["name"]]=val

    ret_files=[]
    result=''
    
    out_file=f"{upload_path}/../../tmp/{id}/"
    if os.path.exists(out_file):
        shutil.rmtree(out_file)
    os.makedirs(out_file)
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
                convert_file_for_xlsx(out_file,template_file,ds_dict,appendFunDict=appendFunDict)
        ret_files.append({'name':one_file,'errcode':'0','message' :'成功生成','url':f'/mg/file/download_t/{id}/{one_file}'})

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
            for one_ds in one_data_from['ds']:
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
                        header,end_line=__guess_col_names(excel_results,"auto")
                        data=pd.DataFrame(excel_results[end_line:],columns=header)
                        ret[one_ds['name']]={'data':data,'header':header,'p':one_ds}
                        one_ds['last_columns']=header
                        one_ds['old_columns']=header
                        appendData_and_execLastSql(one_ds,ret,upload_path)
                        break
                if has_define==False:
                    raise Exception(data_from['url'] +'，不存在名称：'+one_ds['pattern'])
        finally:
            wb.close()
    #for index,row in ret['a']['data'].iterrows():
    #    print(row)
    return ret

def load_from_exists_df(d_p,ds_dict):
    ret=dict()
    data=None
    for p in d_p:
        if p['t']=='sqlite':
            exec_sql=exec_template(None,p['pattern'],[])
            data=pandasql.sqldf(exec_sql,ds_dict)
        ret[p['name']]={'data':data,'p':p,'header':data.columns.to_list()}
    return ret

def files_template_exec(id,config_data,userid,app_save_path,appendFunDict=None,wx_queue=None):
    '''
    生成模板文件
    '''
    upload_path=f"{app_save_path}\\{userid}\\{id}"
    ret_dataset=load_all_data(config_data,id,appendFunDict,upload_path=upload_path,userid=userid)
    ds_dict={k:v['data'] for k,v in ret_dataset.items()}
    
    if(config_data.get("vars") is not None):
        for one_var in config_data["vars"]:#计算依赖excel结果的变量，已经计算的在ds_dict中已经存在了
            if(ds_dict.get(one_var["name"]) is not None):
                continue
            if one_var["var_type"]!="detail" :
                continue
            try:
                val= eval(one_var["last_statement"],ds_dict)
            except SyntaxError as e:
                raise SyntaxError(f'变量<{one_var["name"]}>定义语法错误：'+e.text)
            except Exception as e:
                raise SyntaxError(f'变量<{one_var["name"]}>定义语法错误：'+str(e))
            
            if isinstance(val , float):
                val=round(val,2)
                if float(val)-int(val)==0:
                    val=int(val)
            ds_dict[one_var["name"]]=val

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
    return ret_files,tpl_results

def _main() :  
    sys.path.append(os.path.realpath(os.curdir))
    ret=load_from_url2("http://report.hn.clic/report3/default.aspx?reportName=2019/3jidu/gx_2019_3jidu_new.cr",
                [{'t':'html','name':'a','pattern':'#reportDivmainthetable tr','start':4,'end':'+18','sort':4,'columns':"auto",'view_columns':'0,1,2,3,4'},
                {'t':'html','name':'b','pattern':'#reportDivmainthetable tr','start':3,'end':'+1','sort':None,'columns':"auto",'view_columns':None}
                ]
            )
    ret2=load_from_url2("http://report.hn.clic/report3/default.aspx?reportName=2019/2jidu/gx_bole.cr",
            [{'t':'json','name':'b','pattern':'#reportDivaaa1thetable tr','start':'reportDivaaa1_data={"rows":','end':"/*-end-*/",'sort':None,'columns':"auto",'view_columns':None}]
        )

    t1=ret['a']['data']
    t2=ret2['b']['data']

    t_left=t1[4:]
    t_right=t1[:-4]
    print(pd.merge(left=t_left,right=t_right,left_on='机构代码',right_on='机构代码',how='outer'))

    #pysqldf = lambda q: pandasql.sqldf(q)
    print(pandasql.sqldf("select * from t_left t1 left join t_right t2 on t1.机构代码=t2.机构代码"))

    def Merge(dict1, dict2): 
        res = {**dict1, **dict2} 
        return res     
    ds_dict={}
    ds_dict=Merge(ds_dict,ret)
    template_file= "out.xlsx"
    out_filename='bb.xlsx'
    convert_file_for_xlsx(out_filename,template_file,ds_dict)
    print("done!!!")
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
