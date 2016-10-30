from django.http import HttpResponse, JsonResponse
from django.shortcuts import render_to_response, render
from django.views.decorators.csrf import csrf_exempt
from ..OpenstackCommunication.Authenticate import Authenticate
from ..OpenstackCommunication.StartInstance import StartInstance
from ..OpenstackCommunication.CreateRouter import CreateRouter
from ..OpenstackCommunication.CreateNetwork import CreateNetwork
from ..OpenstackCommunication.FloatingIP import FloatingIP
from ..OpenstackCommunication.ParseEdges import ParseEdges
from ast import literal_eval
from OpenAutomation.NetworkTopology.models import Topology
from json import dumps, loads
import os
import time

PROJECT_PATH = os.path.realpath(os.path.dirname(__file__))


# def index(request):
#    return render_to_response('index.html')


@csrf_exempt
def returnjson(request):
    if request.is_ajax():
        request_data = request.body
        data = literal_eval(str(request_data.decode()))
        # Temporary Values - This would be filled in by user input later.
        auth = Authenticate(auth="http://10.14.192.248:5000/v3", user="admin", passwd="24df4e1f03fe4932",
                            proj_name="admin", user_domain="default", project_domain="default")
        session = auth.start_auth()
        new_instance = StartInstance(session)
        if isinstance(data[1][0], dict):
            if data[0].get("type") == "deploy":
                node_info = data[1]
                edge_info = data[2]
                network_exists = False
                for device_id in node_info:
                    if device_id.get("deployed") == "false":
                        if 'vm' in device_id.get("type"):
                            print(device_id.get("id"))
                            print(edge_info)
                            edge_parser = ParseEdges(edge_info)
                            network_name = edge_parser.parse_edges(node_name=device_id.get("id"))
                            network_info = CreateNetwork(session)
                            network_id, network_exists = network_info.get_network_id(name=network_name)
                            print("network_exists: " + str(network_exists))
                            if network_exists:
                                nova = new_instance.start_instance(server_name=device_id.get("id"), image="cirros",
                                                                   size="m1.small", userdata="", network_id=network_id)
                            elif not network_exists:
                                body = {'name': network_name, 'admin_state_up': True}
                                network_info.create_network(name=network_name, body=body)
                                network_id, network_exists = network_info.get_network_id(name=network_name)
                                print("network_id: " + network_id)
                                nova = new_instance.start_instance(server_name=device_id.get("id"), image="cirros",
                                                                   size="m1.small", userdata="", network_id=network_id)
                        elif 'router' in device_id.get("type"):
                            print(device_id.get("id"))
                            new_router = CreateRouter(session)
                            body = {'name': device_id.get("id")}
                            neutron = new_router.create_router(body)
                        elif 'apache' in device_id.get("type"):
                            print(device_id.get("id"))
                            cloud_init = open(PROJECT_PATH + '/CloudInit/apache_cloudinit.txt')
                            edge_parser = ParseEdges(edge_info)
                            network_name = edge_parser.parse_edges(node_name=device_id.get("id"))
                            network_info = CreateNetwork(session)
                            network_id, network_exists = network_info.get_network_id(name=network_name)
                            print("network_exists: " + str(network_exists))
                            if network_exists:
                                nova = new_instance.start_instance(server_name=device_id.get("id"),
                                                                   image="Ubuntu 16.04 LTS", size="m1.tiny",
                                                                   userdata=cloud_init, network_id=network_id)
                            elif not network_exists:
                                body = {'name': network_name, 'admin_state_up': True}
                                network_info.create_network(name=network_name, body=body)
                                network_id, network_exists = network_info.get_network_id(name=network_name)
                                print("network_id: " + network_id)
                                nova = new_instance.start_instance(server_name=device_id.get("id"),
                                                                   image="Ubuntu 16.04 LTS", size="m1.tiny",
                                                                   userdata=cloud_init, network_id=network_id)
                            time.sleep(5)  # Wait to allow server to complete build (Can't assign FIP until built)
                            new_floatingip = FloatingIP(session)
                            server = new_floatingip.getServer(name=device_id.get("id"))
                            new_floatingip.assignFloatingIP(server)
                        elif 'network' in device_id.get("type") and not network_exists:
                            print(device_id.get("image"))
                            new_network = CreateNetwork(session)
                            body = {'name': device_id.get("id"), 'admin_state_up': True}
                            name = device_id.get("id")
                            neutron = new_network.create_network(name, body)
                        else:
                            print("")
                    else:
                        print("Already deployed: " + device_id.get("id"))
            elif data[0].get("action") == "save_template":
                print("Saving template attempt")
                data_struct = literal_eval(request_data.decode())
                data_struct.pop(0)
                template = Topology()
                template.topology_name = "TEMPORARY_NAME"
                # Convert to JSON before sending to database
                template.topology_json = dumps(data_struct)
                template.save()
                print("DATABASE UPDATED")
            elif data[0].get("action") == "return_topology":
                print("Attempting to return topology")
                # print("TOPOLOGY NAME IS: " + str(data[1][0].get("topology_name")))
                test_access = Topology.objects.filter(topology_name=data[1][0].get("topology_name"))
                topology_from_db = test_access[0].topology_json
                print("test print of topology_from_db " + str(topology_from_db))
                print("TOPOLOGY RETRIEVED ")
                #return render_to_response("index.html", {"topology_from_db": str(topology_from_db)},)
                return JsonResponse(topology_from_db, safe=False)
        else:
            for deleted_instance in data:
                new_instance.delete_instance_by_name(instance_name=deleted_instance)
            print("Instance removed")
    return render(request, "index.html")


