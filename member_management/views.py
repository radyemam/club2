import json
import pandas as pd
from io import BytesIO
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, redirect
from firebase_config import db
from firebase_admin import firestore
import logging

logger = logging.getLogger(__name__)

def total_subscribers(request):
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
    for doc in docs:
        subscriber = doc.to_dict()
        subscriber['id'] = doc.id  # Adding the document ID for linking
        subscribers.append(subscriber)

    return render(request, 'member_management/subscribers_overview.html', {'subscribers': subscribers})
def subscriber_details(request, subscriber_id):
    subscriber_ref = db.collection('subscribers').document(subscriber_id)
    subscriber = subscriber_ref.get().to_dict()
    
    return render(request, 'reports/subscriber_details.html', {'subscriber': subscriber, 'subscriber_id': subscriber_id})

def subscribers_overview(request):
    subscribers_ref = db.collection('subscribers')

    from_date = request.GET.get('from_date')
    to_date = request.GET.get('to_date')
    branch = request.GET.get('branch')
    activity = request.GET.get('activity')
    search_query = request.GET.get('search')

    filters = []
    if from_date:
        filters.append(('registration_date', '>=', from_date))
    if to_date:
        filters.append(('registration_date', '<=', to_date))
    if branch:
        filters.append(('branch', '==', branch))
    if activity:
        filters.append(('activity', '==', activity))
    if search_query:
        filters.append(('name', '>=', search_query))
        filters.append(('name', '<=', search_query + '\uf8ff'))

    for field, op, value in filters:
        subscribers_ref = subscribers_ref.where(field, op, value)

    subscribers_ref = subscribers_ref.order_by('registration_date', direction=firestore.Query.DESCENDING)
    docs = subscribers_ref.stream()

    subscribers = []
    for doc in docs:
        subscriber = doc.to_dict()
        subscriber['id'] = doc.id  # Adding the document ID for linking
        subscribers.append(subscriber)

    return render(request, 'member_management/subscribers_overview.html', {'subscribers': subscribers})

def edit_subscriber(request, subscriber_id):
    if request.method == 'POST':
        subscriber_ref = db.collection('subscribers').document(subscriber_id)
        subscriber_ref.update({
            'name': request.POST.get('name'),
            'phone': request.POST.get('phone'),
            'branch': request.POST.get('branch'),
            'nationality': request.POST.get('nationality'),
            'activity': request.POST.get('activity'),
            'registration_date': request.POST.get('registration_date'),
            'amount': request.POST.get('amount'),
            'remaining': request.POST.get('remaining'),
        })
        return redirect('total_subscribers')

    subscriber_ref = db.collection('subscribers').document(subscriber_id)
    subscriber = subscriber_ref.get().to_dict()
    return render(request, 'member_management/edit_subscriber.html', {'subscriber': subscriber})

def delete_subscriber(request, subscriber_id):
    logger.info(f"Request to delete subscriber with ID: {subscriber_id}")
    try:
        # حذف المشترك من مجموعة subscribers
        subscriber_ref = db.collection('subscribers').document(subscriber_id)
        subscriber = subscriber_ref.get()
        if subscriber.exists:
            subscriber_data = subscriber.to_dict()
            subscriber_name = subscriber_data.get('name')
            subscriber_phone = subscriber_data.get('phone')
            
            # حذف المشترك من مجموعة attendance_schedules
            schedules_ref = db.collection('attendance_schedules')
            schedules = schedules_ref.where('name', '==', subscriber_name).where('phone', '==', subscriber_phone).stream()
            for schedule in schedules:
                schedule.reference.delete()
                logger.info(f"Successfully deleted schedule with ID: {schedule.id} for subscriber with name: {subscriber_name} and phone: {subscriber_phone}")

            # حذف المشترك من مجموعة subscribers
            subscriber_ref.delete()
            logger.info(f"Successfully deleted subscriber with ID: {subscriber_id}")
        else:
            logger.warning(f"Subscriber with ID: {subscriber_id} does not exist.")
    except Exception as e:
        logger.error(f"Error deleting subscriber with ID: {subscriber_id}: {e}")
    return redirect('total_subscribers')

@csrf_exempt
def export_subscribers_to_excel(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        subscribers = data.get('subscribers', [])

        df = pd.DataFrame(subscribers)

        # Use BytesIO to save the Excel file in memory
        with BytesIO() as b:
            with pd.ExcelWriter(b, engine='openpyxl') as writer:
                df.to_excel(writer, index=False, sheet_name='Subscribers')
            b.seek(0)
            response = HttpResponse(
                b.getvalue(),
                content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
            response['Content-Disposition'] = 'attachment; filename=subscribers.xlsx'
            return response

    return HttpResponse(status=400)

def add_revenue(request):
    return render(request, 'member_management/add_revenue.html')

def daily_revenues(request):
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
    for doc in docs:
        subscriber = doc.to_dict()
        subscriber['id'] = doc.id
        subscribers.append(subscriber)

    show_table = bool(from_date or to_date or branch or activity)

    return render(request, 'member_management/daily_revenues.html', {
        'subscribers': subscribers,
        'show_table': show_table,
        'from_date': from_date,
        'to_date': to_date,
        'branch': branch,
        'activity': activity,
    })

@csrf_exempt
def export_daily_revenues_to_excel(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        logger.debug('Received data: %s', data)  # Logging the received data
        subscribers = data.get('subscribers', [])
        total_amount = data.get('total_amount', 0)
        total_remaining = data.get('total_remaining', 0)
        total_paid = data.get('total_paid', 0)

        df = pd.DataFrame(subscribers)

        # Adding the total row
        total_row = pd.DataFrame([{
            '#': '',
            'رقم الاشتراك': '',
            'رقم اللاعب': '',
            'الاسم': 'الإجمالي',
            'تاريخ التسجيل': '',
            'طريقة الدفع': '',
            'اللعبة': '',
            'المستخدم': '',
            'المبلغ': total_amount,
            'المتبقي': total_remaining,
            'المدفوع': total_paid,
        }])
        df = pd.concat([df, total_row], ignore_index=True)

        # Use BytesIO to save the Excel file in memory
        with BytesIO() as b:
            with pd.ExcelWriter(b, engine='openpyxl') as writer:
                df.to_excel(writer, index=False, sheet_name='Daily Revenues')
            b.seek(0)
            response = HttpResponse(
                b.getvalue(),
                content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
            response['Content-Disposition'] = 'attachment; filename=daily_revenues.xlsx'
            return response

    return HttpResponse(status=400)
