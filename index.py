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
    parser.add_argument('-a', '--action', help="choose an action to perform", choices=['list','new'], nargs="?", action="store",default="list",dest="action")
    parser.add_argument('-u', '--username', help='Specify username.', action='store', dest='username')
    parser.add_argument('-p', '--password', help='Specify password.', action='store', dest='password')    
    parser.add_argument('-n', '--name', help='machine name.', action='store', dest='name')    
    
    p = parser.parse_args()

    action = p.action
    password = os.getenv('PASSWORD')
    username = os.getenv('USERNAME')
    if username is None or username == '': sys.exit("missing  username")
    if password is None or password == '': sys.exit("missing  password")



    def randomString(stringLength=10):
        letters = string.ascii_lowercase
        return ''.join(random.choice(letters) for i in range(stringLength))
    if action == 'new':
        if p.template is None: sys.exit("missing  system id")
        if isinstance(p.template, int) != True: sys.exit("template id must be and integer")
        if p.name is None:
            name = randomString()
        else:
            name = p.name
            
        ci = CloudInterface(dc=1)
        ci.login(username=username, password=password, load=True)
        ip = ci.purchase_ip()

        # template_id: 1605 [Template Name: CentOS 7.x 64bit, Hypervisor: VW, Id: 1605, Enabled: True]

        c = ProVmCreator(name=name, admin_password='?W@^ckx#d?3WsR2F', template_id=p.template, auth_obj=ci.auth)
        c.set_cpu_qty(2)
        c.set_ram_qty(6)

        c.add_public_ip(public_ip_address_resource_id=ip.resid)
        c.add_virtual_disk(20)
        #c.add_virtual_disk(40)

        print(c.commit(url=ci.wcf_baseurl, debug=True))


    elif action == 'list':
        if p.search is None: sys.exit("missing  system name")

        ci = CloudInterface(dc=1)
        ci.login(username=username, password=password, load=True)
        ci.get_hypervisors()

        from pprint import pprint
        pprint(ci.find_template(name=p.search, hv=4))
    else:
        print('No valid action selected: choose list or new')