from keystoneauth1.identity import v3
from keystoneauth1 import session
from keystoneclient.v3 import client as keystone_client
from novaclient import client as nova_client


def start_auth():
    auth = v3.Password(auth_url="http://192.168.2.201:5000/v3", username="admin",password="adb945659bff445a",
                       project_name="admin", user_domain_id="default", project_domain_id="default")
    sess = session.Session(auth=auth)
    keystone = keystone_client.Client(session=sess)
    nova = nova_client.Client("2.1", session=sess)
    return keystone, nova, sess


def create_project(keystone):
    proj = keystone.projects.create(name="test", description="My new Project!", domain="default", enabled=True)
    return proj


def start_instance(nova, server_name, server_flavor, server_image):
    nova.servers.create(name=server_name, flavor=server_flavor, image=server_image)

if __name__ == '__main__':
    authenticate, novaclient, sess = start_auth()
    # project = create_project(authenticate)
    flav = novaclient.flavors.find(name="m1.tiny")
    image = novaclient.images.find(name="cirros")
    start_instance(novaclient, server_name="my_server",server_flavor=flav,server_image=image)