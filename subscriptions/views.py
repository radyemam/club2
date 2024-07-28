from django.shortcuts import render
from .models import Subscriber

def subscriber_list(request):
    subscribers = Subscriber.objects.all()
    return render(request, 'registrations/subscriber_list.html', {'subscribers': subscribers})

def expenses_record(request):
    return render(request, 'expenses/record.html')

def expenses_report(request):
    return render(request, 'expenses/report.html')

def manage_subscribers(request):
    return render(request, 'manage_subscribers/index.html')

def daily_revenue(request):
    return render(request, 'daily_revenue/index.html')

def registration_reports(request):
    return render(request, 'registration_reports/index.html')
