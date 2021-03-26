import sys, os, zipfile,re, requests,shutil,json,glob,time
sys.path.append(os.path.realpath(os.curdir+"/hello_app/"))
sys.path.append(os.path.realpath(os.curdir+"/hnclic/"))
from hnclic.taskMain import zbTaskApp
import excel2img
import comtypes.client
from hnclic import convert_main as ce,glb
import pandas as pd
import asyncio
@zbTaskApp.task
def files_template_exec(rptid,config_data,userid,upload_path):
    try:
        return asyncio.run(
            ce.files_template_exec(rptid,config_data,userid,upload_path,wx_queue=glb.msg_queue)   
        )
    except Exception as e:
        return str(e.args),None,None,config_data 

@zbTaskApp.task(bind=True,max_retries=3)
def zb_execute(self,rptid,config_data=None,userid=None,report_name=""):
    if config_data is None or userid is None:
        with glb.db_connect() as conn:
                with conn.cursor(as_dict=True) as cursor:
                    cursor.execute('SELECT config_txt,worker_no,report_name FROM zhanbao_tbl WHERE id=%(id)d and is_catalog=0 order by xuhao asc', 
                                    {"id":rptid}
                                )
                    ret=cursor.fetchone()
        if ret is None:
            return "没有这个ID:"+rptid    
        config_data=json.loads(ret['config_txt'])
        userid=ret['worker_no']
        report_name=ret['report_name']
    try:
        glb.redis.sadd("zb:executing",rptid)    
        return  asyncio.run(ce.files_template_exec(rptid,config_data,userid,glb.config['UPLOAD_FOLDER'],wx_queue=glb.msg_queue))  
    except Exception as e:
        if self.request.retries>=3:
            glb.msg_queue.put({'type':'sendMessage',"wxid":'qywx:'+userid,"content":f"{rptid}：{report_name},执行报错。错误信息："+ str(e.args)})
        print(f"{rptid}：{report_name},执行报错。错误信息："+ str(e))
        raise self.retry(exc=e, countdown=5)
    finally:
        glb.redis.srem("zb:executing",rptid)

@zbTaskApp.task
def send_message():
    glb.msg_queue.sendMessage()

@zbTaskApp.task
def load_all_data(config_data,id,user_input_form_data=None,upload_path=None,userid=None):
    try:
        ds_dict=asyncio.run(
                ce.load_all_data(config_data,id=id,user_input_form_data=user_input_form_data,upload_path=upload_path,userid=userid)
                        )
        df_arr=[]
        ret={}
        for k,v in ds_dict.items():
            if isinstance(v,pd.DataFrame):
                ret[k]=v.to_json(orient='split',force_ascii=False) #
                df_arr.append(k)
            elif k[:2]!='__':
                ret[k]=v
        return df_arr,ret,config_data
    except Exception as e:
        print(e.__traceback__)
        return str(e.args),None,config_data

@zbTaskApp.task
def initDatafrom(data_from,report_id,userid):
    try:
        upload_path=glb.user_report_upload_path(report_id )   
        if data_from['type']=="file":
            filename=os.path.join(upload_path, data_from['url'])
            ret=ce.load_from_file(filename,[])
            data_from={**data_from,**ret['修改这里']['data_from']}
        elif data_from['url'].startswith("结果://"):
            ret=ce.get_excel_data(data_from,report_id,upload_path,ds_dict={},ret={})
        else:
            ret= asyncio.run( ce.load_from_url2(data_from,{},0,userid) )
        ds_dict={}
        for k,v in ret.items():
            if isinstance(v['data'],pd.DataFrame):
                ds_dict[k]=v['data'].to_json(orient='split',force_ascii=False) #

        return [ x for x in ds_dict ],ds_dict,data_from
    except Exception as e:
        return str(e.args),None,data_from

@zbTaskApp.task
def cut_image_xlsx(fn_excel, fn_image, page=None, _range=None):
    excel2img.export_img(fn_excel, fn_image, page=None, _range=None)

@zbTaskApp.task
def ppt2png(pptFileName):
    comtypes.CoInitialize()
    powerpoint = comtypes.client.CreateObject("Powerpoint.Application")
    powerpoint.Visible = True
    outputFileName = pptFileName[0:-5] + ".pdf"
    ppt = powerpoint.Presentations.Open(pptFileName)
    #保存为图片
    ppt.SaveAs(pptFileName[0:-5] + '.jpg', 17)
    #保存为pdf
    #ppt.SaveAs(outputFileName, 32) # formatType = 32 for ppt to pdf
    # 关闭打开的ppt文件
    ppt.Close()
    # 关闭powerpoint软件
    powerpoint.Quit()
