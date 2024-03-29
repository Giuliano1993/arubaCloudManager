from ArubaCloud.PyArubaAPI import CloudInterface
from ArubaCloud.objects import SmartVmCreator
from ArubaCloud.objects import ProVmCreator
import argparse
import sys
import os
import json
import pysftp
from dotenv import load_dotenv
import time;
import paramiko
load_dotenv()


def importConfig(filecont, installer = None, silent = False):
    
    data = json.load(filecont)

    password = os.getenv('PASSWORD')
    username = os.getenv('USERNAME')
    if username is None or username == '': sys.exit("missing  username")
    if password is None or password == '': sys.exit("missing  password")
    ci = CloudInterface(dc=1)
    ci.login(username=username, password=password, load=True)
    ci.get_hypervisors()

    #Search os required by json
    ts = ci.find_template(name=data['os'], hv=4)
    #selecte only the enabled ones...
    available = list(filter(lambda t: t.enabled == True,ts))
    #... and choose the first
    templ = available[0]



    if templ is None: sys.exit("missing  system")

    machineName = data['machineName'] if 'machineName' in data and data['machineName'] != '' else  data['os'].replace(' ','_')+str(time.time())


    machinePassword = data['rootPassword'] if 'rootPassword' in data else ''
    if machinePassword is None or machinePassword == '':
        raise 'YOU FORGOT TO SPECIFY ROOT PASSWORD'

    ci = CloudInterface(dc=1)
    ci.login(username=username, password=password, load=True)

    machineType = data['serverType'] if 'serverType' in data and data['serverType'] != '' else 'smart'

    if machineType == 'pro':
        ip = ci.purchase_ip()
        c = ProVmCreator(name=machineName, admin_password=machinePassword, template_id=templ.template_id, auth_obj=ci.auth)
        cpuQty = data['cpuQty'] if 'cpuQty' in data else 0
        if cpuQty is None or cpuQty == 0:
            cpuQty = 1
        elif isinstance(cpuQty,str) == True:
            raise 'CPU qty must be an integer'

        ramQty = data['ramQty'] if 'ramQty' in data else 0
        if ramQty is None or ramQty == 0:
            ramQty = 1
        elif isinstance(ramQty,str) == True:
            raise 'RAM qty must be an integer!'

        diskSize = data['hdSize'] if 'hdSize' in data else 0
        if diskSize is None or diskSize == 0:
            diskSize = 10
        elif isinstance(diskSize,str) == True:
            raise 'HD size must be an integer'

        c.set_cpu_qty(cpuQty)
        c.set_ram_qty(ramQty)
        c.add_public_ip(public_ip_address_resource_id=ip.resid)
        c.add_virtual_disk(diskSize)

    else:
        packageSize = data['packageSize'] if 'packageSize' in data and data['packageSize'] != '' else 'small'

        c = SmartVmCreator(name=machineName, admin_password=machinePassword, template_id=templ.template_id, auth_obj=ci.auth)
        c.set_type(ci.get_package_id(packageSize))
    res = c.commit(url=ci.wcf_baseurl, debug=not silent)
    if silent != True:
        print(res)

    
    time.sleep(5)
    if res == True:
        ci = CloudInterface(dc=1)
        ci.login(username=username, password=password, load=True)        
        assignedIp = ci.get_vm(machineName)[0].ip_addr
        datas = {
            'ip':assignedIp,
            'user':'root',
            'password':machinePassword
        }
        status = 0
        while status != 3:
            if silent != True:
                print('.')
            ci = CloudInterface(dc=1)
            ci.login(username=username, password=password, load=True)            
            vm = ci.get_vm(machineName)[0]
            status = vm.status
            if status == 3:
                if 'execOnServer' in data:
                    ssh = paramiko.SSHClient()
                    ssh.load_system_host_keys()
                    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())                
                    ssh.connect(assignedIp, username='root', password=machinePassword)
                    #let execute list of command, take it from jsonconfigfile
                    for c in data['execOnServer']:
                        if silent != True:
                            print('now executing '+c+' ...')
                        ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(c)
                        if silent != True:
                            print(ssh_stdout.read())
                if(installer is not None):
                    if silent != True:
                        print('preparo upload dell\'installer')
                    cnopts = pysftp.CnOpts()
                    cnopts.hostkeys = None   
                    srv = pysftp.Connection(host=assignedIp, username="root",password=machinePassword,cnopts=cnopts)                
                    srv.put(installer.name)
                    ssh = paramiko.SSHClient()
                    ssh.load_system_host_keys()
                    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                    ssh.connect(assignedIp, username='root', password=machinePassword)
                    ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command('chmod 700 '+os.path.basename(installer.name))
                    ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command('./'+os.path.basename(installer.name))
                    if silent != True:
                        print(ssh_stdout.read())
                        print(ssh_stderr.read())
                    ssh.close()
            else:
                time.sleep(3)
        json_mylist = json.dumps(datas, separators=(',', ':'))
        print(json_mylist)
    else:
        print('Ops an error occured while tryng to create your machine')

