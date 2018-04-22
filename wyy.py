#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/4/22 16:57
import time

from Crypto.Cipher import AES
import base64
import codecs
import requests
import json
import unicodedata as unicode
url = 'https://music.163.com/weapi/v1/resource/comments/R_SO_4_551816010?' \
      'csrf_token='
header = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 '
                  '(KHTML, like Gecko) Chrome/64.0.3282.140 Safari/537.36',
    'Referer': 'http://music.163.com/song?id=551816010',
    'Origin': 'http://music.163.com',
    'Host': 'music.163.com'
}
# 设置代理服务器
proxies = {
            'http:': 'http://121.232.146.184',
            'https:': 'https://144.255.48.197'
        }
# rid 是歌曲的id标志 offset是控制翻页的标志
# first_param = b'{"rid":"", "offset":"0", "total":"true", "limit":"20", "csrf_token":""}'
second_param = '010001'
third_param = '00e0b509f6259df8642dbc35662901477df22677ec152b5ff68ace615bb7b725152b3ab17a876aea8a5aa' \
              '76d2e417629ec4ee341f56135fccf695280104e0312ecbda92557c93870114af6c9d05c4f7f0c3685b7a46bee' \
              '255932575cce10b424d813cfe4875d3e82047b97ddef52741d546b8e289dc6935b3ece0462db0a22b8e7'
forth_param = b'0CoJUm6Qyw8W8jud'
# params 需要第一个和第四个参数 encSecKey需要一个随机的16位字符串和第二个和第三个参数
strw = 'S' * 16

def aesEncrypt(text, key):
    # 偏移量
    iv = b'0102030405060708'
    pad = 16 - len(text) % 16
    # print(type(text))
    tt = pad * chr(pad)
    text = text + tt.encode('utf-8')
    encrpyptor = AES.new(key, AES.MODE_CBC, iv)
    cipher_text = encrpyptor.encrypt(text)
    cipher_text = base64.b64encode(cipher_text)
    return cipher_text


def rsaEncrypt(pubkey, text, mouduls):
    text = text[::-1]
    rs = int(codecs.encode(text.encode('utf-8'), 'hex_codec'), 16) ** int(pubkey, 16) % int(mouduls, 16)
    rs = format(rs, 'x').zfill(256)
    print(rs)
    return rs


def get_params(text):
    if text == 1:
        first_param = b'{"rid":"", "offset":"0", "total":"true", "limit":"20", "csrf_token":""}'
        params = aesEncrypt(first_param, forth_param)
    else:
        offset = str((text-1)*20)
        first_param = b'{"rid":"", "offset":"%b", "total":"false", "limit":"20", "csrf_token":""}' % offset.encode('utf-8')
        params = aesEncrypt(first_param, forth_param)
    # print('params的随机值是: ')
    # print(params)
    params = aesEncrypt(params, strw.encode('utf-8'))
    # print('第二次加密后的随机值是：')
    # print(params)
    return params


def get_rsa(text):
    encseckey = rsaEncrypt(second_param, text, third_param)
    return encseckey


def get_json(url, pm, esk):
    form_data = {
        'params': pm,
        'encSecKey': esk
    }
    json_text = requests.post(url, headers=header, data=form_data).text
    return json_text

# 抓取一首歌的全部评论


def get_all_comment(url):
    # 存放评论
    list_all = []
    # 文件头部
    list_all.append(u'用户ID 用户昵称 用户头像地址 评论时间 点赞总数 评论内容\n')
    params = get_params(1)
    encSecKey = get_rsa(strw)
    json_text = get_json(url, params, encSecKey)
    json_dict = json.loads(json_text)
    # print(json_text)
    comments_num = int(json_dict['total'])
    # print(comments_num)
    if comments_num % 20 == 0:
        page = comments_num / 20
    else:
        page = int(comments_num / 20) + 1
    print("共有%d条评论!" % comments_num)  # 全部评论总数
    print("共有%d页评论!" % page)
    for i in range(page):  # 逐页抓取
        params = get_params(i + 1)
        encSecKey = get_rsa(strw)
        json_text = get_json(url, params, encSecKey)
        json_dict = json.loads(json_text)
        print(json_text)
        for item in json_dict['comments']:
            comment = item['content']  # 评论内容
            nickname = item['user']['nickname']  # 昵称
            userID = item['user']['userId']  # 评论者id
            likedCount = item['likedCount']  # 点赞总数
            comment_info = str(userID) + u" " + nickname + u" " + comment + u" " + str(likedCount) + "\r\n"
            save_to_file(comment_info, u"我们.txt")
        print("第%d页抓取完毕!" % (i + 1))


# 将评论写入文本文件
def save_to_file(list,filename):
        with codecs.open(filename,'a',encoding='utf-8') as f:
            f.writelines(list)
        print("写入文件成功!")


if __name__ == '__main__':
    start_time = time.time() # 开始时间
    get_all_comment(url)
    end_time = time.time()  # 结束时间
    print("程序耗时%f秒." % (end_time - start_time))