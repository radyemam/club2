from django.urls import path
from . import views

urlpatterns = [
    path('attendance_print/', views.print_attendance, name='attendance_print'),
    path('attendance_by_date/', views.attendance_by_date, name='attendance_by_date'),
    path('today_attendance/', views.today_attendance, name='today_attendance'),
    path('export_print_attendance_to_excel/', views.export_print_attendance_to_excel, name='export_print_attendance_to_excel'),
    path('export_attendance_by_date_to_excel/', views.export_attendance_by_date_to_excel, name='export_attendance_by_date_to_excel'),  # إضافة جديدة
    path('save_attendance_by_date/', views.save_attendance_by_date, name='save_attendance_by_date'),  # إضافة جديدة
    path('attendance_records/today_attendance/', views.today_attendance, name='today_attendance'),
    path('attendance_records/save_today_attendance/', views.save_today_attendance, name='save_today_attendance'),
]
