from django.urls import path

from . import views

app_name = "lightsOutApp"
urlpatterns = [
    path("", views.tutorial, name="tutorial"),
    path("game/", views.index, name="index"),
    path("tutorial/", views.tutorial, name="tutorial"),
    path('ajax/', views.ajax_view, name='ajax_view'),
    path('reset/', views.reset_view, name='reset'),
    path('hint/', views.hint_view, name='hint'),
]
