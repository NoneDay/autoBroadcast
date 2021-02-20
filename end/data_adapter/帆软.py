import sys, os, re, json
import yaml
import lxml
import lxml.html
import time,datetime,arrow
import asyncio,aiohttp
from hnclic.utils import htmltableToArray,exec_template,get_real_form_data
from DataInterface import DataInterface
import urllib.parse
class MyDataInterface(DataInterface):
    def __init__(self,data_from,userid,login_getData_template,user_password):
        super().__init__(data_from,userid,login_getData_template,user_password)
        self.soup=None
 
    def __parse3(self,fr_sjon):
        detail=fr_sjon['pageContent']['detail']
        cellData=detail[0]['cellData']
        pageLayoutInfo=detail[0]['pageLayoutInfo']
        table_result=[]
        for r in range(pageLayoutInfo['rowCount']):
            row=[]
            table_result.append(row)
            for c in range(pageLayoutInfo['colCount']):
                row.append(None)

        for tr in cellData['rows']:
            for td in tr['cells']:
                row=td['row']
                col=td['col']
                for r_i in range(td['rowSpan']):
                    for c_i in range(td['colSpan']):
                        v=td.get('text')
                        if td.get('isnumber'):
                            v=float(v)
                            int_v=int(v)
                            if(int_v==v):
                                v=int_v
                        if table_result[row+r_i][col+c_i] is None:
                            table_result[row+r_i][col+c_i]=v
        show_columms=[]
        
        for idx,cw in enumerate(pageLayoutInfo['colWidth']) :
            if cw!=0:
                show_columms.append(idx)
        ret=[]
        for tr in table_result :
            td_list=[]
            ret.append(td_list)
            for idx,td in enumerate(tr):
                if idx in show_columms:
                    td_list.append(td)
        return ret,None

    async def getData(self,url,input_params={}):
        html_text,content_type,status,_=await super().post(url)
       
        #模式1
        sessionID_search=re.search("this.currentSessionID[\s]*=[\s]*\'(.*)\'",html_text)
        if sessionID_search:
            param_result=re.search("this\.loadReportPane\(([\s|\S]*)\);(\s)*\}\)\.apply\(contentPane\);",html_text,re.M)[1]
            return await self.__getData_1(url,sessionID_search[1],param_result,input_params)
        #模式2
        sessionID_search=re.search("FR\.SessionMgr\.register\(\"(.*)\"",html_text)
        if sessionID_search:
            return await self.__getData_2(url,sessionID_search[1],input_params)
        #模式3 h5
        sessionID_search=re.search("get\s+sessionID\(\s*\)\s+{return\s+\'(.*)\'",html_text)
        if sessionID_search:
            queryString=urllib.parse.unquote(urllib.parse.unquote(url[url.find("?")+1:]))
            
            return await self.__getData_3(url,sessionID_search[1],input_params,queryString)

        raise RuntimeError("没有找到合适的匹配转换")
    async def __getData_3(self,url,sessionID,input_params,queryString):  
        self.next_headers['sessionID']=sessionID
        url_head=re.search("^http[s]?:[\d]*//[\w|\W|\.]+?/",url)[0]+self.login_data['data']['url']
        parameters=re.search("__parameters__=(.*)&",queryString)[1]
        form_refresh_html_text,content_type,status,_=await super().post(f"{url_head}/url/mobile/view/firstdata?op=h5&cmd=firstdata&_={str(int(time.time()))}&__parameters__={parameters}&sessionID={sessionID}")
        param_list=yaml.unsafe_load( re.sub("\"listeners\":\[\{[\s|\S]*?\}\],","",form_refresh_html_text) )['parameter']
        form_inputs=self.parse_params(param_list)
        #先提交参数
        form_data={"__parameters__":json.dumps({**form_inputs,**input_params})}
        param_url=f"{url_head}/view/report?op=fr_dialog&cmd=parameters_d"
        text,content_type,status,_=await super().post(param_url,data=form_data)
        result_url=f"{url_head}/view/report?toVanCharts=true&dynamicHyperlink=true&op=page_content&cmd=json&sessionID={sessionID}&fine_api_v_json=3&pn=1&__fr_locale__=zh_CN"
        text,content_type,status,_=await super().post(result_url)
        ret,title=self.__parse3(json.loads(text))
        return ret ,form_inputs,title    
    async def __getData_2(self,url,sessionID,input_params={}):        
        self.next_headers['sessionID']=sessionID
        url_head=re.search("^http[s]?:[\d]*//[\w|\W|\.]+?/",url)[0]+self.login_data['data']['url']
        form_refresh_html_text,content_type,status,_=await super().post(f"{url_head}/view/form?op=form_refresh&cmd=config&_={str(int(time.time()))}")
        load_content_html_text,content_type,status,_=await super().post(f"{url_head}/view/form?op=fr_form&cmd=load_content&widgetVersion=1&_={str(int(time.time()))}")
        fit_config_html_text,content_type,status,_=await super().post(f"{url_head}/view/form?op=fr_form&cmd=fit_config&widgetVersion=1&_={str(int(time.time()))}&_PAPERWIDTH=980&_PAPERHEIGHT=1003&_SHOWPARA=true&_SHOWPARATEMPLATE=false")
        fit_config=json.loads(fit_config_html_text)
        retDict={}
        title=None
        for x in fit_config['elementCases']:
            ret,t_title=await self.__html_frame(f"{url_head}/view/form",data={'op': 'fr_form','cmd':'load_report_content','widgetName':x,'__parameters__':None,'noCache':'',
            '_':int(time.time()),'__boxModel__':True,'reload':None,'_PAPERWIDTH':980,'_PAPERHEIGHT':1003, '_SHOWPARA':True,'_SHOWPARATEMPLATE':False})
            if title is None:
                title=t_title
            if len(ret):
                retDict[x]=ret
        return retDict,{},title

    def parse_params(self,param_json):
        form_inputs={}
        for one in param_json:
            if one.get('widget'):
                one_param=one.get('widget')
            else:
                one_param=one
            if one_param['type']=='formsubmit':
                continue
            if one_param['type'] in['tagcombocheckbox','combo'] and one_param.get('controlAttr'):
                #if one_param['controlAttr'].get('data'):
                #    real_value=list(filter(lambda x:x['text']==one_param['value'],one_param['controlAttr']['data']))#one_param['controlAttr']['data']
                #    #if len(real_value)>0:
                #    form_inputs[one_param['widgetName']]=real_value[0]['value']
                #else:
                form_inputs[one_param['widgetName']]=one_param['value']
                continue
            elif one_param['type'] in ['label','text']:
                form_inputs[one_param['widgetName']]=one_param['value']#todo:转unicode 用[]包起来每一个汉字
            elif one_param['type'] in ['number']:
                form_inputs[one_param['widgetName']]=int(one_param['value'])#todo:转unicode 用[]包起来每一个汉字
            elif one_param['type'] in ['datetime']:
                datetime.datetime.fromtimestamp(one_param['value']['date_milliseconds']/1000)
                form_inputs[one_param['widgetName']]=arrow.get(one_param['value']['date_milliseconds']/1000).format(one_param['format'].upper() )
            else:
                raise RuntimeError("没有这种类型转换："+one_param['type'])
        return form_inputs

    async def __getData_1(self,url,sessionID,param_result,input_params={}):        
        self.next_headers['sessionID']=sessionID
        url_head=re.search("^http[s]?:[\d]*//[\w|\W|\.]+?/",url)[0]+self.login_data['data']['url']
        
        
        param_json=yaml.unsafe_load(re.sub("\"listeners\":[\s|\S]*?\"useBookMark\"","\"useBookMark\"", param_result))['param']#['html']['items']
        form_inputs={}
        if param_json.get('html') and param_json['html'].get('items'):
            form_inputs=self.parse_params(param_json['html']['items'])
            #先提交参数
            form_data={"__parameters__":json.dumps({**form_inputs,**input_params})}
            param_url=f"{url_head}/view/report?op=fr_dialog&cmd=parameters_d"
            text,content_type,status,_=await super().post(param_url,data=form_data)
        
        ret,t_title=await self.__html_frame(f"{url_head}/view/report?_={str(int(time.time()))}&__boxModel__=true&op=page_content&__webpage__=true&_paperWidth=1280&_paperHeight=127&__fit__=false")
        return ret,form_inputs,t_title

    async def __html_frame(self,report_url_post,data=None):
        combin_tableArray=[]
        title=None
        for pn in range(1,10000):#处理分页，默认最大10000页，或者帆软返回数据中指定的最大页
            if data is None:
                text,content_type,status,_=await super().post(report_url_post+f"&pn={pn}")
                try:
                    result=json.loads(text)['html']
                    reportTotalPage=int(re.search("FR\._p\.reportTotalPage=([\d]+)",result)[1])
                except Exception as e:
                    raise RuntimeError("解析失败，不是预期的格式")
            else:
                data['pageIndex']=pn
                text,content_type,status,_=await super().post(report_url_post,data=data)
                result_json=json.loads(text)
                result=result_json['htmlTag']
                reportTotalPage=result_json['totalPage']

            soup= lxml.html.fromstring(result) 
            for table_lines in soup.cssselect(".pageContentDIV .page-block"):
                if table_lines.attrib.get("class").find("frozen-page")<0:
                    table_lines=table_lines.cssselect("table tr")
                    tableArray=htmltableToArray(table_lines)
                else:#多片的
                    # frozen-corner north west center
                    table_inner=table_lines.cssselect("#frozen-corner table tr")
                    corner_tableArray=htmltableToArray(table_inner)
                    
                    table_inner=table_lines.cssselect("#frozen-north table tr")
                    north_tableArray=htmltableToArray(table_inner)
                    
                    table_inner=table_lines.cssselect("#frozen-west table tr")
                    west_tableArray=htmltableToArray(table_inner)
                    
                    table_inner=table_lines.cssselect("#frozen-center table tr")
                    center_tableArray=htmltableToArray(table_inner)
                    
                    tableArray=[]
                    for i in range(max(len(corner_tableArray),len(north_tableArray))):
                        tr1=[] if i>=len(corner_tableArray) else corner_tableArray[i]
                        tr2=[] if i>=len(north_tableArray) else north_tableArray[i]
                        tableArray.append(tr1 + tr2 )

                    for i in range(max(len(west_tableArray),len(center_tableArray))):
                        tr1=[] if i>=len(west_tableArray) else west_tableArray[i]
                        tr2=[] if i>=len(center_tableArray) else center_tableArray[i]
                        tableArray.append(tr1 + tr2 )
            
            lasttableArray=[]
            for one_line in tableArray:
                td_set=set(one_line)
                if '' in td_set:
                    td_set.remove('')
                if len(td_set)==0:
                    continue
                if title is None and   len(td_set)==1:
                    title=list(td_set)[0]
                    continue
                if title is not None and len(td_set)==1:
                    continue
                lasttableArray.append(one_line)
            if len(lasttableArray):
                combin_tableArray.append(lasttableArray)
            if pn>=reportTotalPage:
                break
        if len(combin_tableArray)==1:
            return combin_tableArray[0],title
        if len(combin_tableArray)==0:
            return [],title

        ret=combin_tableArray[0]
        for i in range(1,len(combin_tableArray)):#合并所有的页到一个数据集
            for end_line in range(100):#表头行数，最大10行就不再处理
                if end_line>=len(combin_tableArray[i]) or set(combin_tableArray[i][end_line])!=set(ret[end_line]):
                    break
            ret=ret+combin_tableArray[i][end_line:]
        return ret,title

