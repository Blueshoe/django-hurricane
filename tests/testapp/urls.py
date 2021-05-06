import time

from django.http import HttpResponse
from django.urls import path


def test_view(request):
    return HttpResponse("Hello world!", status=200)


def medium_view(request):
    time.sleep(0.1)
    return HttpResponse("Hello world!", status=200)


def heavy_view(request):
    time.sleep(0.5)
    return HttpResponse("Hello world!", status=200)


urlpatterns = [
    path("", test_view),
    path("medium", medium_view),
    path("heavy", heavy_view),
]
