from django.shortcuts import render
from .models import Subscriber

def subscriber_list(request):
    subscribers = Subscriber.objects.all()
    return render(request, 'subscriber_list.html', {'subscribers': subscribers})
