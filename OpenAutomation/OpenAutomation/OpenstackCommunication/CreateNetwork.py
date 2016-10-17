from neutronclient.v2_0 import client as neutron_client

class CreateNetwork(object):
    def __init__(self, sess):
        self.session = sess

    def create_network(self, body):
        neutron = neutron_client.Client(session=self.session)
        neutron.create_network({'network':body})
        return neutron

    def delete_network_byName(self, name):
        neutron = neutron_client.Client(session=self.session)
        networks = neutron.list_networks(name=name)
        network_id = networks['networks'][0]['id']
        neutron.delete_network(network_id)
        print("Network: " + name + " has been removed.")

    def delete_network_byId(self, id):
        neutron = neutron_client.Client(session=self.session)
        neutron.delete_network(id)
        print("Network ID: " + id + " has been removed.")