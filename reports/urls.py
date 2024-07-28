from django.urls import path
from . import views

urlpatterns = [
    path('statistics_report/', views.statistics_report, name='statistics_report'),
    path('total_subscribers/', views.total_subscribers, name='reports_total_subscribers'),
    path('add_subscriber/', views.add_subscriber, name='add_subscriber'),
    path('subscriber_details/<str:subscriber_id>/', views.subscriber_details, name='subscriber_details'),
    path('print_form/<str:subscriber_id>/', views.print_form, name='print_form'),
    path('ended_subscriptions/', views.ended_subscriptions, name='ended_subscriptions'),
    path('active_subscriptions/', views.active_subscriptions, name='active_subscriptions'),
    path('near_expiry_subscriptions/', views.near_expiry_subscriptions, name='near_expiry_subscriptions'),
    path('new_subscriptions/', views.new_subscriptions, name='new_subscriptions'),
    path('renewed_subscriptions/', views.renewed_subscriptions, name='renewed_subscriptions'),
    path('remaining_amounts/', views.remaining_amounts, name='remaining_amounts'),
    path('upload_id_document/', views.upload_id_document, name='upload_id_document'),
]
