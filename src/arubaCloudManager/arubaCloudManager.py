from ArubaCloud.PyArubaAPI import CloudInterface
from ArubaCloud.objects import SmartVmCreator, ProVmCreator
from pprint import pprint
import sys, pysftp, time, os, sys, json, paramiko

class arubaCloudManager:
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.ci = self.__init_ci__()

    def __init_ci__(self):
        ci = CloudInterface(dc=1)
        ci.login(username=self.username, password=self.password, load=True)
        return ci

    def getTemplateList(self,name):
        if name is None: sys.exit("missing  system name")
        self.ci.get_hypervisors()
        ts = self.ci.find_template(name=name, hv=4)
        for t in (tt for tt in ts if tt.enabled == True):
            pprint(t)
    def getVmList(self,details = False):
        vms = self.ci.vmlist
        vmlist = []
        for vm in vms:
            print('\n')
            print('Machine ID: '+str(vm.sid))
            print('Machine Name: '+vm.vm_name)
            print('Machine Ip: '+vm.ip_addr)
            print('Machine Status: '+str(vm.status))
            if details:
                print('CPU qty: '+str(vm.cpu_qty))
                print('RAM qty: '+str(vm.ram_qty))
                print('HDs Size: '+str(vm.hd_total_size)+'GB')
                print('HDs qty: '+str(vm.hd_qty))
            print('\n---------------------\n')
    def getInfo(self,details=False):
        name = raw_input('please enter machine name: ')
        vm = self.ci.get_vm(name)[0]
        print('Machine ID: '+str(vm.sid))
        print('Machine Name: '+vm.vm_name)
        print('Machine Ip: '+vm.ip_addr)
        print('Machine Status: '+str(vm.status))
        if details:
            print('CPU qty: '+str(vm.cpu_qty))
            print('RAM qty: '+str(vm.ram_qty))
            print('HDs Size: '+str(vm.hd_total_size)+'GB')
            print('HDs qty: '+str(vm.hd_qty))
    def createVM(self, p):
        self.ci.get_hypervisors()
        #set the machine template
        template = None 
        while template is None or isinstance(template, int) != True:
            template = raw_input('Choose a template id')
            template = int(template)
            if template is None: 
                print("missing  system id")
            elif isinstance(template, int) != True: 
                print("template id must be and integer")

        #set the machine name
        self.machineName = raw_input('Choose a name for your new machine:  ')
        while self.machineName == None or self.machineName == '':
            self.machineName = raw_input('You have to chosse a name for your new machine to continue:  ')

        #set the machine password 
        self.machinePassword = raw_input('Choose a strong password for logging in as root:  ')
        while self.machinePassword == None or self.machinePassword == '':
            self.machinePassword = raw_input('You have to chosse a root password to continue:  ')
        
        vmType = p.type if p.type is not None else raw_input('do you want a pro o smart machine?')
        while vmType is None or (vmType != 'pro' and vmType != 'smart'):
            vmType = raw_input('you should choose either a pro or a smart vm')

        if vmType == 'pro':
            res = self._createVmPro(p,template)
        else:
            res = self._createVmSmart(p,template)


        time.sleep(5)
        if res == True:
            self.ci = self.__init_ci__()
            assignedIp = self.ci.get_vm(self.machineName)[0].ip_addr
            datas = {
                'ip':assignedIp,
                'user':'root',
                'password':self.machinePassword
            }
            status = 0
            while status != 3:
                self.ci = self.__init_ci__()
                vm = self.ci.get_vm(self.machineName)[0]
                status = vm.status
                print('.')
                if status == 3 and p.installer is not None:
                    print('preparo upload dell\'installer')
                    cnopts = pysftp.CnOpts()
                    cnopts.hostkeys = None   
                    srv = pysftp.Connection(host=assignedIp, username="root",password=self.machinePassword,cnopts=cnopts)                
                    srv.put(p.installer.name)
                    ssh = paramiko.SSHClient()
                    ssh.load_system_host_keys()
                    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                    ssh.connect(assignedIp, username='root', password=self.machinePassword)
                    ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command('chmod 700 '+os.path.basename(p.installer.name))
                    ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command('./'+os.path.basename(p.installer.name))
                    print(ssh_stdout.read())
                    print(ssh_stderr.read())
                    ssh.close()
                else:
                    time.sleep(3)
            print('To connect your new machine via ssh use these credentials')
            print('IP : '+assignedIp)
            print('User: root')
            print('Password: '+self.machinePassword)
        else:
            print('Ops an error occured while tryng to create your machine')     


    def _createVmPro(self,p,template):
        ip = self.ci.purchase_ip()
        c = ProVmCreator(name=self.machineName, admin_password=self.machinePassword, template_id=template, auth_obj=self.ci.auth)
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
        return c.commit(url=self.ci.wcf_baseurl, debug=True)
        #TODO: add a loop to add x virtual disks         


    def _createVmSmart(self,p,template):
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


        c = SmartVmCreator(name=self.machineName, admin_password=self.machinePassword, template_id=template, auth_obj=self.ci.auth)
        c.set_type(self.ci.get_package_id(packageSize))
        return c.commit(url=self.ci.wcf_baseurl, debug=True)

    def importConfig(self, filecont, installer = None, silent = False):
        data = json.load(filecont)
        self.ci.get_hypervisors()

        #Search os required by json
        ts = self.ci.find_template(name=data['os'], hv=4)
        #selecte only the enabled ones...
        available = list(filter(lambda t: t.enabled == True,ts))
        #... and choose the first
        templ = available[0]



        if templ is None: sys.exit("missing  system")

        machineName = data['machineName'] if 'machineName' in data and data['machineName'] != '' else  data['os'].replace(' ','_')+str(time.time())

        machinePassword = data['rootPassword'] if 'rootPassword' in data else ''
        if machinePassword is None or machinePassword == '':
            raise 'YOU FORGOT TO SPECIFY ROOT PASSWORD'

        machineType = data['serverType'] if 'serverType' in data and data['serverType'] != '' else 'smart'

        if machineType == 'pro':
            ip = self.ci.purchase_ip()
            c = ProVmCreator(name=machineName, admin_password=machinePassword, template_id=templ.template_id, auth_obj=self.ci.auth)
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

            c = SmartVmCreator(name=machineName, admin_password=machinePassword, template_id=templ.template_id, auth_obj=self.ci.auth)
            c.set_type(self.ci.get_package_id(packageSize))
        res = c.commit(url=self.ci.wcf_baseurl, debug=not silent)
        if silent != True:
            print(res)

        
        time.sleep(5)
        if res == True:
            self.ci = self.__init_ci__()
            assignedIp = self.ci.get_vm(machineName)[0].ip_addr
            datas = {
                'ip':assignedIp,
                'user':'root',
                'password':machinePassword
            }
            status = 0
            while status != 3:
                if silent != True:
                    print('.')
                self.ci = self.__init_ci__()            
                vm = self.ci.get_vm(machineName)[0]
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