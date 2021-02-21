import datetime
import glob
import json
import os
import re
import shutil
import sys
import time
import zipfile
import asyncio
from functools import reduce

import jinja2
import pandas as pd
import requests


def unzip_single(src_file, dest_dir, password=None):
    ''' 解压单个文件到目标文件夹。
    '''
    if password:
        password = password.encode()
    zf = zipfile.ZipFile(src_file)
    try:
        zf.extractall(path=dest_dir, pwd=password)
    except RuntimeError as e:
        print(e)
    zf.close()

def zipDir(dirpath,outFullName):
    """
    压缩指定文件夹
    :param dirpath: 目标文件夹路径
    :param outFullName: 压缩文件保存路径+xxxx.zip
    :return: 无
    """
    zip = zipfile.ZipFile(outFullName,"w",zipfile.ZIP_DEFLATED)
    for path,dirnames,filenames in os.walk(dirpath):
        # 去掉目标跟路径，只对目标文件夹下边的文件及文件夹进行压缩
        fpath = path.replace(dirpath,'')
        for filename in filenames:
            zip.write(os.path.join(path,filename),os.path.join(fpath,filename),zipfile.ZIP_STORED)
    zip.close()

_MAPPING = (u'零', u'一', u'二', u'三', u'四', u'五', u'六', u'七', u'八', u'九', u'十', u'十一', u'十二', u'十三', u'十四', u'十五', u'十六', u'十七',u'十八', u'十九')
_P0 = (u'', u'十', u'百', u'千',)
_S4 = 10 ** 4
def _to_chinese4(num):
    assert (0 <= num and num < _S4)
    if num < 20:
        return _MAPPING[num]
    else:
        lst = []
        while num >= 10:
            lst.append(num % 10)
            num = num / 10
        lst.append(num)
        c = len(lst)  # 位数
        result = u''

        for idx, val in enumerate(lst):
            val = int(val)
            if val != 0:
                result += _P0[idx] + _MAPPING[val]
                if idx < c - 1 and lst[idx + 1] == 0:
                    result += u'零'
        return result[::-1] 

def DataFrame_oneCol_contact(df):
    return '\n'.join([str(x) for x in df.values])

def _whatDayToDate_(d=1,w=0):
    now=datetime.date.today()
    t_date=now-datetime.timedelta(days=now.weekday()-7*w-d+1)
    return t_date.strftime("%Y-%m-%d")

def get_jinja2_Environment():
    env = jinja2.Environment()
    env.globals['time']=time
    env.globals['datetime']=datetime.datetime
    now = datetime.datetime.now()
    #https://stackoverflow.com/questions/904928/python-strftime-date-without-leading-0 取掉额外的0
    env.globals['_今日_']=now.strftime("%#m月%#d日")
    env.globals['_昨日_']=(now+datetime.timedelta(days=-1)).strftime("%#m月%#d日")
    env.globals['_月_']=now.strftime("%#m")
    env.globals['_日_']=now.strftime("%#d")
    env.globals['_时_']=now.strftime("%#H")
    env.globals['_时分_']=now.strftime("%#H时%#M分")

    env.globals['_月0_']=now.strftime("%m")
    env.globals['_日0_']=now.strftime("%d")

    env.globals['_年_']=now.strftime("%Y")
    env.globals['_上年_']=str(int(now.strftime("%Y"))-1)

    env.globals['_今天_']=(now).strftime("%Y-%m-%d")
    env.globals['_昨天_']=(now-datetime.timedelta(days=1)).strftime("%Y-%m-%d")
    env.globals['_whatDayToDate_']=_whatDayToDate_


    env.filters['num2cn'] = _to_chinese4
    env.filters['dflj'] = DataFrame_oneCol_contact
    #env.globals.update(int=int)
    return env

