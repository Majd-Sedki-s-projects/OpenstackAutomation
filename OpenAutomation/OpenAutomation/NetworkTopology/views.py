from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.views.decorators.csrf import csrf_exempt
import ast
from json import loads


def index(request):
    return render_to_response('index.html')


@csrf_exempt
def returnjson(request):
    if request.is_ajax():
        request_data = request.body
        print(str(request_data))
        #data = ast.literal_eval(request_data.decode('utf-8'))
        #print(data[0].keys())
        return HttpResponse("OK")
