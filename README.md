# Aruba Cloud Manager

This is a wrapper command line utility to manage Aruba cloud servers

## Installation 
To get this to work you need to install its dependencies:

~~~
pip install -U python-dotenv
pip install pyarubacloud
~~~

Insert inside .env file your aruba cloud credentials.

### List Available Templates

~~~
python index.py -a list -s osYouNeedHere
~~~


### Create new machine

~~~
python index.py -a new -p serverPassword -n serverName
~~~