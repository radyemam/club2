from django.urls import path
from . import views

urlpatterns = [
    # الأنماط الموجودة
    path('registration_date_report/', views.registration_date_report, name='registration_date_report'),
    path('subscription_start_report/', views.subscription_start_report, name='subscription_start_report'),
    path('subscription_end_report/', views.subscription_end_report, name='subscription_end_report'),
    path('export_registration_report_to_excel/', views.export_registration_report_to_excel, name='export_registration_report_to_excel'),
    path('export_subscription_start_report_to_excel/', views.export_subscription_start_report_to_excel, name='export_subscription_start_report_to_excel'),
    path('export_subscription_end_report_to_excel/', views.export_subscription_end_report_to_excel, name='export_subscription_end_report_to_excel'),
]
