from neutronclient.v2_0 import client as neutron_client

#Not working yet, trying to figure out the neutron client
class CreateNetwork(object):
    def __init__(self, sess):
        self.session = sess

    def create_network(self, body):
        neutron = neutron_client.Client(session=self.session)
        neutron.create_network({'network':body})
        return neutron