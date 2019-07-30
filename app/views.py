"""
Routes and views for the flask application.
"""
# -*- coding: utf-8 -*-
import os
import requests
from config import Config
from urllib import parse
from flask import Flask, render_template, redirect, url_for, send_from_directory,request
from flask_graphql import GraphQLView
from .data.base import db_session
from .data.schema import schema
from app import create_app as app

from flask_cors import CORS
from .services.spider import Spider
import threading, time
from .utils.operate_oss import OSS
from .utils.operate_db import DBUtil

CORS(app, supports_credentials=True, origins="https://www.kuaijiajin.club")


@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()


app.add_url_rule('/graphql', view_func=GraphQLView.as_view('graphql', schema=schema, graphiql = True, context={'session': db_session}))

@app.route('/')
def index():

    return app.send_static_file('index.html')

@app.route('/login/<key>', methods=["GET", "POST"])
def login(key):
    """
    OSS 删除匹配key的所有文件
    """
    if key is None:
        return 'fail'

    print(key)

    if key == 'github':
        print(request.args.get('code'))
        parar={'client_id': Config.GITHUB_CLIENT_ID, 'client_secret': Config.GITHUB_CLIENT_SECRET, 'code': request.args.get('code')}
        headers={
            'Accept':'application/json'
        }
        r = requests.post('https://github.com/login/oauth/access_token',params = parar, headers=headers)
        print(r.text)
        access_token = r.json()
        print(access_token)
        userInfo = requests.get('https://api.github.com/user?access_token=' + access_token['access_token'])
        return userInfo.text

    return 'success'

@app.route('/missionStart/<key>')
def missionStart(key):
    if key is None:
        key = 1
    i = 0
    while(i < 30):
        i += 1
        t = threading.Thread(target=Spider(siteId=key).run, name='spiderMission %s' % i)
        t.start()
    si = threading.Thread(target=Spider(siteId=key).insert, name='insertMission %s' % i)
    sc = threading.Thread(target=Spider(siteId=key).timerStart, name='checkFinish')
    si.start()
    sc.start()

    return 'Mission Start ... '


@app.route('/uploadAll')
def uploadAll():
    '''
    一键上传图片到OSS
    '''
    OSS().upload_all_image()
    return 'success'
@app.route('/getIPList')
def getIPList():
    '''
    获取ip所属地区
    '''
    path = 'D:/DingTalk/ipList.txt'
    res = ''
    with open(path,'r') as f:
        content = f.read()
        ipList = content.split(';')
        for ip in ipList:
            if ip is '':
                continue
            else:
                res += getIPLocation(ip) + ';'
        return res

    return 'fail'

def getIPLocation(ip):
    parar={'query': ip, 'resource_id': '6006', 'ie': 'utf8', 'format':'json'}
    headers={
        'Accept':'application/json'
    }
    r = requests.get('https://sp0.baidu.com/8aQDcjqpAAV3otqbppnN2DJv/api.php',params = parar, headers=headers)
    response_str = r.json()
    data = response_str['data']
    location = '出错了：'
    if response_str['status'] == '0':
        item = data[0]
        location = item['location']
    else:
        location += ip
    return location

@app.route('/delete/<key>')
def delete(key):
    """
    OSS 删除匹配key的所有文件
    """
    if key is None:
        return 'fail'
    OSS().delete_object(key)
    return 'success'


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')

@app.route('/robots.txt')
def robots():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'robots.txt')

@app.route('/test')
def test():
    db_util = DBUtil()
    db_util.resort_chapters()

    return 'testing ...'