_num_pattern = re.compile(r'^[-+]?[-0-9]\d*\.\d*|[-+]?\.?[0-9]\d*$')
def is_number(x):
    if x is None:
        return False
    if (isinstance(x,float) or isinstance(x,int) ):
        return True    
    match=_num_pattern.match(x)
    return match!=None and match.regs[0][1]==len(x)

def guess_col_names(all_lines,rule_str=None,end_line=None):
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
        raise RuntimeError('没有正确取到数据，请检查设置，重新查询')
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
    ret=reduce(inner_func, [[], ] + ret) #将重复的表头后面加上序号
    return list(map(lambda x:re.sub(r"[\s|'|\"|（|）]+","",x),ret))  ,end_line  #去除特殊字符

__special_characters_replacements={
    "“":"\"",
    "”":"\"",
    "‘":"'",
    "’":"'",
    ",":","
}
def exec_template(env,template_string,real_dict):
    if template_string.find("{{") <0:
        return template_string
    if env is None:
        env = get_jinja2_Environment()
    template_string="".join(__special_characters_replacements.get(char, char) for char in template_string)

    template = env.from_string(template_string)
    result=template.render(real_dict)
    result_lines=result.split("\n")
    if(len(result_lines)==1):
        return result    
    for one_line in result_lines:#展开模板计算结果
        one_line_split=one_line.split()
        if len(one_line_split)==2 and is_number(one_line_split[0]) and result_lines[-1].startswith("Name:") and result_lines[-1].find("dtype:")>1:
            real_value=[] #is_pd_serials
            for one_line in result_lines[:-1]:#展开模板计算结果  
                real_value.append(one_line.split()[1])
            return "\n".join(real_value)
        elif len(one_line_split)>2 and len(result_lines[1].split())>len(result_lines[0].split()) : #is_pd_frame  {{ds}} 第一行没有idx 列，要加上 
            return "序号\t"+result
        break
    return result

def htmltableToArray(select_result):
    idex_t=[] #存储每行的展开合并单元格的数据
    lines=len(select_result)
    idex_t=[[]]*lines
    for i_tr, tr in enumerate(select_result):
        lj_col=0
        for td in tr.xpath("th|td"):
            if re.search("display\s*:\s*none", td.attrib.get("style",''), re.IGNORECASE):
                continue
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

# config_data_form_input config 中的总体参数    
# 参数 user_input_form_data 是为了转json的raw 调用时，输入的参数
def get_real_form_data(data_from,config_data_form_input,user_input_form_data):
    url=data_from['url']
    url=exec_template(None,url,[])
    args={}
    #设置取数form参数，先用用户传过来的参数覆盖总体的参数，在用总体参数覆盖具体报表的参数
    args=config_data_form_input
    #设置取数form参数，先用用户传过来的参数覆盖总体的参数，在用总体参数覆盖具体报表的参数
    if user_input_form_data is None:
        user_input_form_data={}
    args={ x['name']: user_input_form_data.get(x['name'],x['value']) for x in config_data_form_input }
    real_args=dict()
    for x in data_from['form_input']:
        if x['value']=='默认值' and args.get(x['name'],'默认值')!='默认值':
            real_args[x['name']]=args[x['name']]
        else:
            if isinstance(x['value'],str) and x['value'].startswith("{{") and x['value'].endswith("}}"):
                real_args[x['name']]=exec_template(None,x['value'],[])
            else:
                real_args[x['name']]=x['value']
    #将默认值参数去掉
    real_form_data=None if real_args is None else {k:v for (k,v) in real_args.items() if v!='默认值'}                
    return url,real_form_data


import uuid
import math
async def acquire_lock_with_timeout(conn,lock_name, acquire_timeout=3, lock_timeout=10):
    """
    基于 Redis 实现的分布式锁
    
    :param conn: Redis 连接
    :param lock_name: 锁的名称
    :param acquire_timeout: 获取锁的超时时间，默认 3 秒
    :param lock_timeout: 锁的超时时间，默认 2 秒
    :return:
    """
    
    identifier = str(uuid.uuid4())
    lockname = f'lock:{lock_name}'
    lock_timeout = int(math.ceil(lock_timeout))

    end = time.time() + acquire_timeout

    while time.time() < end:
        # 如果不存在这个锁则加锁并设置过期时间，避免死锁
        if conn.set(lockname, identifier, ex=lock_timeout, nx=True):
            return identifier
        await asyncio.sleep(0.001)

    return False


