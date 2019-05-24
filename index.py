from ArubaCloud.PyArubaAPI import CloudInterface
from ArubaCloud.objects import SmartVmCreator
from ArubaCloud.objects import ProVmCreator
import argparse
import sys
import os
import json
from dotenv import load_dotenv
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
    
    p = parser.parse_args()

    if p.config is not None:
        import configImport
        configImport.importConfig(p.config)
        exit()

    action = p.action
    password = os.getenv('PASSWORD')
    username = os.getenv('USERNAME')
    if username is None or username == '': sys.exit("missing  username")
    if password is None or password == '': sys.exit("missing  password")



    if action == 'new':
        if p.template is None: sys.exit("missing  system id")
        if isinstance(p.template, int) != True: sys.exit("template id must be and integer")
        machineName = raw_input('Choose a name for your new machine:  ')
        while machineName == None or machineName == '':
            machineName = raw_input('You have to chosse a name for your new machine to continue:  ')

        machinePassword = raw_input('Choose a strong password for logging in as root:  ')
        while machinePassword == None or machinePassword == '':
            machinePassword = raw_input('You have to chosse a root password to continue:  ')

        ci = CloudInterface(dc=1)
        ci.login(username=username, password=password, load=True)
    
        if p.type == 'pro':
            ip = ci.purchase_ip()
            c = ProVmCreator(name=machineName, admin_password=machinePassword, template_id=p.template, auth_obj=ci.auth)
            cpuQty = input('Choose how many cpu you want on your machine: ')
            if cpuQty is None or cpuQty == 0:
                cpuQty = 1
            elif isinstance(cpuQty,str) == True:
                while isinstance(cpuQty,int) == False:
                    cpuQty = input('CPU qty must be an integer: ')
                    if cpuQty is None or cpuQty == 0:
                        cpuQty = 1


            ramQty = input('Choose how much RAM you want on your machine: ')
            if ramQty is None or ramQty == 0:
                ramQty = 1
            elif isinstance(ramQty,str) == True:
                while isinstance(ramQty,int) == False:
                    ramQty = input('RAM qty must be an integer: ')
                    if ramQty is None or ramQty == 0:
                        ramQty = 1

            c.set_cpu_qty(cpuQty)
            c.set_ram_qty(ramQty)

            c.add_public_ip(public_ip_address_resource_id=ip.resid)

            diskSize = input('Choose how many GB you want on your HD: ')
            if diskSize is None or diskSize == 0:
                diskSize = 1
            elif isinstance(diskSize,str) == True:
                while isinstance(diskSize,int) == False:
                    diskSize = input('HD size must be an integer: ')
                    if diskSize is None or diskSize == 0:
                        diskSize = 1
            
            c.add_virtual_disk(diskSize)
            #TODO: add a loop to add x virtual disks 
        else:
            packageSize = ''
            while packageSize is None or packageSize == '':
                packageSize = raw_input('Choose a package for your brand new machine! [s = small / m = medium / l = large / xl = extra large / h = help]')
                if(packageSize == 's'):
                    packageSize = 'small'
                elif(packageSize == 'm'):
                    packageSize = 'medium'
                elif(packageSize == 'l'):
                    packageSize = 'large'
                elif(packageSize == 'xl'):
                    packageSize = 'extra large'
                elif(packageSize == 'h'):
                    print('\n')
                    print('Small package: \n CPU = 1; RAM = 1GB; HD = 20GB')
                    print('\n')
                    print('Medium package: \n CPU = 1; RAM = 2GB; HD = 40GB')
                    print('\n')
                    print('Large package: \n CPU = 2; RAM = 4GB; HD = 80GB')
                    print('\n')
                    print('Extra large package: \n CPU = 4; RAM = 8GB; HD = 160GB')
                    print('\n')
                    packageSize = ''
                else:
                    print('you have chosen an invalid value')
                    packageSize = ''


            c = SmartVmCreator(name=machineName, admin_password=machinePassword, template_id=p.template, auth_obj=ci.auth)
            c.set_type(ci.get_package_id(packageSize))

        res = c.commit(url=ci.wcf_baseurl, debug=True)
        print(res)

        if res == True:
            assignedIp = ci.get_vm(p.name)[0].ip_addr
            print('To connect your new machine via ssh use these credentials')
            print('IP : '+assignedIp)
            print('User: root')
            print('Password: '+p.password)
        else:
            print('Ops an error occured while tryng to create your machine')


    elif action == 'templateList':
        if p.search is None: sys.exit("missing  system name")

        ci = CloudInterface(dc=1)
        ci.login(username=username, password=password, load=True)
        ci.get_hypervisors()

        from pprint import pprint
        #pprint(ci.find_template(name=p.search, hv=4))
        ts = ci.find_template(name=p.search, hv=4)
        for t in (tt for tt in ts if tt.enabled == True):
            pprint(t)
            
    elif action == 'list':
        ci = CloudInterface(dc=1)
        ci.login(username=username, password=password, load=True)
        vms = ci.vmlist
        vmlist = []
        for vm in vms:
            if p.json:
                vmlist.append({
                    'id':str(vm.sid),
                    'name':vm.vm_name,
                    'ip':vm.ip_addr,
                    'status':vm.status,
                    'cpu':str(vm.cpu_qty),
                    'ram':str(vm.ram_qty),
                    'hdSize':str(vm.hd_total_size),
                    'hdNumber':str(vm.hd_qty)
                })
            else:
                print('\n')
                print('Machine ID: '+str(vm.sid))
                print('Machine Name: '+vm.vm_name)
                print('Machine Ip: '+vm.ip_addr)
                print('Machine Status: '+str(vm.status))
                if p.details:
                    print('CPU qty: '+str(vm.cpu_qty))
                    print('RAM qty: '+str(vm.ram_qty))
                    print('HDs Size: '+str(vm.hd_total_size)+'GB')
                    print('HDs qty: '+str(vm.hd_qty))

                print('\n---------------------\n')
        if p.json:
            json_mylist = json.dumps(vmlist, separators=(',', ':'))
            print(json_mylist)
    elif action == 'info':
        ci = CloudInterface(dc=1)
        ci.login(username=username, password=password, load=True)
        name = raw_input('please enter machine name: ')
        vm = ci.get_vm(name)[0]
        print('Machine ID: '+str(vm.sid))
        print('Machine Name: '+vm.vm_name)
        print('Machine Ip: '+vm.ip_addr)
        print('Machine Status: '+str(vm.status))
        if p.details:
            print('CPU qty: '+str(vm.cpu_qty))
            print('RAM qty: '+str(vm.ram_qty))
            print('HDs Size: '+str(vm.hd_total_size)+'GB')
            print('HDs qty: '+str(vm.hd_qty))

    else:
        print('No valid action selected: choose templateList, list or new')