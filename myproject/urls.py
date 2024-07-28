from django.contrib import admin
from django.urls import path, include
from . import views  # تأكد من استيراد views بشكل صحيح

urlpatterns = [
    path('admin/', admin.site.urls),
    path('expenses/', include('expenses.urls')),
    path('daily_revenue/', include('daily_revenue.urls')),
    path('manage_subscribers/', include('manage_subscribers.urls')),
    path('registration_reports/', include('registration_reports.urls')),
    path('subscriptions/', include('subscriptions.urls')),
    path('reports/', include('reports.urls')),  # إضافة هذا السطر لتضمين URLs لفولدر reports
    path('member_management/', include('member_management.urls')),
    path('attendance_records/', include('attendance_records.urls')),
    path('accounts/', include('django.contrib.auth.urls')),  
    path('logout/', views.logout_view, name='logout'),
    path('profile/edit/', views.profile_edit, name='profile_edit'),

]
