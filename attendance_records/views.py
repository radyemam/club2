
from datetime import datetime, timedelta
import calendar
from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.template.loader import get_template
from django.template import TemplateDoesNotExist
from firebase_config import db
from firebase_admin import firestore
import json
import pandas as pd
from io import BytesIO

def print_attendance(request):
    try:
        template = get_template('attendance_records/attendance_print.html')
    except TemplateDoesNotExist:
        return HttpResponse("Template attendance_records/attendance_print.html does not exist")
    
    attendance_ref = db.collection('attendance_schedules')

    name = request.GET.get('name')
    activity = request.GET.get('activity')

    if name:
        attendance_ref = attendance_ref.where('name', '==', name)
    if activity:
        attendance_ref = attendance_ref.where('activity', '==', activity)

    attendance_ref = attendance_ref.order_by('name', direction=firestore.Query.ASCENDING)
    docs = attendance_ref.stream()

    subscribers = []
    for doc in docs:
        subscriber = doc.to_dict()
        subscriber['id'] = doc.id
        subscribers.append(subscriber)
    
    return render(request, 'attendance_records/attendance_print.html', {
        'subscribers': subscribers,
        'name': name,
        'activity': activity
    })

@csrf_exempt
def export_print_attendance_to_excel(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        subscribers = data.get('subscribers', [])

        df = pd.DataFrame(subscribers)

        # Use BytesIO to save the Excel file in memory
        with BytesIO() as b:
            with pd.ExcelWriter(b, engine='openpyxl') as writer:
                df.to_excel(writer, index=False, sheet_name='Print Attendance')
            b.seek(0)
            response = HttpResponse(
                b.getvalue(),
                content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
            response['Content-Disposition'] = 'attachment; filename=print_attendance.xlsx'
            return response

    return HttpResponse(status=400)

@csrf_exempt
def export_attendance_by_date_to_excel(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        attendees = data.get('attendees', [])

        df = pd.DataFrame(attendees)

        # Use BytesIO to save the Excel file in memory
        with BytesIO() as b:
            with pd.ExcelWriter(b, engine='openpyxl') as writer:
                df.to_excel(writer, index=False, sheet_name='Attendance By Date')
            b.seek(0)
            response = HttpResponse(
                b.getvalue(),
                content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
            response['Content-Disposition'] = 'attachment; filename=attendance_by_date.xlsx'
            return response

    return HttpResponse(status=400)

def attendance_by_date(request):
    selected_date = request.GET.get('from_date')

    if selected_date:
        selected_date = datetime.strptime(selected_date, '%Y-%m-%d')

        attendance_ref = db.collection('attendance_schedules').where('attendance_dates', 'array_contains', selected_date.strftime('%Y-%m-%d'))
        docs = attendance_ref.stream()

        attendees = []
        for doc in docs:
            attendee = doc.to_dict()
            attendee['number_of_sessions'] = attendee.get('number_of_sessions', '')
            attendee['status'] = attendee.get('status', {}).get(selected_date.strftime('%Y-%m-%d'), 'X')
            attendee['attendance_days'] = len(attendee.get('attendance_days', []))
            attendee['subscription_number'] = doc.id
            attendees.append(attendee)

        return render(request, 'attendance_records/attendance_by_date.html', {
            'attendees': attendees,
            'selected_date': selected_date.strftime('%Y-%m-%d')
        })

    return render(request, 'attendance_records/attendance_by_date.html', {
        'attendees': [],
        'selected_date': ''
    })

@csrf_exempt
def save_attendance_by_date(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        attendees = data.get('attendees', [])
        selected_date = data.get('selected_date')

        for attendee in attendees:
            doc_ref = db.collection('attendance_schedules').document(attendee['subscription_number'])
            doc = doc_ref.get()
            if doc.exists:
                doc_data = doc.to_dict()
                if 'status' not in doc_data:
                    doc_data['status'] = {}
                doc_data['status'][selected_date] = attendee['الحالة']
                if attendee['الحالة'] == 'حضور':
                    if 'attendance_days' not in doc_data:
                        doc_data['attendance_days'] = []
                    if selected_date not in doc_data['attendance_days']:
                        doc_data['attendance_days'].append(selected_date)
                    doc_data['num_of_day_attendance'] = len(doc_data['attendance_days'])
                doc_ref.set(doc_data, merge=True)

        return HttpResponse(status=200)

    return HttpResponse(status=400)

def today_attendance(request):
    selected_date = datetime.now().strftime('%Y-%m-%d')

    attendance_ref = db.collection('attendance_schedules').where('attendance_dates', 'array_contains', selected_date)
    docs = attendance_ref.stream()

    attendees = []
    for doc in docs:
        attendee = doc.to_dict()
        attendee['number_of_sessions'] = attendee.get('number_of_sessions', '')
        attendee['status'] = attendee.get('status', {}).get(selected_date, 'X')
        attendee['attendance_days'] = len(attendee.get('attendance_days', []))
        attendee['subscription_number'] = doc.id
        attendees.append(attendee)

    return render(request, 'attendance_records/today_attendance.html', {
        'attendees': attendees,
        'selected_date': selected_date
    })

@csrf_exempt
def save_today_attendance(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        attendees = data.get('attendees', [])
        selected_date = data.get('selected_date')

        for attendee in attendees:
            doc_ref = db.collection('attendance_schedules').document(attendee['subscription_number'])
            doc = doc_ref.get()
            if doc.exists:
                doc_data = doc.to_dict()
                if 'status' not in doc_data:
                    doc_data['status'] = {}
                doc_data['status'][selected_date] = attendee['الحالة']
                if attendee['الحالة'] == 'حضور':
                    if 'attendance_days' not in doc_data:
                        doc_data['attendance_days'] = []
                    if selected_date not in doc_data['attendance_days']:
                        doc_data['attendance_days'].append(selected_date)
                    doc_data['num_of_day_attendance'] = len(doc_data['attendance_days'])
                doc_ref.set(doc_data, merge=True)

        return HttpResponse(status=200)

    return HttpResponse(status=400)
