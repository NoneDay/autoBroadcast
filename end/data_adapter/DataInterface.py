import json,yaml
import asyncio,aiohttp
from hnclic.utils import htmltableToArray,exec_template,get_real_form_data,AES_decrypt,AES_encrypt
class DataInterface():
    def __init__(self,data_from,userid,login_getData_template,user_password):
        self.data_from=data_from
        self.userid=userid
        self.login_getData_template=login_getData_template
        self.user_password=user_password
        self.proxy=login_getData_template.get("proxy")
        self.login_data=dict()
        
    
    async def _login(self):
        cookies={}
        login_headers={}
        next_headers={}
        if self.login_getData_template['login_url']!='':
            form_data=self.login_getData_template['login_data_template']                
            if form_data:                    
                form_data=exec_template(None,form_data,self.user_password)
                if self.login_getData_template['login_data_type']=="json":
                    login_headers={'Content-Type': 'application/json'}                        
                else:
                    login_headers={'Content-Type':'application/x-www-form-urlencoded; charset=UTF-8'}
                    form_data=json.loads(form_data)
                login_headers={**json.loads(self.login_getData_template['headers']),**login_headers}
                        
                async with self.session.post(self.login_getData_template['login_url'],data=form_data,
                                            proxy=self.proxy,headers=login_headers ) as login_response:
                    self.login_data=await login_response.text()
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
                    cookies=login_response.cookies
            else:
                raise RuntimeError("模板定义了登陆url，但没有定义form_data")
        else:
            self.login_data={}
        return cookies,login_headers,next_headers

    async def login_check(self):
        async with aiohttp.ClientSession() as self.session:
            cookies,login_headers,next_headers=await self._login()
        
    async def load_data_from_url(self,config_data_form_input,user_input_form_data):
        async with aiohttp.ClientSession() as self.session:
            cookies,login_headers,next_headers=await self._login()
            temp_dict={**{"login_data":self.login_data,"userid":self.userid},**self.user_password}
            next_headers=json.loads(exec_template(None,self.login_getData_template['next_headers'],temp_dict))
            next_cookies=json.loads(exec_template(None,self.login_getData_template['next_cookies'], temp_dict))
            self.next_cookies={**cookies,**next_cookies}
            self.next_headers={**login_headers,**next_headers}

            data_from=self.data_from
            url,real_form_data=get_real_form_data(data_from,config_data_form_input,user_input_form_data)
            self.data,form_inputs=await self.getData(url,real_form_data)

        if data_from['ds'] is None or len(data_from['ds'])==0:
            data_from['ds']=[{"t": "json","pattern": 'no',"end":10000,
                        "start": 1,"columns": "auto","view_columns": "","sort": "","name": "修改这里",
                        "old_columns": self.data[0]}]
            data_from['form_input']=[{'name':k,'value':v} for (k,v) in form_inputs.items()]

    def load_data_for_p(self,p):
        start=int(p['start'])
        end=1000000 if not p['end'] else( int(p['start'])+int(p['end']) if isinstance(p['end'],str) and p['end'][0]=='+' else int(p['end']))
        return "TableModel",self.data[0],self.data[start:end],None
    
    async def getData(self,url,input_params={}):
        # 可以自己写成远程调用
        # 所有参数已经经过了模板替换，直接使用就可以
        # start_time=time.time()
        # async with self.session.get(url,cookies=self.next_cookies,headers=self.next_headers) if (input_params is None or len(input_params) ==0) \
        #        else self.session.post(url,data=input_params,cookies=self.next_cookies,headers=self.next_headers) as response:
        #    text=await response.text()
        #    print(f'{url}取数用时： {time.time()-start_time}')
        #    return text,response.content_type,response.status #,text_html.content_type,'text/html'
        raise RuntimeError("没有实现get_ata")