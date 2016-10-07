from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.views.decorators.csrf import csrf_exempt
import ast
from ..OpenstackCommunication.Authenticate import Authenticate
from novaclient import client as nova_client


def index(request):
    return render_to_response('index.html')


@csrf_exempt
def returnjson(request):
    if request.is_ajax():
        request_data = request.body
        test = str(request_data.decode())
        data = ast.literal_eval(test)
        node_info = data[0]
        edge_info = data[1]
        #Temporary Values - This would be filled in by user input later.
        test = Authenticate(auth="http://192.168.2.201:5000/v3", user="admin", passwd="adb945659bff445a",
                       proj_name="admin", user_domain="default", project_domain="default")
        session = test.start_auth()
        for device_id in node_info:
            print(device_id.get("id"))
            start_instance(session, device_id.get("id"))
        return HttpResponse("OK")


def start_instance(session,server_name):
    nova = nova_client.Client("2.1", session=session)
    flavour = nova.flavors.find(name="m1.tiny")
    image = nova.images.find(name="cirros")
    nova.servers.create(name=str(server_name), flavor=flavour, image=image)
