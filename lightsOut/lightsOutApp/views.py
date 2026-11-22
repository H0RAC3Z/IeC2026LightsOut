from django.shortcuts import render, redirect
from django.template import loader
from .models import LightsOut

# Create your views here.

from django.http import HttpResponse


def index(request):
    obj = LightsOut()
    board = obj.board
    return render(request, "lightsOutApp/index.html", { "obj" : obj , "board" : board })