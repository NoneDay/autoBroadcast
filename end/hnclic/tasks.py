import sys, os, zipfile,re, requests,shutil,json,glob,time
sys.path.append(os.path.realpath(os.curdir+"/hello_app/"))
sys.path.append(os.path.realpath(os.curdir+"/hnclic/"))
from hnclic.taskMain import zbTaskApp
import excel2img
import comtypes.client
from hnclic import convert_main as ce,glb

@zbTaskApp.task
def files_template_exec(rptid,config_data,userid,upload_path):
    ce.files_template_exec(rptid,config_data,userid,upload_path,wx_queue=glb.msg_queue)   

@zbTaskApp.task
def zb_execute(rptid,config_data=None,userid=None,report_name=""):
    if config_data is not None:
        return glb.zb_execute(rptid,config_data,userid,report_name)    
    with glb.db_connect() as conn:
            with conn.cursor(as_dict=True) as cursor:
                cursor.execute('SELECT config_txt,worker_no,report_name FROM zhanbao_tbl WHERE id=%(id)d and is_catalog=0 order by xuhao asc', 
                                {"id":rptid}
                            )
                ret=cursor.fetchone()
    if ret is None:
        return "没有这个ID:"+rptid    
    return glb.zb_execute(rptid,json.loads(ret['config_txt']),ret['worker_no'],ret['report_name'])

@zbTaskApp.task
def send_message():
    glb.msg_queue.sendMessage()

@zbTaskApp.task
def load_all_data(config_data,id,args=None,upload_path=None,userid=None):
    return ce.load_all_data(config_data,id=id,args=args,upload_path=upload_path,userid=userid)

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
