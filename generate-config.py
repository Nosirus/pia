from argparse import ArgumentParser
from piawg import piawg
from pick import pick
from getpass import getpass
from datetime import datetime

# Get commandline arguments
parser = ArgumentParser(description="Wireguard configuration generator")
parser.add_argument("-u", "--username", type=str, metavar="USER", dest="username", default="")
parser.add_argument("-p", "--password", type=str, metavar="PASS", dest="password", default="")
parser.add_argument("-r", "--region", type=str, metavar="REG", dest="region")
parser.add_argument("-o", "--out", type=str, metavar="OUT", dest="out")

args = parser.parse_args()

pia = piawg()

# Generate public and private key pair
pia.generate_keys()

# Select region
if args.region and args.region in pia.server_list.keys():
    pia.set_region(args.region)
else:
    title = 'Please choose a region: '
    options = sorted(list(pia.server_list.keys()))
    option, index = pick(options, title)
    pia.set_region(option)
    print("Selected '{}'".format(option))

# Get token
if pia.get_token(args.username, args.password):
    print("Login successful!")
else:
    while True:
        username = input("\nEnter PIA username: ")
        password = getpass()
        if pia.get_token(username, password):
            print("Login successful!")
            break
        else:
            print("Error logging in, please try again...")

# Add key
status, response = pia.addkey()
if status:
    print("Added key to server!")
else:
    print("Error adding key to server")
    print(response)

# Build config
timestamp = int(datetime.now().timestamp())
location = pia.region.replace(' ', '-')
config_file = args.out if args.out else 'PIA-{}-{}.conf'.format(location, timestamp)
print("Saving configuration file {}".format(config_file))
with open(config_file, 'w') as file:
    file.write('[Interface]\n')
    file.write('Address = {}\n'.format(pia.connection['peer_ip']))
    file.write('PrivateKey = {}\n'.format(pia.privatekey))
    file.write('DNS = {},{}\n\n'.format(pia.connection['dns_servers'][0], pia.connection['dns_servers'][1]))
    file.write('[Peer]\n')
    file.write('PublicKey = {}\n'.format(pia.connection['server_key']))
    file.write('Endpoint = {}:1337\n'.format(pia.connection['server_ip']))
    file.write('AllowedIPs = 0.0.0.0/0\n')
    file.write('PersistentKeepalive = 25\n')
