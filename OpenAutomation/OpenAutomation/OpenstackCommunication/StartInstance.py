from novaclient import client as nova_client

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
							nics=[{'net-id': "6c9b77ff-3341-4000-8e65-1e71a720e6cb"}])
        return nova

    def add_security_to_server(self, nova, server_name, security_group_name):
        server = nova.servers.find(name=server_name)
        nova.servers.add_security_group(server, security_group_name)
