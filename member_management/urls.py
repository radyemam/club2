# C:\Users\Eng Rady\Desktop\abdallah_club\myproject\member_management\urls.py

from django.urls import path
from . import views
from .views import (
    total_subscribers, 
    edit_subscriber, 
    delete_subscriber, 
    export_subscribers_to_excel, 
    daily_revenues, 
    add_revenue,
    subscribers_overview,
    export_daily_revenues_to_excel  # إضافة الدالة الجديدة هنا
)

urlpatterns = [
    path('total_subscribers/', views.total_subscribers, name='total_subscribers'),
    path('edit_subscriber/<str:subscriber_id>/', views.edit_subscriber, name='edit_subscriber'),
    path('delete_subscriber/<str:subscriber_id>/', views.delete_subscriber, name='delete_subscriber'),
    path('export_subscribers_to_excel/', views.export_subscribers_to_excel, name='export_subscribers_to_excel'),
    path('daily_revenues/', views.daily_revenues, name='daily_revenues'),
    path('add_revenue/', views.add_revenue, name='add_revenue'),
    path('subscriber_details/<str:subscriber_id>/', views.subscriber_details, name='subscriber_details'),
    path('subscribers_overview/', views.subscribers_overview, name='subscribers_overview'),
    path('export_daily_revenues_to_excel/', views.export_daily_revenues_to_excel, name='export_daily_revenues_to_excel'),  # إضافة الرابط هنا
]
