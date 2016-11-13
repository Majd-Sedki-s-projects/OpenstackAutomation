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
from ast import literal_eval
from OpenAutomation.NetworkTopology.models import Topology
from json import dumps, loads
import os
import time

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
                    if device_id.get("deployed") == "true":
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
                            body = {'name': device_id.get("label")}
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
                                                                   image="Ubuntu-16", size="m1.small",
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
                                                                   image="Ubuntu-16", size="m1.small",
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
                                                                   image="CentOS6", size="m1.small",
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
                                                                   image="CentOS6", size="m1.small",
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
                            #Currently causes issues. Don't uncomment for now.
                            #print(device_id.get("image"))
                            #new_network = CreateNetwork(session)
                            #body = {'name': device_id.get("label"), 'admin_state_up': True}
                            #name = device_id.get("label")
                            #neutron = new_network.create_network(name, body)
                        else:
                            print("")
                    else:
                        print("Already deployed: " + device_id.get("label"))
                return JsonResponse(deployment_status, safe=False)
            elif data[0].get("action") == "save_template":
                print("Saving template attempt")
                data_struct = literal_eval(request_data.decode())
                template = Topology()
                template.topology_name = data_struct[0].get("topology_name")
                data_struct.pop(0)
                # Convert to JSON before sending to database
                template.topology_json = dumps(data_struct)
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
        else:
            for deleted_instance in data:
                new_instance.delete_instance_by_name(instance_name=deleted_instance)
            print("Instance removed")

    # Get a list of topology names from MySQL DB.
    topology_name = list(Topology.objects.values_list('topology_name', flat=True))
    # Get a list of networks
    network_list = utilities.get_network_list()
    return render(request, "index.html", {'topology_name': topology_name, 'network_list': network_list})
