from django.http import HttpResponse, JsonResponse
from django.shortcuts import render_to_response, render
from django.views.decorators.csrf import csrf_exempt
from ..OpenstackCommunication.Authenticate import Authenticate
from ..OpenstackCommunication.StartInstance import StartInstance
from ..OpenstackCommunication.CreateRouter import CreateRouter
from ..OpenstackCommunication.CreateNetwork import CreateNetwork
from ..OpenstackCommunication.FloatingIP import FloatingIP
from ..OpenstackCommunication.ParseEdges import ParseEdges
from ..OpenstackCommunication.GlanceCommunication import GlanceCommunication
from ..OpenstackCommunication.Utils import Utils
from ..OpenstackCommunication.CreateSubnet import CreateSubnet
from ast import literal_eval
from .models import Topology, NetworkApplications
from .forms import ConfigurationForm
from json import dumps, loads
import os
from fileinput import FileInput
import time
import json

PROJECT_PATH = os.path.realpath(os.path.dirname(__file__))


def home(request):
    return HttpResponse("Home Page")


def admin(request):
    return render(request, "admin.html")


def contact(request):
    return render(request, "contact.html")


@csrf_exempt
def network_topology(request):

    # Initial Authentication with Openstack
    auth = Authenticate(auth="http://10.14.192.248:5000/v3", user="admin", passwd="24df4e1f03fe4932",
                        proj_name="admin", user_domain="default", project_domain="default")
    session = auth.start_auth()
    utilities = Utils(session=session)
    glance = GlanceCommunication(session)
    completed_groups = []

    if request.is_ajax():
        request_data = request.body
        data = literal_eval(str(request_data.decode()))
        # Temporary Values - This would be filled in by user input later.
        new_instance = StartInstance(session)
        deployment_status = {"deployed_successfully": [], "device_name": []}

        if isinstance(data[1][0], dict):
            if data[0].get("type") == "deploy":
                node_info = data[1]
                edge_info = data[2]
                network_exists = False
                default_router="7a92ad72-272d-4f0b-9c8f-36cc2c1071db"

                for device_id in node_info:
                    if device_id.get("group") in completed_groups:
                        print("Group already deployed")
                    else:
                        if device_id.get("deployed") == "false":
                            if device_id.get("type") == 'vm':
                                num_vms = device_id.get("numVMs")
                                
                                # num_vms is used to determine how many VMs will be used to deploy a new application
                                if num_vms == 1:
                                    app_name = device_id.get("application")
                                    os_name = loads(NetworkApplications.objects.values('application_os').filter(
                                        application_name=app_name)[0]["application_os"])
                                    cloud_init = open(PROJECT_PATH + '/CloudInit/' + app_name + '_single.txt')
                                    edge_parser = ParseEdges(edge_info)
                                    network_name = edge_parser.parse_edges(node_name=device_id.get("label"))
                                    network_info = CreateNetwork(session)
                                    network_id, network_exists = network_info.get_network_id(name=network_name)
                                    print("network_exists: " + str(network_exists))
                                    if network_exists:
                                        nova, status = new_instance.start_instance(server_name=device_id.get("label"),
                                                                                   image=os_name, size="m1.small",
                                                                                   userdata=cloud_init,
                                                                                   network_id=network_id)
                                        if status:
                                            deployment_status["deployed_successfully"].append("true")
                                            deployment_status["device_name"].append(device_id.get("label"))
                                        elif not status:
                                            deployment_status["deployed_successfully"].append("false")
                                            deployment_status["device_name"].append(device_id.get("label"))
                                    elif not network_exists:
                                        body = {'name': network_name, 'admin_state_up': True}
                                        network_info.create_network(name=network_name, body=body)
                                        network_id, network_exists = network_info.get_network_id(name=network_name)
                                        print("network_id: " + network_id)
                                        nova, status = new_instance.start_instance(server_name=device_id.get("label"),
                                                                                   image=os_name, size="m1.small",
                                                                                   userdata=cloud_init,
                                                                                   network_id=network_id)
                                        if status:
                                            deployment_status["deployed_successfully"].append("true")
                                            deployment_status["device_name"].append(device_id.get("label"))
                                        elif not status:
                                            deployment_status["deployed_successfully"].append("false")
                                            deployment_status["device_name"].append(device_id.get("label"))
                                    new_floatingip = FloatingIP(session)
                                    server = new_floatingip.getServer(name=device_id.get("label"))
                                    new_floatingip.assignFloatingIP(server)
                                    
                                elif num_vms > 1:
                                    started_instances = []
                                    completed_groups.append(device_id.get("group"))
                                    group_data = utilities.find_group(node_info, device_id.get("group"))
                                    ansible_server = group_data.pop(0)
                                    print("GROUP DATA " + str(len(group_data)))
                                    cloud_init = open(PROJECT_PATH + '/CloudInit/BASE_CONFIG.txt')
                                    # Start all but one instance
                                    for group_nodes in group_data:
                                        app_name = group_nodes.get("application")
                                        os_name = loads(NetworkApplications.objects.values('application_os').filter(
                                            application_name=app_name)[0]["application_os"])
                                        edge_parser = ParseEdges(edge_info)
                                        network_name = edge_parser.parse_edges(node_name=group_nodes.get("label"))
                                        network_info = CreateNetwork(session)
                                        network_id, network_exists = network_info.get_network_id(name=network_name)
                                        print("network_exists: " + str(network_exists))
                                        if network_exists:
                                            nova, status = new_instance.start_instance(server_name=group_nodes.get("label"),
                                                                                       image=os_name, size="m1.small",
                                                                                       userdata=cloud_init, network_id=network_id)
                                            if status:
                                                deployment_status["deployed_successfully"].append("true")
                                                deployment_status["device_name"].append(group_nodes.get("label"))
                                            elif not status:
                                                deployment_status["deployed_successfully"].append("false")
                                                deployment_status["device_name"].append(group_nodes.get("label"))
                                        elif not network_exists:
                                            body = {'name': network_name, 'admin_state_up': True}
                                            network_info.create_network(name=network_name, body=body)
                                            network_id, network_exists = network_info.get_network_id(name=network_name)
                                            print("network_id: " + network_id)
                                            nova, status = new_instance.start_instance(server_name=group_nodes.get("label"),
                                                                                       image=os_name, size="m1.small",
                                                                                       userdata=cloud_init, network_id=network_id)
                                            if status:
                                                deployment_status["deployed_successfully"].append("true")
                                                deployment_status["device_name"].append(group_nodes.get("label"))
                                            elif not status:
                                                deployment_status["deployed_successfully"].append("false")
                                                deployment_status["device_name"].append(group_nodes.get("label"))
                                        started_instances.append(group_nodes.get("label"))
                                        new_floatingip = FloatingIP(session)
                                        server = new_floatingip.getServer(name=group_nodes.get("label"))
                                        new_floatingip.assignFloatingIP(server)
                                    print("Started Instances " + str(started_instances))
                                    server_ip = new_instance.get_server_ip(started_instances, network_name)
                                    print("SERVER IP " + str(server_ip))

                                    # BUILD FINAL SERVER - SEND UPDATED CONFIG TO IT.
                                    final_app_name = ansible_server.get("application")
                                    final_os_name = loads(NetworkApplications.objects.values('application_os').filter(
                                            application_name=final_app_name)[0]["application_os"])
                                    cloud_init = PROJECT_PATH + '/CloudInit/' + final_app_name + '.txt'
                                    count = 0
                                    with open(cloud_init, 'r') as file:
                                        old_file_data = file.read()
                                        new_file_data = old_file_data
                                        for ip in server_ip:
                                            for line in new_file_data.split('\n'):
                                                if 'IP_REPLACEMENT_IP' in line:
                                                    count += 1
                                                    text_to_replace = 'IP_REPLACEMENT_IP' + str(count)
                                                    new_line = line.replace(text_to_replace, ip)
                                                    new_file_data = new_file_data.replace(line, new_line)
                                                    break
                                    with open(cloud_init, 'w') as file:
                                        file.write(new_file_data)
                                    cloud_init = open(PROJECT_PATH + '/CloudInit/' + final_app_name + '.txt')
                                    edge_parser = ParseEdges(edge_info)
                                    network_name = edge_parser.parse_edges(node_name=ansible_server.get("label"))
                                    network_info = CreateNetwork(session)
                                    network_id, network_exists = network_info.get_network_id(name=network_name)
                                    print("network_exists: " + str(network_exists))
                                    if network_exists:
                                        nova, status = new_instance.start_instance(server_name=ansible_server.get("label"),
                                                                                   image=final_os_name, size="m1.small",
                                                                                   userdata=cloud_init, network_id=network_id)
                                        if status:
                                            deployment_status["deployed_successfully"].append("true")
                                            deployment_status["device_name"].append(ansible_server.get("label"))
                                        elif not status:
                                            deployment_status["deployed_successfully"].append("false")
                                            deployment_status["device_name"].append(ansible_server.get("label"))
                                    elif not network_exists:
                                        body = {'name': network_name, 'admin_state_up': True}
                                        network_info.create_network(name=network_name, body=body)
                                        network_id, network_exists = network_info.get_network_id(name=network_name)
                                        print("network_id: " + network_id)
                                        nova, status = new_instance.start_instance(server_name=ansible_server.get("label"),
                                                                                   image=final_os_name, size="m1.small",
                                                                                   userdata=cloud_init, network_id=network_id)
                                        if status:
                                            deployment_status["deployed_successfully"].append("true")
                                            deployment_status["device_name"].append(ansible_server.get("label"))
                                        elif not status:
                                            deployment_status["deployed_successfully"].append("false")
                                            deployment_status["device_name"].append(ansible_server.get("label"))
                                    started_instances.append(ansible_server.get("label"))
                                    new_floatingip = FloatingIP(session)
                                    server = new_floatingip.getServer(name=ansible_server.get("label"))
                                    new_floatingip.assignFloatingIP(server)
                                cloud_init = PROJECT_PATH + '/CloudInit/' + final_app_name + '.txt'
                                with open(cloud_init, 'w') as file:
                                    file.write(old_file_data)
                            elif device_id.get("type") == 'router':

                                if device_id.get("label") not in utilities.get_router_list():
                                    print("Spawning router: " + device_id.get("label"))
                                    new_router = CreateRouter(session)
                                    ext_net = {"network_id": "7a92ad72-272d-4f0b-9c8f-36cc2c1071db", "enable_snat": True}
                                    body = {'name': device_id.get("label"),
                                            'external_gateway_info': ext_net
                                            }
                                    neutron = new_router.create_router(body)
                                else:
                                    print("Router exists. Moving on.")
                            elif 'network' in device_id.get("type"):

                                if device_id.get("label") not in utilities.get_network_list():

                                     print("Spawning network: " + device_id.get("label"))
                                     new_network = CreateNetwork(session)
                                     new_subnet = CreateSubnet(session)
                                     body = {'name': device_id.get("label"), 'admin_state_up': True}
                                     name = device_id.get("label")
                                     neutron = new_network.create_network(name, body)

                                     time.sleep(5)  # *Wait to allow network to be set up
                                     networks = neutron.list_networks(name=device_id.get("label"))
                                     new_network_id = networks['networks'][0]['id']
                                     subnet = {'name': device_id.get("subnetName"),
                                             'cidr': device_id.get("subnet"),
                                            # 'dns_nameservers':'8.8.8.8',
                                             'network_id': new_network_id,
                                             'ip_version':'4',
                                             'enable_dhcp': True,
                                              'allocation_pools': [
                                                 {"start": device_id.get("dhcp_start"),
                                                  "end": device_id.get("dhcp_end")
                                                  } ]
                                             }
                                     neutron = new_subnet.create_subnet(subnet)

                                     edge_parser = ParseEdges(edge_info)
                                     router_info = CreateRouter(session)
                                     subnet_info = CreateNetwork(session)
                                     connected_router = edge_parser.parse_from_to(node_name=device_id.get("label"))
                                     connected_router_id = router_info.get_router_id(name=connected_router)
                                     print("Connected router ID: " + connected_router_id)

                                     connected_subnet_id = subnet_info.get_subnet_id(name=device_id.get("subnetName"))
                                     print("Connected subnet ID: " + connected_subnet_id)

                                     router_interface = {'subnet_id': connected_subnet_id}

                                     if connected_router in utilities.get_router_list():
                                         print("Router found. Connecting to network as gateway.")
                                         neutron.add_interface_router(connected_router_id, router_interface) #Note to self: fix pls
                                     else:
                                         print("No router found, connecting to default router.")
                                         neutron.add_interface_router(default_router, router_interface)
                                else:
                                    print("Network already exists. Moving on.")
                                    pass
                        else:
                            print("Already deployed: " + device_id.get("label"))
                return JsonResponse(deployment_status, safe=False)
            elif data[0].get("action") == "save_template":
                print("Saving template attempt")
                topology_data = literal_eval(request_data.decode())
                template = Topology()
                template.topology_name = topology_data[0].get("topology_name")
                topology_data.pop(0)
                # Convert to JSON before sending to database
                template.topology_json = dumps(topology_data)
                template.save()
                print("DATABASE UPDATED")
            elif data[0].get("action") == "return_topology":
                print("Attempting to return topology")
                db_access_with_topology_name = Topology.objects.filter(topology_name=data[1][0].get("topology_name"))
                topology_from_db = db_access_with_topology_name[0].topology_json
                print("test print of topology_from_db " + str(topology_from_db))
                print("TOPOLOGY RETRIEVED ")
                return JsonResponse(topology_from_db, safe=False)
            elif data[0].get("action") == "delete_template":
                Topology.objects.filter(topology_name=data[1][0].get("topology_name")).delete()
                print("Topology removed")
            elif data[0].get("action") == "teardown":
                print(data[0])
                nodes_to_remove = literal_eval(data[1][0].get("removed_nodes"))
                for deleted_instance in nodes_to_remove:
                    print("Deleted: " + deleted_instance)
                    new_instance.delete_instance_by_name(instance_name=deleted_instance)
                print("Instances removed")
            elif data[0].get("action") == "add_application":
                new_application = NetworkApplications()
                print("DATA IS: " + str(data))
                application_data = data.pop(1)
                application_data = literal_eval(application_data[0]["application_info"])
                new_application.application_name = application_data[0]
                new_application.application_requirements = dumps(application_data[1].split(','))
                print("APP IS: " + str(application_data))
                new_application.application_os = dumps((application_data[2]))
                new_application.save()
                print("ADDED NEW APPLICATION TO DB")
            elif data[0].get("action") == "remove_application":
                application_data = data.pop(1)
                application_name = literal_eval(application_data[0]["application_info"])
                print(application_name)
                NetworkApplications.objects.filter(application_name=application_name).delete()
                print("APPLICATION DELETED")

    # Get a list of topology names from MySQL DB.
    topology_name = list(Topology.objects.values_list('topology_name', flat=True))
    # Get a list of networks
    network_list = utilities.get_network_list()
    # Get a list of applications from the database.
    application_names = list(NetworkApplications.objects.values_list('application_name', flat=True))
    application_reqs = list(NetworkApplications.objects.values_list('application_requirements', flat=True))
    # application_os = list(NetworkApplications.objects.values_list('application_os', flat=True))
    form = ConfigurationForm()
    # Get image list
    image_list = glance.get_image_list()
    return render(request, "index.html", {'topology_name': topology_name, 'network_list': network_list,
                                          'application_names': application_names, 'application_reqs': application_reqs,
                                          'image_list': image_list, 'form': form})
