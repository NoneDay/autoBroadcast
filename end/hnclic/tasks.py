import sys, os, zipfile,re, requests,shutil,json,glob,time
sys.path.append(os.path.realpath(os.curdir+"/hello_app/"))
sys.path.append(os.path.realpath(os.curdir+"/hnclic/"))
from hnclic.taskMain import zbTaskApp
import excel2img
import comtypes.client
from hnclic import convert_main as ce,glb
@zbTaskApp.task
def add(x, y):
    time.sleep(1)
    return x + y

@zbTaskApp.task
def zb_execute(rptid,config_data,userid,upload_path):
    ce.files_template_exec(rptid,config_data,userid,upload_path,wx_queue=glb.msg_queue)   

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

@zbTaskApp.task
def sendMessage():
    glb.msg_queue.sendMessage()
    #requests.post(f"http://localhost:10001/{res['type']}",data=res['data'].encode('utf-8','surrogatepass'))
    
@zbTaskApp.task
def send_yzl(id):
    pass

