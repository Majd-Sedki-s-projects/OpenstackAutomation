from neutronclient.v2_0 import client as neutron_client


class CreateRouter(object):
    def __init__(self, sess):
        self.session = sess

    def create_router(self, body):
        neutron = neutron_client.Client(session=self.session)
        neutron.create_router({'router':body})
        return neutron

    def delete_router(self, routerID):
        neutron = neutron_client.Client(session=self.session)
        neutron.delete_router(routerID)
        return neutron

    def get_router_id(self, name):
        neutron = neutron_client.Client(session=self.session)
        try:
            router_id = neutron.list_routers(name=name)["routers"][0]["id"]
            return router_id
        except:
            return "", False