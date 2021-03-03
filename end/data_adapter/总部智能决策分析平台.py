from Crypto import Random
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5
import base64

from aip import AipOcr

""" 你的 APPID AK SK """
APP_ID = '23701408'
API_KEY = '57Gf97vfebGSjGq1WQmQ6s7g'
SECRET_KEY = 't1zfM5ykEu79kO18Bn6YOwMCDDVZk87R'

client = AipOcr(APP_ID, API_KEY, SECRET_KEY)
""" 读取图片 """
def get_file_content(filePath):
    with open(filePath, 'rb') as fp:
        return fp.read()

image = get_file_content('./data_adapter/test2.jpg')

""" 调用通用文字识别, 图片参数为本地图片 """
aaa=client.basicGeneral(image)

""" 如果有可选参数 """
options = {}
options["language_type"] = "ENG"

""" 带参数调用通用文字识别, 图片参数为本地图片 """
client.basicGeneral(image, options)

url = "https//www.x.com/sample.jpg"

""" 调用通用文字识别, 图片参数为远程url图片 """
client.basicGeneralUrl(url)

""" 如果有可选参数 """
options = {}
options["language_type"] = "CHN_ENG"
options["detect_direction"] = "true"
options["detect_language"] = "true"
options["probability"] = "true"

""" 带参数调用通用文字识别, 图片参数为远程url图片 """
client.basicGeneralUrl(url, options)



# 公钥加密
def rsa_encode(message, public_key):
    rsakey = RSA.importKey(public_key)  # 导入读取到的公钥
    cipher = PKCS1_v1_5.new(rsakey)  # 生成对象
    # 通过生成的对象加密message明文，注意，在python3中加密的数据必须是bytes类型的数据，不能是str类型的数据
    cipher_text = base64.b64encode(
        cipher.encrypt(message.encode(encoding="utf-8")))
    # 公钥每次加密的结果不一样跟对数据的padding（填充）有关
    return cipher_text.decode()
def bytesToHexString(content):
    hexCodes=[]
    for one in content:
        hexCodes.append(str(hex(ord(one)))[2:])
    return "".join(hexCodes)

public_key = """-----BEGIN PUBLIC KEY-----
"MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQCwjDm1HXDw8QH5ZtGMQIl2h/I8E+chOQA8aQ8xCR/+aHnROaN/ZU5Vmd2Zz7g6cAacR9BSm60+iSCYtvEGJKl0WqvbPGJkc8tedjNF1QqgWqkkuE6Udgw2OkEKJCxDg6PrAniR7Cc0io9G8bW4P8JDJjSbbafvMPDDFbVVUWJxxwIDAQAB
-----END PUBLIC KEY-----"""
a= rsa_encode("14101533",public_key)
print(a)
b=bytesToHexString("oFJNdCrY9uoC+++R5/6RFi1sc3TPwOD3IYpaePxN19Yn+7aExqADmM/MfDXAipdNpeBTuWK1G0L6k2/xLritWslk57WgLGc0DmfTBQnNLgUKySi4c5XkzTgLMg95cd43I8egosXbYru4h47kwQxINqE+fcXxvkdOpZxz9aNQ6cE=")
if b=="6f464a4e6443725939756f432b2b2b52352f36524669317363335450774f4433495970616550784e3139596e2b376145787141446d4d2f4d664458416970644e7065425475574b3147304c366b322f784c72697457736c6b353757674c476330446d665442516e4e4c67554b795369346335586b7a54674c4d67393563643433493865676f735862597275346834376b775178494e71452b66635878766b644f705a787a39614e513663453d":
    print(b)
else:
    print("b")