import json
import pandas as pd
from io import BytesIO
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from firebase_config import db
from firebase_admin import firestore
import logging

logger = logging.getLogger(__name__)

def registration_date_report(request):
    subscribers_ref = db.collection('subscribers')
    
    from_date = request.GET.get('from_date')
    to_date = request.GET.get('to_date')
    branch = request.GET.get('branch')
    activity = request.GET.get('activity')
    
    filters = []
    if from_date:
        filters.append(('registration_date', '>=', from_date))
    if to_date:
        filters.append(('registration_date', '<=', to_date))
    if branch:
        filters.append(('branch', '==', branch))
    if activity:
        filters.append(('activity', '==', activity))
    
    for field, op, value in filters:
        subscribers_ref = subscribers_ref.where(field, op, value)
    
    subscribers_ref = subscribers_ref.order_by('registration_date', direction=firestore.Query.DESCENDING)
    docs = subscribers_ref.stream()

    subscribers = []
    total_amount = 0.0
    total_remaining = 0.0
    for doc in docs:
        subscriber = doc.to_dict()
        subscriber['id'] = doc.id  # Adding the document ID for linking
        total_amount += float(subscriber.get('amount', 0))
        total_remaining += float(subscriber.get('remaining', 0))
        subscribers.append(subscriber)

    show_table = bool(from_date or to_date or branch or activity)

    context = {
        'subscribers': subscribers,
        'total_amount': total_amount,
        'total_remaining': total_remaining,
        'show_table': show_table,
        'from_date': from_date,
        'to_date': to_date,
        'branch': branch,
        'activity': activity,
    }

    return render(request, 'registration_reports/registration_date_report.html', context)

