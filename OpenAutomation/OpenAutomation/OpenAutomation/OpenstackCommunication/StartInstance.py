from novaclient import client as nova_client
from time import sleep
NOVA_CLIENT_VERSION = "2.1"


class StartInstance(object):
    def __init__(self, sess):
        self.session = sess

    def start_instance(self, server_name, image, size, userdata, network_id):
        nova = nova_client.Client("2.1", session=self.session)
        flavour = nova.flavors.find(name=size)
        image = nova.images.find(name=image)
        #network = nova_client.networks.find(name="public")
        print("Creating server in object")
        server = ""
        server = nova.servers.create(name=str(server_name), flavor=flavour, image=image,
                            userdata=userdata, #Userdata to add cloud-init file
                            nics=[{'net-id': network_id}])

        print("finding server id")
        # Wait for server to be built.
        server = nova.servers.find(id=server.id)
        print(str(server.status))
        while server.status != 'ACTIVE':
            sleep(3)
            print("Waiting for server to build...")
            server = nova.servers.find(id=server.id)
        server = nova.servers.find(id=server.id)
        if server.status == 'ACTIVE':
            return nova, True
 
    def add_security_to_server(self, server_name, security_group_name):
        nova = nova_client.Client(NOVA_CLIENT_VERSION, session=self.session)
        server = nova.servers.find(name=server_name)
        nova.servers.add_security_group(server, security_group_name)

    def delete_instance_byId(self, instance_id):
        nova = nova_client.Client(NOVA_CLIENT_VERSION, session=self.session)
        nova.servers.delete(instance_id)

    def delete_instance_by_name(self, instance_name):
        nova = nova_client.Client(NOVA_CLIENT_VERSION,session=self.session)
        server = nova.servers.find(name=instance_name)
        nova.servers.delete(server)
