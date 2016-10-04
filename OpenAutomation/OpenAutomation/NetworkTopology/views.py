from django.http import HttpResponse
from django.shortcuts import render_to_response


def index(request):
    #return HttpResponse("Hello, world!")
    return render_to_response('index.html')
