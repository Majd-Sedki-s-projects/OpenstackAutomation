from novaclient import client as nova_client

NOVA_CLIENT_VERSION = "2.1"


class StartInstance(object):
    def __init__(self, sess):
        self.session = sess

    def start_instance(self, server_name, image, size,userdata):
        nova = nova_client.Client("2.1", session=self.session)
        flavour = nova.flavors.find(name=size)
        image = nova.images.find(name=image)
        #network = nova_client.networks.find(name="public")
        nova.servers.create(name=str(server_name), flavor=flavour, image=image,
                            userdata=userdata, #Userdata to add cloud-init file
                            nics=[{'net-id': "7dd889fc-ef10-4fb5-8c71-35738d627846"}])
        return nova
 
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
