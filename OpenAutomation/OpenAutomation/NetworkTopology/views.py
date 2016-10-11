from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.views.decorators.csrf import csrf_exempt
import ast
from ..OpenstackCommunication.Authenticate import Authenticate
from ..OpenstackCommunication.StartInstance import StartInstance


def index(request):
    return render_to_response('index.html')


@csrf_exempt
def returnjson(request):
    if request.is_ajax():
        request_data = request.body
        data = ast.literal_eval(str(request_data.decode()))
        node_info = data[0]
        edge_info = data[1]
        #Temporary Values - This would be filled in by user input later.
        auth = Authenticate(auth="http://192.168.2.201:5000/v3", user="admin", passwd="adb945659bff445a",
                            proj_name="admin", user_domain="default", project_domain="default")
        session = auth.start_auth()
        for device_id in node_info:
            if 'vm' in device_id.get("image"):
                print(device_id.get("id"))
                new_instance = StartInstance(session)
                nova = new_instance.start_instance(server_name=device_id.get("id"), image="cirros", size="m1.small")
            else:
                print("Only VM creation is currently supported")
        return HttpResponse("OK")