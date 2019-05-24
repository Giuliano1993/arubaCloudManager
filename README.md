# Aruba Cloud Manager

This is a wrapper command line utility to manage Aruba cloud servers

## Installation 
To get this to work you need to install its dependencies:

~~~bash
pip install -U python-dotenv
pip install pyarubacloud
~~~

Insert inside .env file your aruba cloud credentials.

### List Available Templates

~~~bash
python index.py -a templateList -s osYouNeedHere
~~~


### Create new machine

~~~bash
python index.py -a new -t templateId
~~~

### Check server list

~~~bash
python index.py -a list
~~~

or, if you want more details

~~~bash
python index.py -a list -d
~~~

##### Json format

If you want an output in json format, just specify the -j parameter

~~~bash
python index.py -a list -j
~~~

### Automatic mode
You can pass a config file in json format to let all the operation work seamlessly and have in return a json in the stdin

~~~bash
python index.py -c config.json
~~~

this is the config file schema

~~~json
{
    "serverType":"smart",
    "os":"Ubuntu Server 16",
    "rootPassword":"mySecurePassword",
    "takeSnapshot":true,
    "machineName":"newMachine",
    "packageSize":"small",
    "cpuQty":2,
    "ramQty":2,
    "hdSize":2,
    "execOnServer":[
        "apt-get update",
        "apt-get install apache2",
        "apt-get install mysql-server",
        "apt-get install php libapache2-mod-php",
        "systemctl restart apache2"
    ]
}
~~~
the only mandatory parameters are ```os``` and ```rootPassword``` 