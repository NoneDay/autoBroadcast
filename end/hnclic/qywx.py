import json
import requests
import urllib3
import logging
import os
import sys
import getopt

class Qywx():
    '''
    #-----------发送企业微信的消息格式------------
    #图片（image）:1MB，支持JPG,PNG格式
    #语音（voice）：2MB，播放长度不超过60s，支持AMR格式
    #视频（video）：10MB，支持MP4格式
    #普通文件（file）：20MB
    #--------------------------------
    '''
    def __init__(self,corpid='yourid',corpsecret='yoursecret',is_log=True,log_path="qywx.log",log_level=0,redis=None):
        """初始化，需要传入企业ID和密钥，在企业微信的页面上有显示"""
        self.url="https://qyapi.weixin.qq.com"
        self.corpid=corpid
        self.corpsecret=corpsecret
        self.is_log=is_log
        self.log_path=log_path
        self.log_level=log_level
        self.redis=redis
        self._token=None
        if is_log==True:
            LOG_FORMAT = "%(asctime)s - %(levelname)s: %(message)s"
            DATE_FORMAT = "%m/%d/%Y %H:%M:%S %p"
            if log_level==0:
                logging.basicConfig(level=logging.INFO,filename=log_path,format=LOG_FORMAT, datefmt=DATE_FORMAT)
            else:
                logging.basicConfig(level=logging.ERROR,filename=log_path,format=LOG_FORMAT, datefmt=DATE_FORMAT)

    def send_message(self,msg,msgtype,agid,touser="@all"):
        
        if msgtype=="text":
            data=self.msg_messages(msg,agid,msgtype='text',msgid="content",touser=touser)
        elif msgtype=="image":
            media_id=self.get_media_ID(msg,msgtype="image")
            data=self.msg_messages(media_id,agid,msgtype='image',msgid="media_id",touser=touser)
        elif msgtype=="voice":
            media_id=self.get_media_ID(msg,msgtype="voice")
            data=self.msg_messages(media_id,agid,msgtype='voice',msgid="media_id",touser=touser)
        elif msgtype=="video":
            media_id=self.get_media_ID(msg,msgtype="video")
            data=self.msg_messages(media_id,agid,msgtype='video',msgid="media_id",touser=touser)
        elif msgtype=="file":
            media_id=self.get_media_ID(msg,msgtype="file")
            data=self.msg_messages(media_id,agid,msgtype='file',msgid="media_id",touser=touser)
        else:
            raise Exception("msgtype参数错误，参数只能是image或text或voice或video或file")
        
        for cnt in range(2):
            token=self.get_token()
            send_url = '%s/cgi-bin/message/send?access_token=%s' % (self.url,token)
            respone=requests.post(url=send_url, data=data).text
            x = json.loads(respone)
            #42001	access_token已过期	access_token有时效性，需要重新获取一次 errmsg
            if x['errcode'] == 0:
                print ("{} 发送成功".format(msg))
                if self.is_log==True:
                    logging.info("{} 发送成功".format(msg))
                break
            elif x['errcode'] in (42001,40014):
                get_token(reget=True)
                continue
            else:
                print ("{} 发送失败".format(msg))
                if self.is_log==True:
                    logging.info("{} 发送失败".format(msg))
                break

    def send_msg_message(self,msg,agid=1000002,touser="@all"):
        try:
            self.send_message(msg,'text',agid,touser)
        except Exception as e:
            if self.is_log==True:
                logging.error(e)
    def send_image_message(self,path,agid=1000002,touser="@all"):
        if path.lower().endswith("jpg")==False and path.lower().endswith("png")==False:
            raise Exception("图片只能为jpg或png格式")
        if os.path.getsize(path)>1048576:
            raise Exception("图片大小不能超过1MB")
        try:
            self.send_message(path,'image',agid,touser)
        except Exception as e:
            if self.is_log==True:
                logging.error(e)
    def send_voice_message(self,path,agid=1000002,touser="@all"):
        if path.endswith("amr")==False:
            raise Exception("语音文件只能为amr格式，并且不能大于2MB，不能超过60s")
        if os.path.getsize(path)>2097152:
            raise Exception("语音文件大小不能超过2MB，并且不能超过60s，只能为amr格式")
        try:
            self.send_message(path,'voice',agid,touser)
        except Exception as e:
            if self.is_log==True:
                logging.error(e)
    def send_video_message(self,path,agid=1000002,touser="@all"):
        if path.endswith("mp4")==False:
            raise Exception("视频文件只能为mp4格式，并且不能大于10MB")
        if os.path.getsize(path)>10485760:
            raise Exception("视频文件大小不能超过10MB,只能为mp4格式")
        try:
            self.send_message(path,'video',agid,touser)
        except Exception as e:
            if self.is_log==True:
                logging.error(e)
    def send_file_message(self,path,agid=1000002,touser="@all"):
        if os.path.getsize(path)>20971520:
            raise Exception("文件大小不能超过20MB")
        try:
            self.send_message(path,'file',agid,touser)
        except Exception as e:
            if self.is_log==True:
                logging.error(e)

    def get_token(self,reget=False):
        if reget==True:
            if self.redis==None :
                self._token=None
            else:
                self.redis.delete("qywx:token")
        if self.redis is None:
            token=self._token
        else:
            token=self.redis.get("qywx:token")
            if token!=None:
                token=token.decode()
        if token is None or token=="":
            token_url = '%s/cgi-bin/gettoken?corpid=%s&corpsecret=%s' % (self.url, self.corpid, self.corpsecret)
            token = json.loads(requests.get(token_url).text)['access_token']
            if self.redis==None :
                self._token=token
            else:
                self.redis.set("qywx:token",token,ex=7200)
        return token

    def get_media_ID(self,file_path,msgtype="image"):
        """上传资源到企业微信的存储上,msgtype有image,voice,video,file
        备注：上传时图片的名字最好序列化为数字或英文，中文图片的名字不支持图片上传
        """
        for cnt in range(2):
            token=self.get_token()
            media_url = "https://qyapi.weixin.qq.com/cgi-bin/media/upload?access_token={}&type={}".format(token,msgtype)

            #r = requests.post(media_url,files=[('files', ( urllib.parse.quote (os.path.split(file_path)[-1]), open(file_path, 'rb')))])
            #re = json.loads(r.text)

            with open(file_path, 'rb') as f:
                files = {msgtype: f}
                r = requests.post(media_url, files=[('files', ( (os.path.split(file_path)[-1]), f ))])
                re = json.loads(r.text)
                if re["errcode"]==0:
                    return re['media_id']
                elif re["errcode"] in (42001,40014):
                    get_token(reget=True)
                    continue
                else:
                    raise Exception("access_token error")

    def msg_messages(self,msg,agid,msgtype='text',msgid="content",touser='@all'):
        """
        msgtype有text,image,voice,video,file；如果msgytpe为text,msgid为content，如果是其他，msgid为media_id。
        msg为消息的实际内容，如果是文本消息，则为字符串，如果是其他类型，则传递media_id的值。

        """
        values = {
                "touser": touser,
                "msgtype": msgtype,
                "agentid": agid,
                msgtype: {msgid: msg},
                "safe": 0
                }
        msges=(bytes(json.dumps(values), 'utf-8'))
        return msges

    def usage():
        str="""
        ********************调用格式如下**********************
        发送文本消息：
        python qywx.py -t text -m 你要发送的消息
        发送文本消息，指定要发送的应用的ID： 
        python qywx.py -t text -m 你要发送的消息 -a 1000005 
        发送图片消息： 
        python qywx.py -t image -m 图片的全路径 
        发送图片消息，指定要发送的应用的ID： 
        python qywx.py -t image -m 图片的全路径 -a 1000005 
        发送语音消息：
        python qywx.py -t voice -m 语音的路径 
        发送视频消息： 
        python qywx.py -t video -m 视频的路径 
        发送文件消息： 
        python qywx.py -t file -m 文件的路径 
        *********************注意事项***************************
        图片只能是png或jpg图片，大小不能超过1MB
        语音只能是amr格式，播放长度不能超过60s,大小不能超过2MB
        视频只能是mp4格式，大小不能超过10MB 
        普通文件大小不能超过20MB
        ******************************************************** 
        *********************例子*******************************
        python qywx.py -t image -m /root/test.png
        python qywx.py -t text -m 测试消息
        ********************************************************
        """
        print(str)

