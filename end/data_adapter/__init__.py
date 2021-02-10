import sys, os,re
from hnclic.utils import AES_decrypt,AES_encrypt
module_dict={}
login_getData_template_arr=[ {
            'name':"帆软",
            'type': "帆软",
            'patterns':["http://demo.finereport.com/decision/"],
            "allow_userid":".*",
            'login_data_template':'{"username":"{{username}}","password":"{{password}}","validity":-1,"sliderToken":"","origin":"","encrypted":false}',
            'login_data_type':"json",
            'login_url':"http://demo.finereport.com/decision/login",
            "proxy":"http://10.20.112.145:8080",
            "headers":"""
            {"Accept": "application/json, text/javascript, */*; q=0.01"
                ,"Content-Type": "application/json"
                ,"Cookie": "fine_remember_login=-1"
                ,"X-Requested-With": "XMLHttpRequest"
            }
            """,
            "login_success":"",
            "login_error":'errorCode',
            'next_headers':'{"Authorization": "Bearer {{login_data["data"]["accessToken"]}}"}',
            "next_cookies":'{"fine_remember_login":-1,"fine_auth_token":"{{login_data["data"]["accessToken"]}}" }',
        },{
            'name':"河南个险331",
            'type': "河南",
            'patterns':["http://report.hn.clic/report3/zdjy.aspx"],
            "allow_userid":"^141.+",
            'login_data_template':'{"emp.empNo":"{{username}}","emp.empPassword":"{{password}}"}',
            'login_data_type':"form",#form
            'login_url':"http://report.hn.clic/gxzc_331/home/login",
            "headers":"""{ }""",
            "login_success":'',
            "login_error":'用户名或密码错误',
            'next_cookies':'{}',
            "next_headers":'{"needType":"json","worker_no":"{{username}}" }',
        },{
            'name':"河南通用",
            'type': "河南",
            'patterns':["http://"],
            "allow_userid":"^141.+",
            'login_data_template':'{}',
            'login_data_type':"json",#form
            'login_url':"",
            "headers":"""{}""",
            "login_success":'',
            "login_error":'',
            'next_cookies':'{}',
            "next_headers":'{"needType":"json","worker_no":"{{userid}}" }',
        }]
user_login_dict={
    "帆软":{'name':"帆软","username":"6RvkuDjf91tjjoW/iShfiiLLqkLwp9Tsa+dgmxTFz4I=\n","password":'fIFXFs1aT73Oxu36OXe8jyLLqkLwp9Tsa+dgmxTFz4I=\n'},
    "河南个险331":{'name':"河南个险331","username":"ioqPGAO/hcrxfqLs8KjevS0boOeE/xEdcIvWH4zN2eA=\n","password":"aL/pRbAz5aq6doYJbh0Imy0boOeE/xEdcIvWH4zN2eA=\n"},
}

login_getData_template_dict=dict()
for x in login_getData_template_arr:
    login_getData_template_dict[x['name']]=x

def get(data_from,userid):
    if data_from['type'] in ["html",'json'] and (data_from['ds'] is None or len(data_from['ds'])==0):
        match_arry=[]
        url=data_from['url']
        for v in login_getData_template_arr:
            if re.search(v['allow_userid'],userid):
                for one_rule in v['patterns']:
                    if url.startswith(one_rule):
                        match_arry.append((v["name"],v,one_rule))
                        break
        if len(match_arry)==0:
            raise RuntimeError(f"你的工号不能查询这个网址！")
        else:
            data_from['type']=match_arry[0][0]

    if data_from['type'] in ["html",'json']:
        template_id="河南通用"
    else:
        template_id=data_from['type']
    
    login_getData_template=login_getData_template_dict.get(template_id)
    if login_getData_template is None:
        raise RuntimeError(f"没有实现类型<{module_name}>！")
    module_name=login_getData_template['type']
    module=module_dict.get(module_name)
    if module is None:
        module=__import__(module_name)
        module_dict[module_name]=module

    if module is None:
        raise RuntimeError(f"没有实现类型<{module_name}>！")
    user_login=user_login_dict.get(template_id,{})
    user_login_decrypt=dict()
    for k,v in user_login.items():
        user_login_decrypt[k]=AES_decrypt(v,login_getData_template['name'])

    ret = module.MyDataInterface(data_from,userid,login_getData_template, user_login_decrypt)
    return ret
    
