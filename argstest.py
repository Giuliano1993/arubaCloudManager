import argparse

from pprint import pprint


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--datacenter', help='Specify datacenter to login.', action='store', type=int, dest='dc')
    parser.add_argument('-p', '--pattern', help='Specify pattern to search.', action='store', dest='pattern')
    parser.add_argument('-u', '--username', help='Specify username.', action='store', dest='username')
    parser.add_argument('-w', '--password', help='Specify password.', action='store', dest='password')
    parser.add_argument('-i', '--initialize', help="Initialize new cloud machine", action="store", type=bool, dest="action", default=False)
    p = parser.parse_args()
    if p.action:
        print('allora install')
    else:
        print('non installo')
    