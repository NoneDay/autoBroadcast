import datetime
import glob
import json
import os
import re
import shutil
import sys
import time
import zipfile
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

    return reduce(inner_func, [[], ] + ret) ,end_line #将重复的表头后面加上序号
