from django.http import HttpResponse, JsonResponse
from django.shortcuts import render_to_response, render
from django.views.decorators.csrf import csrf_exempt
from ..OpenstackCommunication.Authenticate import Authenticate
from ..OpenstackCommunication.StartInstance import StartInstance
from ..OpenstackCommunication.CreateRouter import CreateRouter
from ..OpenstackCommunication.CreateNetwork import CreateNetwork
from ..OpenstackCommunication.FloatingIP import FloatingIP
from ..OpenstackCommunication.ParseEdges import ParseEdges
from ..OpenstackCommunication.Utils import Utils
from ..OpenstackCommunication.CreateSubnet import CreateSubnet
from ast import literal_eval
from OpenAutomation.NetworkTopology.models import Topology, NetworkApplications
from json import dumps, loads
import os
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
    auth = Authenticate(auth="http://144.217.53.20:5000/v3", user="admin", passwd="fdc014394ad84458",
                        proj_name="admin", user_domain="default", project_domain="default")
    session = auth.start_auth()
    utilities = Utils(session=session)
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
                for device_id in node_info:
                    if device_id.get("deployed") == "false":
                        if 'vm' in device_id.get("type"):
                            print(device_id.get("label"))
                            print(edge_info)
                            edge_parser = ParseEdges(edge_info)
                            network_name = edge_parser.parse_edges(node_name=device_id.get("label"))
                            network_info = CreateNetwork(session)
                            network_id, network_exists = network_info.get_network_id(name=network_name)
                            print("network_exists: " + str(network_exists))
                            if network_exists:
                                print("Creating Instance")
                                print("Network is: " + network_id)
                                nova, status = new_instance.start_instance(server_name=device_id.get("label"),
                                                                           image="cirros", size="m1.tiny", userdata="",
                                                                           network_id=network_id)
                                if status:
                                    print("Instance Created")
                                    deployment_status["deployed_successfully"].append("true")
                                    deployment_status["device_name"].append(device_id.get("label"))
                                elif not status:
                                    print("Instance failed")
                                    deployment_status["deployed_successfully"].append("false")
                                    deployment_status["device_name"].append(device_id.get("label"))
                            elif not network_exists:
                                body = {'name': network_name, 'admin_state_up': True}
                                network_info.create_network(name=network_name, body=body)
                                network_id, network_exists = network_info.get_network_id(name=network_name)
                                print("network_id: " + network_id)
                                nova, status = new_instance.start_instance(server_name=device_id.get("label"),
                                                                           image="cirros", size="m1.small", userdata="",
                                                                           network_id=network_id)
                                if status:
                                    deployment_status["deployed_successfully"].append("true")
                                    deployment_status["device_name"].append(device_id.get("label"))
                                elif status:
                                    deployment_status["deployed_successfully"].append("false")
                                    deployment_status["device_name"].append(device_id.get("label"))
                        elif 'router' in device_id.get("type"):
                            print(device_id.get("label"))
                            new_router = CreateRouter(session)
                            ext_net = {"network_id": "fb1879a3-6ec5-4593-8b51-4de72d872f4e", "enable_snat": True}
                            body = {'name': device_id.get("label"),
                                    'external_gateway_info': ext_net
                                    }
                            neutron = new_router.create_router(body)
                        elif 'apache' in device_id.get("type"):
                            print(device_id.get("label"))
                            cloud_init = open(PROJECT_PATH + '/CloudInit/apache_cloudinit.txt')
                            edge_parser = ParseEdges(edge_info)
                            network_name = edge_parser.parse_edges(node_name=device_id.get("label"))
                            network_info = CreateNetwork(session)
                            network_id, network_exists = network_info.get_network_id(name=network_name)
                            print("network_exists: " + str(network_exists))
                            if network_exists:
                                nova, status = new_instance.start_instance(server_name=device_id.get("label"),
                                                                           image="Ubuntu 16.04 LTS", size="m1.small",
                                                                           userdata=cloud_init, network_id=network_id)
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
                                                                           image="Ubuntu 16.04 LTS", size="m1.small",
                                                                           userdata=cloud_init, network_id=network_id)
                                if status:
                                    deployment_status["deployed_successfully"].append("true")
                                    deployment_status["device_name"].append(device_id.get("label"))
                                elif not status:
                                    deployment_status["deployed_successfully"].append("false")
                                    deployment_status["device_name"].append(device_id.get("label"))
                            time.sleep(10)  # Wait to allow server to complete build (Can't assign FIP until built)
                            new_floatingip = FloatingIP(session)
                            server = new_floatingip.getServer(name=device_id.get("label"))
                            new_floatingip.assignFloatingIP(server)
                        elif 'wordpress' in device_id.get("type"):
                            print(device_id.get("label"))
                            print("project path is: " + PROJECT_PATH)
                            cloud_init = open(PROJECT_PATH + '/CloudInit/wordpress_centos6_cloudinit.txt')
                            edge_parser = ParseEdges(edge_info)
                            network_name = edge_parser.parse_edges(node_name=device_id.get("label"))
                            network_info = CreateNetwork(session)
                            network_id, network_exists = network_info.get_network_id(name=network_name)
                            print("network_exists: " + str(network_exists))
                            if network_exists:
                                nova, status = new_instance.start_instance(server_name=device_id.get("label"),
                                                                           image="Centos6", size="m1.small",
                                                                           userdata=cloud_init, network_id=network_id)
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
                                                                           image="Centos6", size="m1.small",
                                                                           userdata=cloud_init, network_id=network_id)
                                if status:
                                    deployment_status["deployed_successfully"].append("true")
                                    deployment_status["device_name"].append(device_id.get("label"))
                                elif not status:
                                    deployment_status["deployed_successfully"].append("false")
                                    deployment_status["device_name"].append(device_id.get("label"))
                            time.sleep(10)  # Wait to allow server to complete build (Can't assign FIP until built)
                            new_floatingip = FloatingIP(session)
                            server = new_floatingip.getServer(name=device_id.get("label"))
                            new_floatingip.assignFloatingIP(server)
                        elif 'network' in device_id.get("type") and not network_exists:
                            pass
                            # Currently causes issues. Don't uncomment for now.
                            # print(device_id.get("image"))
                            # new_network = CreateNetwork(session)
                            # new_subnet = CreateSubnet(session)
                            # body = {'name': device_id.get("label"), 'admin_state_up': True}
                            # name = device_id.get("label")
                            # neutron = new_network.create_network(name, body)

                            # time.sleep(5)  # WWait to allow network to be set up
                            # networks = neutron.list_networks(name=device_id.get("label"))
                            # new_network_id = networks['networks'][0]['id']
                            # subnet = {'name': device_id.get("subnetName"),
                            #          'cidr': device_id.get("subnet"),
                            #          'network_id': new_network_id,
                            #          'ip_version':'4',
                            #          'enable_dhcp': True,
                            #          'allocation_pools': [
                            #              {"start": device_id.get("dhcp_start"),
                            #               "end": device_id.get("dhcp_end")
                            #               } ]
                            #          }
                            # neutron = new_subnet.create_subnet(subnet)

                        else:
                            print("")
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

    # Get a list of topology names from MySQL DB.
    topology_name = list(Topology.objects.values_list('topology_name', flat=True))
    # Get a list of networks
    network_list = utilities.get_network_list()
    # Get a list of applications from the database.
    application_names = list(NetworkApplications.objects.values_list('application_name', flat=True))
    return render(request, "index.html", {'topology_name': topology_name, 'network_list': network_list,
                                          'application_names': application_names})
