from ArubaCloud.PyArubaAPI import CloudInterface
import sys

ci = CloudInterface(dc=1)
ci.login(username="ARU-238352", password="fBSCu114!f", load=True)
ci.get_hypervisors()

from pprint import pprint
pprint(ci.find_template(name=sys.argv[1], hv=4))