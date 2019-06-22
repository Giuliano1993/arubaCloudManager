#!/usr/bin/python
import argparse, sys, os, json
from dotenv import load_dotenv
from pprint import pprint
from src.arubaCloudManager import arubaCloudManager

load_dotenv()
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    
    parser.add_argument('-t', '--template', help="the name of the template to search", action="store", type=int, dest="template")
    parser.add_argument('-s', '--searchTemplate', help="the name of the template to search", action="store", type=str, dest="search")
    parser.add_argument('--type', help="type of server to instantiate", action="store", choices=['pro','smart'], type=str, dest="type")
    parser.add_argument('-a', '--action', help="choose an action to perform", choices=['templateList','new','list','info'], nargs="?", action="store",default="list",dest="action")
    parser.add_argument('-d', '--details', help="get more details on the machines", action="store_true")
    parser.add_argument('-c', '--config', help="get a config file", type=argparse.FileType('r'), action="store", dest="config")
    parser.add_argument('-j', '--json', help="set list output as json", action="store_true")
    parser.add_argument('-i', '--installer', help="installer to put on server and execute", type=argparse.FileType('r'), action="store", dest="installer")
    parser.add_argument('-S', '--silent', help="output only the result", action="store_true")

    p = parser.parse_args()
    password = os.getenv('PASSWORD')
    username = os.getenv('USERNAME')

    

    acm = arubaCloudManager(username, password)
    if p.config is not None:
        silent = True if p.silent is not None and p.silent == True else False
        if p.installer is not None:
            acm.importConfig(p.config, p.installer,silent)
        else:
            acm.importConfig(p.config, None,silent)
        exit() 
    if p.action == 'new':
        acm.createVM(p)
    elif p.action == 'templateList':
        acm.getTemplateList(p.search)
    elif p.action == 'list':
        acm.getVmList(p.details)
    elif p.action == 'info':
        acm.getInfo(p.details)
    else:
        print("you should select an action with -a and ['templateList','new','list','info']")