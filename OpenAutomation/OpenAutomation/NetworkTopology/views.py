from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.views.decorators.csrf import csrf_exempt


def index(request):
    return render_to_response('index.html')


@csrf_exempt
def returnjson(request):
    if request.is_ajax():
        request_data = request.POST
        print("Raw Data: " + str(request_data))
        return HttpResponse("OK")
