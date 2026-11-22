from django.urls import path

from . import views

app_name = "lightsOutApp"
urlpatterns = [
    path("", views.index, name="index"),
]