@csrf_exempt
def export_registration_report_to_excel(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            logger.debug('Received data: %s', data)  # التحقق من البيانات
            subscribers = data.get('subscribers', [])
            total_amount = data.get('total_amount', 0)
            total_remaining = data.get('total_remaining', 0)

            df = pd.DataFrame(subscribers)

            # Adding the total row
            total_row = pd.DataFrame([{
                '#': '',
                'الاسم': 'الإجمالي',
                'الجوال': '',
                'اللعبة': '',
                'تاريخ التسجيل': '',
                'المبلغ': total_amount,
                'المتبقي': total_remaining,
                'الاشتراكات': '',
            }])
            df = pd.concat([df, total_row], ignore_index=True)

            # Use BytesIO to save the Excel file in memory
            with BytesIO() as b:
                with pd.ExcelWriter(b, engine='openpyxl') as writer:
                    df.to_excel(writer, index=False, sheet_name='Registration Report')
                b.seek(0)
                response = HttpResponse(
                    b.getvalue(),
                    content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                )
                response['Content-Disposition'] = 'attachment; filename=registration_report.xlsx'
                return response
        except Exception as e:
            logger.error("Error exporting to Excel: %s", e)
            return HttpResponse(status=500)

    return HttpResponse(status=400)

def subscription_start_report(request):
    subscribers_ref = db.collection('subscribers')
    
    from_date = request.GET.get('from_date')
    to_date = request.GET.get('to_date')
    branch = request.GET.get('branch')
    activity = request.GET.get('activity')
    
    filters = []
    if from_date:
        filters.append(('registration_date', '>=', from_date))
    if to_date:
        filters.append(('registration_date', '<=', to_date))
    if branch:
        filters.append(('branch', '==', branch))
    if activity:
        filters.append(('activity', '==', activity))
    
    for field, op, value in filters:
        subscribers_ref = subscribers_ref.where(field, op, value)
    
    subscribers_ref = subscribers_ref.order_by('registration_date', direction=firestore.Query.DESCENDING)
    docs = subscribers_ref.stream()

    subscribers = []
    total_amount = 0.0
    total_remaining = 0.0
    for doc in docs:
        subscriber = doc.to_dict()
        subscriber['id'] = doc.id  # Adding the document ID for linking
        total_amount += float(subscriber.get('amount', 0))
        total_remaining += float(subscriber.get('remaining', 0))
        subscribers.append(subscriber)

    show_table = bool(from_date or to_date or branch or activity)

    context = {
        'subscribers': subscribers,
        'total_amount': total_amount,
        'total_remaining': total_remaining,
        'show_table': show_table,
        'from_date': from_date,
        'to_date': to_date,
        'branch': branch,
        'activity': activity,
    }

    return render(request, 'registration_reports/subscription_start_report.html', context)

@csrf_exempt
def export_subscription_start_report_to_excel(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            logger.debug('Received data: %s', data)  # التحقق من البيانات
            subscribers = data.get('subscribers', [])
            total_amount = data.get('total_amount', 0)
            total_remaining = data.get('total_remaining', 0)

            df = pd.DataFrame(subscribers)

            # Adding the total row
            total_row = pd.DataFrame([{
                '#': '',
                'الاسم': 'الإجمالي',
                'الجوال': '',
                'اللعبة': '',
                'تاريخ التسجيل': '',
                'المبلغ': total_amount,
                'المتبقي': total_remaining,
                'الاشتراكات': '',
            }])
            df = pd.concat([df, total_row], ignore_index=True)

            # Use BytesIO to save the Excel file in memory
            with BytesIO() as b:
                with pd.ExcelWriter(b, engine='openpyxl') as writer:
                    df.to_excel(writer, index=False, sheet_name='Subscription Start Report')
                b.seek(0)
                response = HttpResponse(
                    b.getvalue(),
                    content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                )
                response['Content-Disposition'] = 'attachment; filename=subscription_start_report.xlsx'
                return response
        except Exception as e:
            logger.error("Error exporting to Excel: %s", e)
            return HttpResponse(status=500)

    return HttpResponse(status=400)

def subscription_end_report(request):
    subscribers_ref = db.collection('subscribers')
    
    from_date = request.GET.get('from_date')
    to_date = request.GET.get('to_date')
    branch = request.GET.get('branch')
    activity = request.GET.get('activity')
    
    filters = []
    if from_date:
        filters.append(('expiration_date', '>=', from_date))
    if to_date:
        filters.append(('expiration_date', '<=', to_date))
    if branch:
        filters.append(('branch', '==', branch))
    if activity:
        filters.append(('activity', '==', activity))
    
    for field, op, value in filters:
        subscribers_ref = subscribers_ref.where(field, op, value)
    
    subscribers_ref = subscribers_ref.order_by('expiration_date', direction=firestore.Query.DESCENDING)
    docs = subscribers_ref.stream()

    subscribers = []
    total_amount = 0.0
    total_remaining = 0.0
    for doc in docs:
        subscriber = doc.to_dict()
        subscriber['id'] = doc.id  # Adding the document ID for linking
        subscriber['expiration_date'] = subscriber.get('expiration_date')  # تعديل هنا
        total_amount += float(subscriber.get('amount', 0))
        total_remaining += float(subscriber.get('remaining', 0))
        subscribers.append(subscriber)

    show_table = bool(from_date or to_date or branch or activity)

    context = {
        'subscribers': subscribers,
        'total_amount': total_amount,
        'total_remaining': total_remaining,
        'show_table': show_table,
        'from_date': from_date,
        'to_date': to_date,
        'branch': branch,
        'activity': activity,
    }

    return render(request, 'registration_reports/subscription_end_report.html', context)

@csrf_exempt
def export_subscription_end_report_to_excel(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            logger.debug('Received data: %s', data)  # التحقق من البيانات
            subscribers = data.get('subscribers', [])
            total_amount = data.get('total_amount', 0)
            total_remaining = data.get('total_remaining', 0)

            df = pd.DataFrame(subscribers)

            # Adding the total row
            total_row = pd.DataFrame([{
                '#': '',
                'الاسم': 'الإجمالي',
                'الجوال': '',
                'اللعبة': '',
                'تاريخ الانتهاء': '',
                'المبلغ': total_amount,
                'المتبقي': total_remaining,
                'الاشتراكات': '',
            }])
            df = pd.concat([df, total_row], ignore_index=True)

            # Use BytesIO to save the Excel file in memory
            with BytesIO() as b:
                with pd.ExcelWriter(b, engine='openpyxl') as writer:
                    df.to_excel(writer, index=False, sheet_name='Subscription End Report')
                b.seek(0)
                response = HttpResponse(
                    b.getvalue(),
                    content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                )
                response['Content-Disposition'] = 'attachment; filename=subscription_end_report.xlsx'
                return response
        except Exception as e:
            logger.error("Error exporting to Excel: %s", e)
            return HttpResponse(status=500)

    return HttpResponse(status=400)
