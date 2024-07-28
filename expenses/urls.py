# urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('record/', views.record, name='expense_record'),
    path('new_record/', views.new_record, name='new_record'),
    path('edit_record/<str:expense_id>/', views.edit_record, name='edit_record'),
    path('delete_record/<str:expense_id>/', views.delete_record, name='delete_record'),
    path('expenses_and_revenues_report/', views.expenses_and_revenues_report, name='expenses_and_revenues_report'),  # تأكد من أن هذا السطر موجود
    path('export_expenses_and_revenues_to_excel/', views.export_expenses_and_revenues_to_excel, name='export_expenses_and_revenues_to_excel'),
]