if __name__ == '__main__':
    #DENHF1WCTpFh6DZG/ML6Pw==
    #with open("C:\\其他省的\\帆软.json", 'r',encoding="utf8") as f:
    #    html_text = f.read()
    #parse(json.loads(html_text))
    #分页
    #data=getData("http://demo.finereport.com/decision/v10/entry/access/old-platform-reportlet-entry-602?width=1040&height=351")
    #多片
    #data=getData("http://demo.finereport.com/decision/v10/entry/access/44963dba-b642-4135-b730-878f6ee96ebf?width=1040&height=351")
    # 分页
    #data=getData("http://demo.finereport.com/decision/v10/entry/access/old-platform-reportlet-entry-606?width=1040&height=838")
    # 分栏合计
    #data=getData("http://demo.finereport.com/decision/v10/entry/access/old-platform-reportlet-entry-610?width=1040&height=838")
    # 同比环比
    #data=getData("http://demo.finereport.com/decision/v10/entry/access/old-platform-reportlet-entry-605?width=1040&height=838")
    #参数 combo label
    #data=getData("http://demo.finereport.com/decision/v10/entry/access/old-platform-reportlet-entry-618?width=1040&height=838",{"YEAR":"10"})
    #参数 text
    #data=getData("http://demo.finereport.com/decision/v10/entry/access/old-platform-reportlet-entry-621?width=1680&height=894")
    #参数 number
    data=getData("http://demo.finereport.com/decision/v10/entry/access/old-platform-reportlet-entry-622?width=1680&height=894")
    
    pass
