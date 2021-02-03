import sys, os, zipfile,re, requests,shutil,json,glob
import lxml
import lxml.html
from functools import reduce
import comtypes.client
import asyncio
import aiohttp
import yaml

class LoadUrlError(RuntimeError):
    def __init__(self, arg):
        self.args = [arg]

class HeNan():
    def __init__():
        self.is_cr_json=True
        self.soup=None

    def pre_parse(html_text,data_from):
        try:#新版报表可直接返回json，先按json处理，如果不能处理，就按老版本的方式处理
            self.soup =json.loads(html_text)
            form_inputs={  x['name']:"默认值" for x in self.soup['form'] }
            
            #isinstance(self.soup,dict)
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
                data_from['form_input']=[{'name':k,'value':v} for (k,v) in form_inputs.items()]
        except json.decoder.JSONDecodeError as identifier:
            self.soup = lxml.html.fromstring(html_text) 
            #查出来取数form所需要的参数，传递给前台设置到config中
            form_inputs={x.attrib['name']:"默认值" for x in self.soup.xpath('//form/input|//form/select') }
            print(f"{data_from['url']}分析html用时： {time.time()-start_time}")

            if data_from['ds'] is None or len(data_from['ds'])==0:
                t_p,ds_desc=_guess_ds()
                data_from['ds']=[t_p]
                data_from['desc']=ds_desc
                data_from['form_input']=[{'name':k,'value':v} for (k,v) in form_inputs.items()]
            print(f"{data_from['url']}_guess_ds用时： {time.time()-start_time}")
        #使用原先定义的参数设置覆盖缺省的
        form_inputs= {**form_inputs,**{x["name"]:x["value"] for x in data_from['form_input']}}
        data_from['form_input']=[{'name':k,'value':v} for (k,v) in form_inputs.items()]

    def load_data(p,data_from):
        if self.is_cr_json:
            pattern=p['pattern']
            if pattern.startswith('#'):#兼容老格式，取出核心名字
                pattern=p['pattern'][10:p['pattern'].find("thetable")]
            if isinstance(self.soup['data'],list):
                data=[x for x in self.soup['data'] if x is not None and x['name']==pattern][0]
            else:
                data=self.soup['data'][pattern]
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
                pattern_dict[p['pattern']]= __expland_merge_cells(self.soup,p['pattern'])
            table_lines=pattern_dict[p['pattern']] 
            header,_=__guess_col_names(table_lines,p['columns'])
        elif p['t']=="html":
            if not pattern_dict.get(p['pattern']) :
                pattern_dict[p['pattern']]= __expland_merge_cells(self.soup,p['pattern'])
            table_lines=pattern_dict[p['pattern']] 
            start=int(p['start'])
            end= 1000000 if not p['end'] else( int(p['start'])+int(p['end'])   if  p['end'][0]=='+' else int(p['end']))
            data=pd.DataFrame(table_lines[start:end])
            header,_=__guess_col_names(table_lines,p['columns'],start)
            p['data_is_json']=False   
        return header,data
         
    def _guess_ds():
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
        table_lines=__expland_merge_cells(self.soup,t_p['pattern'])
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
