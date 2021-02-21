import json,yaml
import asyncio,aiohttp
from hnclic.utils import htmltableToArray,exec_template,get_real_form_data,guess_col_names,acquire_lock_with_timeout,release_lock
from hnclic import glb
class DataInterface():
    def __init__(self,data_from,userid,login_getData_template,user_password):
        self.data_from=data_from
        self.userid=userid
        self.login_getData_template=login_getData_template
        self.user_password=user_password
        self.proxy=login_getData_template.get("proxy")
        self.login_data=dict()
        self.next_cookies={}
        self.next_headers={}
        self.dropNaNColumn=False
    
    async def _login(self):

        cookies={}
        login_headers={}
        if self.login_getData_template['login_url']!='':
            form_data=self.login_getData_template['login_data_template']
            if form_data:                    
                form_data=exec_template(None,json.dumps(form_data).replace('\\"','"'),self.user_password)
                post_type=self.login_getData_template['login_data_type']
                #if self.login_getData_template['login_data_type']=="json":
                #    login_headers={'Content-Type': 'application/json'}                        
                #else:
                #    login_headers={'Content-Type':'application/x-www-form-urlencoded; charset=UTF-8'}
                form_data=json.loads(form_data)
                login_headers={**self.login_getData_template['headers'],**login_headers}

                cache_key=self.login_getData_template['type']+":"+self.user_password['username']
                identifier=await acquire_lock_with_timeout(glb.redis3,"lock:"+cache_key)
                if identifier:
                    try:
                        cache_login_data_cookies=glb.redis3.get(cache_key)
                        if cache_login_data_cookies is None:
                            self.login_data,_2,_1,cookies= await  self.post(self.login_getData_template['login_url'],
                                                        data=form_data if post_type!="json" else None,
                                                        json=form_data if post_type=="json" else None,
                                                        headers=login_headers ) 
                            cookies={k:v for k,v in cookies.items()}
                            cache_login_data_cookies={"login_data":self.login_data,"cookies":cookies}
                            glb.redis3.set(cache_key,json.dumps(cache_login_data_cookies),glb.ini.get('login_cache_second',30))
                        else:
                            glb.redis3.expire(cache_key,glb.ini.get('login_cache_second',30))
                            cache_login_data_cookies=json.loads(cache_login_data_cookies)
                            self.login_data=cache_login_data_cookies['login_data']
                            cookies=cache_login_data_cookies['cookies']
                    finally:
                        release_lock(glb.redis3,"lock:"+cache_key,identifier)
                else:
                    raise RuntimeError(f"登陆等待获取redis 锁超时<{self.login_getData_template['url']}>")

                success_flag=self.login_getData_template['login_success']
                error_flag=self.login_getData_template['login_error']
                login_name=self.login_getData_template['name']
                if success_flag:
                    if self.login_data.find(success_flag) <0:
                        raise RuntimeError(f"模拟登陆<{login_name}>失败，没有检查到登陆标志："+success_flag)
                else:
                    if self.login_data.find(error_flag) >0:
                        raise RuntimeError(f"模拟登陆<{login_name}>失败，检查到失败标志：" + error_flag)
                try:
                    self.login_data=json.loads(self.login_data)
                except:
                    self.login_data={}
            else:
                raise RuntimeError("模板定义了登陆url，但没有定义form_data")
        else:
            self.login_data={}
        return cookies,login_headers
        

    async def login_check(self):
        async with aiohttp.ClientSession() as self.session:
            return await self._login()
        
    async def load_data_from_url(self,config_data_form_input,user_input_form_data):
        data_from=self.data_from
        async with aiohttp.ClientSession() as self.session:
            cookies,login_headers=await self._login()
            temp_dict={**{"login_data":self.login_data,"userid":self.userid},**self.user_password}
            next_headers=json.loads(exec_template(None,json.dumps(self.login_getData_template['next_headers']).replace('\\"','"'),temp_dict))
            next_cookies=json.loads(exec_template(None,json.dumps(self.login_getData_template['next_cookies']).replace('\\"','"'), temp_dict))
            self.next_cookies={**cookies,**next_cookies}
            self.next_headers={**login_headers,**next_headers}
            url,real_form_data=get_real_form_data(data_from,config_data_form_input,user_input_form_data)
            self.data,form_inputs,title=await self.getData(url,real_form_data)

        if data_from['ds'] is None or len(data_from['ds'])==0:
            if data_from['desc'] is None or data_from['desc']=='':
                data_from['desc']=title
            if isinstance(self.data,dict):
                data_from['ds']=[]
                for k,v in self.data.items():
                    data_from['ds'].append({"t": "json","pattern": k,"end":10000,
                                "start": 1,"columns": "auto","view_columns": "","sort": "","name": "修改"+k,
                                "old_columns": k[0]})
                    
                data_from['ds'][0]['name']='修改这里'
            else:
                data_from['ds']=[{"t": "json","pattern": 'no',"end":10000,
                            "start": 1,"columns": "auto","view_columns": "","sort": "","name": "修改这里",
                            "old_columns": self.data[0]}]
        #使用原先定义的参数设置覆盖缺省的
        #form_inputs= {**form_inputs,**{x["name"]:x["value"] for x in data_from['form_input']}}
        #data_from['form_input']=[{'name':k,'value':v} for (k,v) in form_inputs.items()]
        
        for x in data_from['form_input']:
            a=list(filter(lambda y:y['name']==x['name'],form_inputs))
            if len(a):
                a[0]['value']=x['value']
            else:
                form_inputs.append(x)
        data_from['form_input']=form_inputs
        

    def load_data_for_p(self,p):
        start=int(p['start'])
        end=1000000 if not p['end'] else( int(p['start'])+int(p['end']) if isinstance(p['end'],str) and p['end'][0]=='+' else int(p['end']))
        if isinstance(self.data,dict):
            data=self.data[ p['pattern']]            
        else:
            data=self.data
        header,_=guess_col_names(data,p['columns'],start)
        return "TableModel",header,data[start:end],None 
    
    async def getData(self,url,input_params={}):
        # 可以自己写成远程调用
        # 所有参数已经经过了模板替换，直接使用就可以
        # start_time=time.time()
        # async with self.session.get(url,cookies=self.next_cookies,headers=self.next_headers) if (input_params is None or len(input_params) ==0) \
        #        else self.session.post(url,data=input_params,cookies=self.next_cookies,headers=self.next_headers) as response:
        #    text=await response.text()
        #    print(f'{url}取数用时： {time.time()-start_time}')
        #    return text,response.content_type,response.status #,text_html.content_type,'text/html'
        raise RuntimeError("没有实现get_data")

    async def post(self,url=None,data=None,cookies={},headers={},json=None):
        # 可以自己写成远程调用
        # 所有参数已经经过了模板替换，直接使用就可以
        t_cookies={**self.next_cookies,**cookies}
        t_headers={**self.next_headers,**headers}
        
        async with self.session.get(url,cookies=t_cookies,headers=t_headers,proxy=self.proxy) \
                if (data is None and json is None) else \
                self.session.post(url,data=data,json=json,cookies=t_cookies,headers=t_headers,proxy=self.proxy) as response:
            text=await response.text()
            if text.startswith("\ufeff"):
                text=text[1:]
            return text,response.content_type,response.status,response.cookies #,text_html.content_type,'text/html'
        