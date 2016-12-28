# OpenstackAutomation
Network Topology made with: http://visjs.org/

Adding an application to the topology
![addApp](https://i.gyazo.com/2d9b9cb926f53b23c8f655421036115c.png "Adding an application to the topology")
![addApp](https://i.gyazo.com/bc8db32edcc8f95a4949a1d8a9846aef.gif "Adding an application to the topology")


In the screenshot below, two application chains will be deployed. One will launch a single instance, and install all the requirements for Wordpress(i.e. Wordpress, MYSQL, NGINX/Apache). The other will launch two instances to setup a LAMP stack(Apache one 1 instance, MYSQL on the other). All application installation is done using ansible.
 ![addApp](https://i.gyazo.com/0027ab63c85627a5213df3c512a552e6.png "Adding an application to the topology")

All topologies can be saved to a MYSQL database and be retrieved at a later point in time. 

# Openstack Python Clients

python-openstackclient  
Project: http://docs.openstack.org/developer/python-openstackclient/  
Repo: https://github.com/openstack/python-openstackclient.git  

python-glanceclient  
Project: http://docs.openstack.org/developer/glance/  
Repo: https://github.com/openstack/python-glanceclient.git  

python-novaclient  
Project: http://docs.openstack.org/developer/nova/  
Repo: https://github.com/openstack/python-novaclient.git  

python-neutronclient  
Project: https://launchpad.net/neutron  
Repo: https://github.com/openstack/python-neutronclient.git  

python-swiftclient  
Project: http://docs.openstack.org/developer/swift/  
Repo: https://github.com/openstack/python-swiftclient.git  
