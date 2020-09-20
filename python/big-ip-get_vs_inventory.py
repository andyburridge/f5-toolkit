# module imports
import sys
import requests
import getpass
from f5.bigip import ManagementRoot

# disable ssl certificate warnings
requests.packages.urllib3.disable_warnings()

# prompt for user credentals
bigip = input("BIG-IP: ")
username = input("Username: ")
password = getpass.getpass("Password for " + username + ": ")

# variable declarations
mgmt = ManagementRoot(bigip, username, password)
vs_details = {}
pool_details = {}
monitor_details = {}

# this list is needed as each monitor type is referenced in a separate collection. The way the collections are referenced
# in the API is annoyingly different from the way they are returned when querying.  This list encompasses all the 
# collection endpoints in the format they can be queried by the API, so we can iterate over it.  Ugly, but works.
monitorTypes = ['https',
                'https_s',
                'diameters',
                'dns_s',
                'externals',
                'firepass_s',
                'ftps',
                'gateway_icmps',
                'icmps',
                'imaps',
                'inbands',
                'ldaps',
                'module_scores',
                'mqtts',
                'mssqls',
                'mysqls',
                'nntps',
                'oracles',
                'pop3s',
                'postgresqls',
                'radius_s',
                'radius_accountings',
                'real_servers',
                'rpcs',
                'sasps',
                'scripteds',
                'sips',
                'smbs',
                'smtps',
                'snmp_dcas',
                'snmp_dca_bases',
                'soaps',
                'tcps',
                'tcp_echos',
                'tcp_half_opens',
                'udps',
                'virtual_locations',
                'waps',
                'wmis']

virtual_servers = mgmt.tm.ltm.virtuals.get_collection()
pools = mgmt.tm.ltm.pools.get_collection()


# virtual_servers ultimately becomes the dictionary that we add everything into, so the first
# entry is a comma, this is to separate the dictionary key (vs name) from the first entry.
for vs in virtual_servers:
    vs_details.update({vs.name:[","]})
    if hasattr(vs, 'partition'):
    	vs_details[vs.name].append(str(vs.partition) + ",")
    else:
    	vs_details[vs.name].append(",")
    if hasattr(vs, 'destination'):
        # destination comprises of virtual address, prefixed by partition, and suffixed by 
        # route domain andport: e.g.  /PREP-CORP/1.1.1.1%3:80
        # we want to strip off the partition and route domain, and take just the address and port, as csv
        vs_port_list = str(vs.destination).split(':')
        vs_port = vs_port_list[1]
        vs_address_list = str(vs.destination).split('/')
        vs_address_rd = vs_address_list[2].split('%')
        vs_address = vs_address_rd[0]
        vs_details[vs.name].append(vs_address + "," + vs_port + ",")
    else:
    	vs_details[vs.name].append(",")
    if hasattr(vs, 'pool'):
    	# strip partition from the pool
    	vs_pool_list = str(vs.pool).split('/')
    	vs_pool = vs_pool_list[2]
    	vs_details[vs.name].append(vs_pool + ",")
    else:
    	vs_details[vs.name].append(",")
    # for endpoints that potentially return multiple objects, such as irules and profile, create the list first
    # and then append to the list, this allows changing of the delimeter, so formatting isn't impacted when
    # exporting to .csv
    irules_list = []
    if hasattr(vs, 'rules'):
        vs_details[vs.name].append(str(vs.rules).replace(',',':') + ",")
    else:
    	vs_details[vs.name].append(",")
    profile_list = []
    for profile in vs.profiles_s.get_collection():
        profile_list.append(str(profile.name))
    vs_details[vs.name].append(str(profile_list).replace(',',':') + ",")


for pool in pools:
    pool_details.update({pool.name:[]})
    # for endpoints that potentially return multiple objects, such as monitors and nodes, create the list first
    # and then append to the list, this allows changing of the delimeter, so formatting isn't impacted when
    # exporting to .csv
    monitor_list = []
    if hasattr(pool, 'monitor'):
        monitor_list.append(str(pool.monitor))
    else:
        pool_details[pool.name].append(",")
    pool_details[pool.name].append(str(monitor_list) + ",")
    if hasattr(pool, 'loadBalancingMode'):
        pool_details[pool.name].append(str(pool.loadBalancingMode) + ",")
    else:
    	pool_details[pool.name].append(",")
    node_list = []
    for member in pool.members_s.get_collection():
        node_list.append([str(member.name),str(member.priorityGroup),str(member.ratio)])
    pool_details[pool.name].append(str(node_list).replace(',',':') + ",")


for t in monitorTypes:
    # iterate over all the monitor types, as defined in the list above.  
    endp = 'mgmt.tm.ltm.monitor.' + t + '.get_collection()'
    e = eval(endp)    
    for monitor in e:
        monitor_details.update({monitor.name:[str(t) + ","]})
        if hasattr(monitor, 'destination'):
            monitor_details[monitor.name].append(str(monitor.destination) + ",")
        else:
        	monitor_details[monitor.name].append(",")
        if hasattr(monitor, 'send'):
            monitor_details[monitor.name].append(str(monitor.send) + ",")
        else:
        	monitor_details[monitor.name].append(",")
        if hasattr(monitor, 'recv'):
            monitor_details[monitor.name].append(str(monitor.recv) + ",")
        else:
        	monitor_details[monitor.name].append(",")
        if hasattr(monitor, 'interval'):
            monitor_details[monitor.name].append(str(monitor.interval) + ",")
        else:
        	monitor_details[monitor.name].append(",")
        if hasattr(monitor, 'timeout'):
            monitor_details[monitor.name].append(str(monitor.timeout) + ",")
        else:
        	monitor_details[monitor.name].append(",")
        if hasattr(monitor, 'sslProfile'):
            monitor_details[monitor.name].append(str(monitor.sslProfile) + ",")
        else:
        	monitor_details[monitor.name].append(",")


# Combine dictionaries, first matching the monitor name (key for monitor_details), to the corresponding pool entry,
# then the pool name (key for pool_details) to the corresponding virtual server entry.
for pool_entry in pool_details:
    for monitor_entry in monitor_details:
        if str(monitor_entry) in str(pool_details[pool_entry]):
            for entry in monitor_details[monitor_entry]:
                pool_details[pool_entry].append(str(entry))
            break

for vs_entry in vs_details:
    for pool_entry in pool_details:
        if str(pool_entry) in str(vs_details[vs_entry]):
            for entry in pool_details[pool_entry]:
                vs_details[vs_entry].append(str(entry))
            break


# Create output .csv file, write headers, then write data.
try:
    vs_file = open("virtual server details.csv","w")
except IOError:
    sys.exit("Unable to create the output file.")

vs_file.write("Virtual Server,Partition,IP,VS Port,Pool(s),iRule(s),Profile(s),Pool Monitor(s),LB Method,Node(s) w/ Port + Pri Grp + Ratio,Monitor Type,Monitor Port,Send,Receive,Interval,Timeout,SSL-Profile")
vs_file.write("\n")

for vs_entry in vs_details:
    vs_complete = str(vs_entry) + "".join(vs_details[vs_entry])
    vs_file.write(vs_complete)
    vs_file.write("\n")

vs_file.close()