#from redis import StrictRedis, ConnectionPool        

if __name__=="__main__":
    qywx=Qywx(corpid='ccccccccc',corpsecret='vvvvvvvvvv',is_log=True,log_path='yourpath')
    try:
        options,args = getopt.getopt(sys.argv[1:],"ht:m:a:",["help","type=","message=","agentid="])
    except Except as e:
        print(e)
    a=1000002
    t=None
    m=None
    for name,value in options:
        if name in ("-h","--help"):
            usage()
        elif name in ("-t","--type"):
            t=value
        elif name in ("-m","--message"):
            m=value
        elif name in ("-a","--agentid"):
            a=value
        else:
            usage()
    if t and m:
        if t=="text":
            qywx.send_msg_message(m,agid=a,touser="xxxxxxxxxxx")
        elif t=="image":
            qywx.send_image_message(m,agid=a)
        elif t=="voice":
            qywx.send_voice_message(m,agid=a)
        elif t=="video":
            qywx.send_video_message(m,agid=a)
        elif t=="file":
            qywx.send_file_message(m,agid=a)
        else:
            usage()
#-----------代码中直接调用---------------------
#   qywx=Qywx()  #Qywx(corpid='cccccccccccc',corpsecret='ccccccccccccccccc',is_log=True,log_path='yourpath')
#   qywx.send_msg_message("test")
#   qywx.send_image_message("/root/test.png")F:\vue\avue-cli\dist\img
#   qywx.send_voice_message("/root/test.amr")
#   qywx.send_video_message("/root/test.mp4")
#   qywx.send_file_message("/root/test.mp3")
#   qywx.send_msg_message("test",agid=1000003)
#-----------代码中直接调用---------------------
