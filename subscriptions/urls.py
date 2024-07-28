from django.urls import path
from . import views

urlpatterns = [
    path('', views.subscriber_list, name='subscriber_list'),
]
