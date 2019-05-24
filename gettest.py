from ArubaCloud.PyArubaAPI import CloudInterface
from ArubaCloud.objects import SmartVmCreator
from ArubaCloud.objects import ProVmCreator
import argparse
import sys
import os
import time
import json
from pprint import pprint
import paramiko
import pysftp
from dotenv import load_dotenv
load_dotenv()


if __name__ == '__main__':


    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--installer', help="installer to put on server and execute", type=argparse.FileType('r'), action="store", dest="installer")
    p = parser.parse_args()


    password = os.getenv('PASSWORD')
    username = os.getenv('USERNAME')
    if username is None or username == '': sys.exit("missing  username")
    if password is None or password == '': sys.exit("missing  password")
    ci = CloudInterface(dc=1)
    ci.login(username=username, password=password, load=True)
    #print(ci.get_ip_by_vm(ci.get_vm('small01')[0]))


    data = {
        "serverType":"smart",
        "os":"Ubuntu Server 16",
        "rootPassword":"mySecurePassword",
        "takeSnapshot":True,
        "machineName":"newMachineRevenge",
        "packageSize":"small",
        "cpuQty":1,
        "ramQty":1,
        "hdSize":5,
        "execOnServer":[
            "apt-get update",
            "apt-get install -y apache2",
            "apt-get install -y php libapache2-mod-php",
            "systemctl restart apache2"
        ]
    }


    machineName = 'newMachine'
    machinePassword = data['rootPassword']


    #ci.create_snapshot(dc=1,server_id='439396')
    vm = ci.get_vm(machineName)[0]
    assignedIp = vm.ip_addr
    
    datas = {
        'ip':assignedIp,
        'user':'root',
        'password':'MyStrongPassword'
    }

    status = 0
    while status != 3:
        print('.')
        vm = ci.get_vm(machineName)[0]
        status = vm.status
        if status == 3 and 'execOnServer' in data:
            ssh = paramiko.SSHClient()
            ssh.load_system_host_keys()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(assignedIp, username='root', password=machinePassword)

            #let execute list of command, take it from jsonconfigfile
            for c in data['execOnServer']:
                print('start')
                print(c)
                ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(c)                
                print(ssh_stdout.read())
                print('end')
                print(c)
            ssh.close()
        if(p.installer is not None):
            print('preparo upload dell\'installer')
            srv = pysftp.Connection(host=assignedIp, username="root",password=machinePassword)
            srv.put(p.installer.name)
            ssh = paramiko.SSHClient()
            ssh.load_system_host_keys()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(assignedIp, username='root', password=machinePassword)
            ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command('chmod 700 '+os.path.basename(p.installer.name))
            ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command('./'+os.path.basename(p.installer.name))
            print(ssh_stdout.read())
            print(ssh_stderr.read())
            ssh.close()
        else:
            time.sleep(3)
    json_mylist = json.dumps(datas, separators=(',', ':'))
    print(json_mylist)