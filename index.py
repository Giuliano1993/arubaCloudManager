from ArubaCloud.PyArubaAPI import CloudInterface
from ArubaCloud.objects import SmartVmCreator
from ArubaCloud.objects import ProVmCreator
import argparse
import sys
import os
from dotenv import load_dotenv
load_dotenv()
#ci.login(username="ARU-238352", password="fBSCu114!f", load=True)

if __name__ == '__main__':
    
    parser = argparse.ArgumentParser()
    
    parser.add_argument('-t', '--template', help="the name of the template to search", action="store", type=int, dest="template")
    parser.add_argument('-s', '--searchTemplate', help="the name of the template to search", action="store", type=str, dest="search")
    parser.add_argument('--type', help="type of server to instantiate", action="store", choices=['pro','smart'], type=str, dest="type")
    parser.add_argument('-a', '--action', help="choose an action to perform", choices=['templateList','new','list'], nargs="?", action="store",default="list",dest="action")
    parser.add_argument('-p', '--password', help='machine root password.', action='store', dest='password')       
    parser.add_argument('-n', '--name', help='machine name.', action='store', dest='name')    
    parser.add_argument('-d', '--details', help="get more details on the machines", action="store_true")
    
    p = parser.parse_args()

    action = p.action
    password = os.getenv('PASSWORD')
    username = os.getenv('USERNAME')
    if username is None or username == '': sys.exit("missing  username")
    if password is None or password == '': sys.exit("missing  password")



    if action == 'new':
        if p.template is None: sys.exit("missing  system id")
        if p.password is None: sys.exit("server password missing")
        if isinstance(p.template, int) != True: sys.exit("template id must be and integer")
        if p.name is None:
            name = randomString()
        else:
            name = p.name
            
        ci = CloudInterface(dc=1)
        ci.login(username=username, password=password, load=True)
        

        # template_id: 1605 [Template Name: CentOS 7.x 64bit, Hypervisor: VW, Id: 1605, Enabled: True]

        if p.type == 'pro':
            ip = ci.purchase_ip()
            c = ProVmCreator(name=name, admin_password=p.password, template_id=p.template, auth_obj=ci.auth)
            c.set_cpu_qty(2)
            c.set_ram_qty(6)

            c.add_public_ip(public_ip_address_resource_id=ip.resid)
            c.add_virtual_disk(20)
            #c.add_virtual_disk(40)
        else:
            c = SmartVmCreator(name=p.name, admin_password=p.password, template_id=p.template, auth_obj=ci.auth)
            c.set_type(ci.get_package_id('small'))

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
        pprint(ci.find_template(name=p.search, hv=4))
    elif action == 'list':
        ci = CloudInterface(dc=1)
        ci.login(username=username, password=password, load=True)
        vms = ci.vmlist
        for vm in vms:
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
    else:
        print('No valid action selected: choose templateList, list or new')