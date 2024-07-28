from django.urls import path
from . import views

urlpatterns = [
    path('', views.daily_revenue, name='daily_revenue'),
]
