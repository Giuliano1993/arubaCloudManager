from ArubaCloud.PyArubaAPI import CloudInterface
from ArubaCloud.objects import SmartVmCreator
from ArubaCloud.objects import ProVmCreator
import argparse
import sys
import os
from dotenv import load_dotenv
load_dotenv()


if __name__ == '__main__':
    password = os.getenv('PASSWORD')
    username = os.getenv('USERNAME')
    if username is None or username == '': sys.exit("missing  username")
    if password is None or password == '': sys.exit("missing  password")
    ci = CloudInterface(dc=1)
    ci.login(username=username, password=password, load=True)
    #print(ci.get_ip_by_vm(ci.get_vm('small01')[0]))
    print(ci.get_vm('small01')[0].ip_addr)


    print(ci.vmlist)