def release_lock(conn,lock_name, identifier):
    """
    释放锁
    
    :param conn: Redis 连接
    :param lockname: 锁的名称
    :param identifier: 锁的标识
    :return:
    """
    unlock_script = """
    if redis.call("get",KEYS[1]) == ARGV[1] then
        return redis.call("del",KEYS[1])
    else
        return 0
    end
    """
    lockname = f'lock:{lock_name}'
    unlock = conn.register_script(unlock_script)
    result = unlock(keys=[lockname], args=[identifier])
    if result:
        return True
    else:
        return False

# -*- coding: utf-8 -*-
'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
#作者：cacho_37967865
#博客：https://blog.csdn.net/sinat_37967865
#文件：encryption.py
#日期：2019-07-31
#备注：多种加解密方法    # pip install pycryptodome
用pyCryptodome模块带的aes先将秘钥以及要加密的文本填充为16位   AES key must be either 16, 24, or 32 bytes long
'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
import base64
from Crypto.Cipher import AES
 
 
#  bytes不是32的倍数那就补足为32的倍数
def __add_to_32(value):
    while len(value) % 32 != 0:
            value += b'\x00'
    return value     # 返回bytes
 
 
# str转换为bytes超过32位时处理
def __cut_value(org_str):
    org_bytes = str.encode(org_str)
    n = int(len(org_bytes) / 32)
    i = 0
    new_bytes = b''
    while n >= 1:
        i = i + 1
        new_byte = org_bytes[(i-1)*32:32*i-1]
        new_bytes += new_byte
        n = n - 1
    if len(org_bytes) % 32 == 0:                   # 如果是32的倍数，直接取值
        all_bytes = org_bytes
    elif len(org_bytes) % 32 != 0 and n>1:         # 如果不是32的倍数，每次截取32位相加，最后再加剩下的并补齐32位
        all_bytes = new_bytes + __add_to_32 (org_bytes[i*32:])
    else:
        all_bytes = __add_to_32 (org_bytes)          # 如果不是32的倍数，并且小于32位直接补齐
    return all_bytes
 
 
def AES_encrypt(org_str,key):
    # 初始化加密器
    aes = AES.new(__cut_value(key), AES.MODE_ECB)
    #先进行aes加密
    encrypt_aes = aes.encrypt(__cut_value(org_str))
    # 用base64转成字符串形式
    encrypted_text = str(base64.encodebytes(encrypt_aes), encoding='utf-8')  # 执行加密并转码返回bytes
    return(encrypted_text)
 
 
def AES_decrypt(secret_str,key):
    # 初始化加密器
    aes = AES.new(__cut_value(key), AES.MODE_ECB)
    # 优先逆向解密base64成bytes
    base64_decrypted = base64.decodebytes(secret_str.encode(encoding='utf-8'))
    # 执行解密密并转码返回str
    decrypted_text = str(aes.decrypt(base64_decrypted), encoding='utf-8').replace('\0', '')
    return decrypted_text
 
 
if __name__ == '__main__':
    org_str = 'http://mp.weixin.qq.com/s?__biz=MjM5NjAxOTU4MA==&amp;mid=3009217590&amp;idx=1&amp;sn=14532c49bc8cb0817544181a10e9309f&amp;chksm=90460825a7318133e7905c02e708d5222abfea930e61b4216f15b7504e39734bcd41cfb0a26d&amp;scene=27#wechat_redirect'
    # 秘钥
    key = '123abc'
    secret_str = AES_encrypt(org_str,key)
    print(AES_decrypt(secret_str,key))

