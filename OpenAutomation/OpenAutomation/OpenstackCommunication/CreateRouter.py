from neutronclient.v2_0 import client as neutron_client

#Not working yet, trying to figure out the neutron client
class CreateRouter(object):
    def __init__(self, sess):
        self.session = sess

    def create_router(self, body):
        neutron = neutron_client.Client(session=self.session)
        neutron.create_router({'router':body})
        return neutron
