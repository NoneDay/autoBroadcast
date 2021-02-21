import asyncio
import glob
import json
import os
import re
import shutil
import sys
import time
import zipfile
from functools import reduce
import aiohttp
import lxml
import lxml.html
import requests
import yaml
from hnclic.utils import is_number,guess_col_names,htmltableToArray,exec_template,get_real_form_data

from DataInterface import DataInterface

class LoadUrlError(RuntimeError):
    def __init__(self, arg):
        self.args = [arg]


class MyDataInterface(DataInterface):
    def __init__(self,data_from,userid,login_getData_template,user_password):
        super().__init__(data_from,userid,login_getData_template,user_password)
        self.is_cr_json=False
        self.soup=None
        self.start_time = time.time()
        self.pattern_dict={}
        
    async def getData(self,url,input_params={}):        
        for i in range(1,30):
            self.html_text,response_content_type,response_status=await self._load_html(url,input_params)
            if self.html_text.find("查询报表出错")>=0:
                raise Exception(self.html_text)
            if(self.html_text.find('正在刷新缓存，请稍后再试')==-1):
                break
            else:
                print("message:正在刷新缓存，5秒后再试")
                await asyncio.sleep(5)
        if(self.html_text.find('正在刷新缓存，请稍后再试')>=0):
            raise LoadUrlError('没有正确取到数据，请检查设置，重新查询')
        if response_status!=200:
            raise LoadUrlError(self.html_text+"\n"+self.data_from['url'])
       
        data_from=self.data_from
        #新版报表可直接返回json，先按json处理，如果不能处理，就按老版本的方式处理
        if response_content_type=='application/json':
            self.soup =json.loads(self.html_text)
            #form_inputs={  x['name']:"默认值" for x in self.soup['form'] }
            form_inputs=[{'name':x['name'],'value':"默认值",'label':x['prompt'],'type':x['data_type'],'valueList':x['tagValueList']} for x in self.soup['form'] ]
            
            self.is_cr_json=True
            if data_from['ds'] is None or len(data_from['ds'])==0:
                if isinstance(self.soup['data'],list):
                    soup_first_data=self.soup['data'][0]
                else:
                    soup_first_data=[v for k,v in self.soup['data'].items() if v['type']!='htmlText'] [0]
                data_from['ds']=[{"t": "json","pattern": soup_first_data['name'],"end": soup_first_data['extend_lines'][1]+1,
                        "start": soup_first_data['colName_lines'][1]+1,"columns": "auto","view_columns": "","sort": "","name": "修改这里",
                        "old_columns": soup_first_data['columns']}]
                data_from['desc']=soup_first_data['title']
        else:
            self.soup = lxml.html.fromstring(self.html_text) 
            #查出来取数form所需要的参数，传递给前台设置到config中
            form_inputs=[]
            for x in self.soup.xpath('//form/input|//form/select'):
                one={'name':x.attrib['name'],'value':"默认值" ,'type':x.get('type')}
                if x.attrib.get('data-options'):
                    one['valueList']=re.search('data:\[([\s|\S]*)',x.attrib['data-options'])[1]
                form_inputs.append(one)
            print(f"{data_from['url']}分析html用时： {time.time()-self.start_time}")

            if data_from['ds'] is None or len(data_from['ds'])==0:
                data_from['ds'],data_from['desc']=self._guess_ds()
            print(f"{data_from['url']}_guess_ds用时： {time.time()-self.start_time}")
        return self.soup,form_inputs,None

    async def _load_html(self,url,input_params):
        '''
        先模拟登陆，然后访问真正的网址
        '''        
        start_time=time.time()
        cookies={}
        data_from=self.data_from
        if data_from.get('grant_url') is not None and data_from.get('grant_url').strip()!="" :#授权url，获取cookies ，让取数url带过去
            real_form_data=None if data_from.get('grant_form_input') is None else {x['name']:x['value'] for x in data_from['grant_form_input']}
            text,content_type,status,cookies=await super().post(data_from['grant_url'],data=real_form_data)
            
        text,content_type,status,_=await super().post(url,data=input_params,cookies=cookies)
        if text.startswith("\ufeff"):
            text=text[1:]
        return text,content_type,status

    def load_data_for_p(self,p):
        if self.is_cr_json:#这是我的新报表的数据格式分析
            pattern=p['pattern']
            if pattern.startswith('#'):#兼容老格式，取出核心名字
                pattern=p['pattern'][10:p['pattern'].find("thetable")]
            if isinstance(self.soup['data'],list):
                data=[x for x in self.soup['data'] if x is not None and x['name']==pattern]
                if len(data)==0:
                    raise RuntimeError("数据集<"+p["name"]+">无数据，请检查设置是否正确.通常做法：删除你手工建的数据集，然后直接点击查看数据就可以自动生成。")
                data=data[0]
            else:
                data=self.soup['data'][pattern]

            p['data_is_json']=True    
            if data["type"]=="common":
                start=int(p['start'])
                end=1000000 if not p['end'] else( int(p['start'])+int(p['end'])   if isinstance(p['end'],str) and p['end'][0]=='+' else int(p['end']))
                return "TableModel",data['columns'],data['tableData'][start:end],None
            elif data["type"]=="large":
                return "TableModel",data['columns'],data['data'],None
        elif p['t']=="json":#这是老格式的大数据报表分析
            start_pos=re.search(p['start'],self.html_text).regs[0][1]
            end_pos=re.search("/\*-end-\*/" if p['end']=="/*-end-*/" else p['end'],self.html_text).regs[0][0]
            try:
                t_json=json.loads(self.html_text[start_pos:end_pos].replace("\ufeff",""))
            except json.decoder.JSONDecodeError as identifier: # 解析非标准JSON的Javascript字符串，等同于json.loads(JSON str)
                t_json=eval( self.html_text[start_pos:end_pos].replace("\ufeff","") , type('Dummy', (dict,), dict(__getitem__=lambda s, n: n))())
                #t_json=yaml.load(html_text[start_pos:end_pos].replace("\ufeff",""))
            json_props=[x for x in t_json[0]]
            json_props.sort(key=lambda x:str(len(x))+x)
            p['data_is_json']=True
            if not self.pattern_dict.get(p['pattern']) :
                self.pattern_dict[p['pattern']]= MyDataInterface.__expland_merge_cells(self.soup,p['pattern'])
            table_lines=self.pattern_dict[p['pattern']] 
            header,_=guess_col_names(table_lines,p['columns']) #json模式。有列名和json属性的的对照
            return "JsonModel",header,t_json,json_props
        elif p['t']=="html":#这是老格式的自由数据报表分析
            if not self.pattern_dict.get(p['pattern']) :
                self.pattern_dict[p['pattern']]= MyDataInterface.__expland_merge_cells(self.soup,p['pattern'])
            table_lines=self.pattern_dict[p['pattern']] 
            start=int(p['start'])
            end= 1000000 if not p['end'] else( int(p['start'])+int(p['end'])   if  p['end'][0]=='+' else int(p['end']))
            header,_=guess_col_names(table_lines,p['columns'],start)
            p['data_is_json']=False   #table模式。有列名和明细数据的的表模式
            return "TableModel",header,table_lines[start:end],None
    
    def _guess_ds(self):
        '''
        自动猜数据定义
        '''
        one_table=[x for x in self.soup.xpath('//table') if x.attrib.get("id",'').endswith('thetable')][0]
        if one_table.attrib.has_key('data-options'):
            if self.soup.text_content().find("/*-end-*/")>0:
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
        table_lines=MyDataInterface.__expland_merge_cells(self.soup,t_p['pattern'])
        t_p['old_columns'],_=guess_col_names(table_lines,t_p['columns'])    
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
        return [t_p],(''.join([x.text_content() for x in one_table.cssselect('tr:nth-child(1) td')])) .replace(u'\xa0', u' ').strip()
            

    @staticmethod
    def __expland_merge_cells(soup,h_pattern):
        '''
        将合并单元格展开
        '''
        h_pattern=h_pattern.strip()
        select_result=soup.cssselect(h_pattern)
        if h_pattern.startswith('#'):#easyui的固定行列会导致有多个table，我们将他们的数据按行合并起来
            if len(select_result)>0 and select_result[0].attrib.has_key('data-options'):
                #可以排除没有固定列的情况
                all_heads=[x for x in [MyDataInterface.__expland_merge_cells(one,'tr') for one in select_result[0].cssselect('thead')] if len(x)>0]
                return [ [y for x in one_line for y in x] for one_line in [x for x in zip(*all_heads) ] ]
        #如果不是tr结尾，就自动添加一个上去
        if not h_pattern.strip().endswith('tr'):
            h_pattern=h_pattern+' tr'
            select_result=soup.cssselect(h_pattern)
        return htmltableToArray(select_result)