#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

import configparser
import logging
import os
import requests
import sys
import time
import zmail
from translate import Translator
from requests.packages.urllib3.exceptions import InsecureRequestWarning

from db_help import sqliteDB

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

root_path = os.path.split(os.path.realpath(__file__))[0]

logger = logging.getLogger(__name__)
logger.setLevel(level = logging.INFO)
handler = logging.FileHandler(os.path.join(root_path,"log.txt"))
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
console = logging.StreamHandler()
console.setLevel(logging.INFO)

logger.addHandler(handler)
logger.addHandler(console)


def fanyi(context):
    translator = Translator(to_lang="chinese")
    try:
        zh_context = translator.translate(context)
    except Exception as e:
        logger.info("[-] translator line:{},Error:{}".format(sys.exc_info()[2].tb_lineno,e))
        zh_context = context
    return zh_context

def github_api_search(keyword):
    rl = []
    url = "https://api.github.com/search/repositories?q={}&sort=updated&order=desc".format(keyword)
    logger.info("[+] request {}".format(url))
    headers = {"Content-Type": "application/json","X-GitHub-Media-Type": "github.v3"}
    try:
        rj = requests.get(url,headers=headers,verify=False).json()
        for item in rj["items"][:20]:
            name = item.get("full_name","")
            url = item.get("html_url","")
            updated_at = item.get("updated_at","")
            description = item.get("description","")
            zh_description = fanyi(description)
            
            rl.append([name,url,updated_at,description,zh_description])
    except Exception as e:
        logger.info("[-] line:{},Error:{}".format(sys.exc_info()[2].tb_lineno,e))
    logger.info("[+] get  {}".format(len(rl)))
    return rl

def sendmail(user,passwd,touser,title,rl):
    html_raw = '<html><body><table border="1"><tr><th>名称</th><th>url</th><th>更新时间</th><th>描述</th><th>中文描述</th></tr>{}</table></body></html>'
    td_raw = ''
    for row in rl:
        td_raw += '<tr><td>{}</td><td>{}</td><td>{}</td><td>{}</td><td>{}</td></tr>'.format(row[0],row[1],row[2],row[3],row[4])
    html_raw = html_raw.format(td_raw)
    server = zmail.server(user, passwd)
    mail = {'subject': title,'content_html':html_raw}
    res = server.send_mail(touser,mail)
    if res:
        logger.info("[+] send:{} sussess".format(touser))
    else:
        logger.info("[-] send:{} fail".format(touser))

if __name__ == "__main__":
    dbname = os.path.join(root_path,"github.db")
    create_table = 'CREATE TABLE github (name TEXT NOT NULL,url TEXT NOT NULL,updated_at TEXT NOT NULL,description TEXT NOT NULL, zh_description TEXT NOT NULL);'
    if not os.path.exists(dbname):
        db = sqliteDB(dbname,create_table)
    else:
        db = sqliteDB(dbname)
    cfgpath = os.path.join(root_path, "config.ini")
    conf = configparser.ConfigParser()
    conf.read(cfgpath, encoding="utf-8") 
    for line in  conf.sections():
        items = dict(conf.items(line))
        keyword = items.get("keyword")
        user = items.get("user")
        passwd = items.get("passwd")
        touser = items.get("touser")
        rl = github_api_search(keyword)
        new_rl = []
        for row in rl:
            if db.get("select * from github where url=?",[row[1]]):
                logger.info("[-] {} 已存在".format(row))
                continue
            else:
                new_rl.append(row)
                row = list(map(str,(row)))
                if db.set("INSERT INTO github (name,url,updated_at,description,zh_description) VALUES (?,?,?,?,?)",row):
                    logger.info("[+] 更新{}成功".format(row))
                else:
                    logger.info("[-] 更新{}失败".format(row))
        if new_rl:
            sendmail(user,passwd,touser.split(","),"[*] 监控关键字：{}".format(keyword),new_rl)
        else:
            logger.info("[-] 无新增")
        time.sleep(10)
