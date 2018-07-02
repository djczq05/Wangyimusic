from Crypto.Cipher import AES
import requests
import base64
import os
import codecs
import json
from pypinyin import  lazy_pinyin
from urllib.request import urlretrieve
# 后三个参数和i的值（随机的十六位字符串）
b = '010001'
c = '00e0b509f6259df8642dbc35662901477df22677ec152b5ff68ace615bb7b725152b3ab17a876aea8a5aa76d2e417629ec4ee341f56135fccf695280104e0312ecbda92557c93870114af6c9d05c4f7f0c3685b7a46bee255932575cce10b424d813cfe4875d3e82047b97ddef52741d546b8e289dc6935b3ece0462db0a22b8e7'
d = '0CoJUm6Qyw8W8jud'
#随机的十六位字符串
def createSecretKey(size):
	return (''.join(map(lambda xx: (hex(ord(xx))[2:]), str(os.urandom(size)))))[0:16]
#AES加密算法
def AES_encrypt(text, key, iv):
    pad = 16 - len(text) % 16
    if type(text)==type(b''):
        text = str(text, encoding='utf-8')
    text = text + str(pad * chr(pad))
    encryptor = AES.new(key, AES.MODE_CBC, iv)
    encrypt_text = encryptor.encrypt(text)
    encrypt_text = base64.b64encode(encrypt_text)
    return encrypt_text
#得到第一个加密参数
def Getparams(a,SecretKey):
    #0102030405060708是偏移量，固定值
    iv = '0102030405060708'
    h_encText = AES_encrypt(a,d,iv)
    h_encText = AES_encrypt(h_encText,SecretKey,iv)
    return h_encText
#得到第二个加密参数
def GetSecKey(text, pubKey, modulus):
    text = text[::-1]
    rs = int(codecs.encode(text.encode('utf-8'), 'hex_codec'), 16) ** int(pubKey, 16) % int(modulus, 16)
    return format(rs, 'x').zfill(256)
#得到表单的两个参数
def GetFormData(a):
    SecretKey = createSecretKey(16)
    params = Getparams(a,SecretKey)
    enSecKey = GetSecKey(SecretKey,b,c)
    data = {
		"params":str(params,encoding='utf-8'),
		"encSecKey":enSecKey
	}
    return data
def getOnePatam():
    # 查询id的url
    url = 'https://music.163.com/weapi/cloudsearch/get/web?csrf_token='
    #伪装头部
    head = {
        'Host': 'music.163.com',
        'Origin':'https://music.163.com',
        'Referer':'https://music.163.com/search/',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36',
    }
    print("输入你想要下载的歌手")
    song_name = input()
    #第一个参数
    song_name = ''.join(lazy_pinyin(song_name))
    key = '{hlpretag:"",hlposttag:"</span>",s:"'+song_name+'",type:"1",csrf_token:"",limit:"30",total:"true",offset:"0"}'
    FormData = GetFormData(key)
    html = requests.post(url,headers=head,data=FormData)
    result = json.loads(html.text)
    return result['result']['songs']
#下载器：
def download(name,id):
    # 获取歌曲的url的路径
    song_url = "https://music.163.com/weapi/song/enhance/player/url?csrf_token="
    # 伪装头部
    headers = {
        'Host': 'music.163.com',
        'Origin': 'https://music.163.com',
        'Referer': 'https://music.163.com/',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36'
    }
    # 把上个页面查询到的id放到第二个页面的第一个参数上
    a =str({'ids': "["+str(id)+"]", 'br': 320000, 'csrf_token': ""})
    FormData = GetFormData(a)
    response = requests.post(song_url,data = FormData,headers=headers)
    json_dict = json.loads(response.content)
    song_url=json_dict['data'][0]['url']
    print(song_url)
    folder = os.path.exists('songs')
    if not folder:
        os.makedirs('songs')
    path = os.path.join('songs',name+".mp3")
    urlretrieve(song_url,filename=path)
if __name__ == '__main__':
    song_list = getOnePatam()
    for i in song_list:
        name = i['name']
        id = i['id']
        download(name,id)