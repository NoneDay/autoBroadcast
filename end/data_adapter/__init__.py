import sys, os,re,glob
from hnclic.utils import AES_decrypt,AES_encrypt
from hnclic import glb
module_dict={}

user_login_dict={
    "帆软":{'name':"帆软","username":"6RvkuDjf91tjjoW/iShfiiLLqkLwp9Tsa+dgmxTFz4I=\n","password":'fIFXFs1aT73Oxu36OXe8jyLLqkLwp9Tsa+dgmxTFz4I=\n'},
    "河南个险331":{'name':"河南个险331","username":"ioqPGAO/hcrxfqLs8KjevS0boOeE/xEdcIvWH4zN2eA=\n","password":"aL/pRbAz5aq6doYJbh0Imy0boOeE/xEdcIvWH4zN2eA=\n"},
}



def get(data_from,userid,user_login=None):
    #if data_from['type'] in ["html",'json'] and (data_from['ds'] is None or len(data_from['ds'])==0):
    #    match_arry=[]
    #    url=data_from['url']
    #    for k,v in glb.login_getData_template_dict.items():
    #        if re.search(v['allow_userid'],userid):
    #            for one_rule in v['patterns']:
    #                if url.startswith(one_rule):
    #                    match_arry.append((v["name"],v,one_rule))
    #                    break
    #    if len(match_arry)==0:
    #        raise RuntimeError(f"你的工号不能查询这个网址！")
    #    else:
    #        match_arry=sorted(match_arry,key=lambda x:-len(x[2])) #按匹配最长的URL被选中
    #        data_from['type']=match_arry[0][0]

    if data_from['type'] in ["html",'json'] and userid[1:3]=="41":
        sys_name="河南通用"
    else:
        sys_name=data_from['type']
    #
    login_getData_template= glb.getSysRegister(sys_name)
    if login_getData_template is None:
        raise RuntimeError(f"没有实现类型<{module_name}>！")
    module_name=login_getData_template['type']
    module=module_dict.get(module_name)
    if module is None:
        module=__import__(module_name)
        module_dict[module_name]=module

    if module is None:
        raise RuntimeError(f"没有实现类型<{module_name}>！")
    if user_login is None:
        with glb.db_connect() as conn:
            with conn.cursor(as_dict=True) as cursor:
                cursor.execute('SELECT * FROM login_tbl WHERE sys_name=%(sys_name)s and worker_no=%(worker_no)s', {"sys_name":sys_name,"worker_no":userid})
                user_login=cursor.fetchone()
    #user_login=user_login_dict.get(sys_name,{})
    #user_login_decrypt=dict()
    #for k,v in user_login.items():
    #    user_login_decrypt[k]=AES_decrypt(v,login_getData_template['name'])

    ret = module.MyDataInterface(data_from,userid,login_getData_template, user_login if user_login is not None else {})
    return ret
    
