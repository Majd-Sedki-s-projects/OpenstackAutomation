from neutronclient.v2_0 import client as neutron_client
from novaclient import client as nova_client

class FloatingIP(object):
    def __init__(self, sess):
        self.session = sess

    def assignFloatingIP(self, name):
        neutron = neutron_client.Client(session=self.session)
        nova = nova_client.Client("2.1", session=self.session)

        #Gets only floating ips that are not active
        floatingIP = neutron.list_floatingips(status='DOWN')
        newFloatingIP = floatingIP['floatingips'][0]['floating_ip_address']

        #Gets new instance's fixed ip
        server = nova.servers.list(detailed=True,search_opts={'name':name})
        print(server)

        #nova.server.add_floating_ip(address=newFloatingIP, fixed_address=serverIP)