from datetime import datetime, timedelta
import calendar
from django.shortcuts import render, redirect
from django.urls import reverse
from firebase_config import db, storage  # قم بالاستيراد من firebase_config
from firebase_admin import firestore
from datetime import datetime, timedelta
from django.http import JsonResponse



def get_count(collection_ref, filters=None):
    if filters:
        for field, op, value in filters:
            collection_ref = collection_ref.where(field, op, value)
    return len(list(collection_ref.stream()))

def statistics_report(request):
    subscribers_ref = db.collection('subscribers').stream()
    
    total_subscribers_count = 0
    ended_subscriptions_count = 0
    active_subscriptions_count = 0
    near_expiry_subscriptions_count = 0
    renewed_subscriptions_count = 0
    remaining_amounts_count = 0
    new_subscriptions_count = 0
    
    total_amount = 0
    total_remaining = 0
    
    activity_data = {}
    
    for doc in subscribers_ref:
        subscriber = doc.to_dict()
        total_subscribers_count += 1
        
        try:
            amount = int(subscriber.get('amount', '0'))
        except ValueError:
            amount = 0
        
        try:
            remaining = int(subscriber.get('remaining', '0'))
        except ValueError:
            remaining = 0
        
        total_amount += amount
        total_remaining += remaining
        
        activity = subscriber.get('activity', 'Unknown')
        if activity not in activity_data:
            activity_data[activity] = {
                'subscribers': 0,
                'ended': 0,
                'active': 0,
                'total_amount': 0,
                'total_remaining': 0
            }
        
        activity_data[activity]['subscribers'] += 1
        activity_data[activity]['total_amount'] += amount
        activity_data[activity]['total_remaining'] += remaining
        
        expiration_date_str = subscriber.get('expiration_date')
        if expiration_date_str:
            try:
                expiration_date = datetime.strptime(expiration_date_str, '%Y-%m-%d')
                if expiration_date < datetime.now():
                    ended_subscriptions_count += 1
                    activity_data[activity]['ended'] += 1
                else:
                    active_subscriptions_count += 1
                    activity_data[activity]['active'] += 1
                    
                    if expiration_date < datetime.now() + timedelta(days=7):
                        near_expiry_subscriptions_count += 1
            except ValueError:
                pass  # تجاهل إذا لم يكن التاريخ بتنسيق صحيح
        
        registration_date_str = subscriber.get('registration_date')
        if registration_date_str:
            try:
                registration_date = datetime.strptime(registration_date_str, '%Y-%m-%d')
                if registration_date.month == datetime.now().month and registration_date.year == datetime.now().year:
                    new_subscriptions_count += 1
            except ValueError:
                pass  # تجاهل إذا لم يكن التاريخ بتنسيق صحيح

    total_paid = total_amount - total_remaining
    
    context = {
        'total_subscribers_count': total_subscribers_count,
        'ended_subscriptions_count': ended_subscriptions_count,
        'active_subscriptions_count': active_subscriptions_count,
        'near_expiry_subscriptions_count': near_expiry_subscriptions_count,
        'renewed_subscriptions_count': renewed_subscriptions_count,
        'remaining_amounts_count': remaining_amounts_count,
        'new_subscriptions_count': new_subscriptions_count,
        'total_amount': total_amount,
        'total_remaining': total_remaining,
        'total_paid': total_paid,
        'activity_data': activity_data,
    }
    
    return render(request, 'reports/statistics_report.html', context)

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

    return render(request, 'reports/total_subscribers.html', {'subscribers': subscribers})


def upload_id_document(request):
    if request.method == 'POST' and request.FILES.get('id_document'):
        id_document = request.FILES['id_document']
        
        filename = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{id_document.name}"
        bucket = storage.bucket()
        blob = bucket.blob(filename)
        
        blob.upload_from_file(id_document)
        url = blob.public_url
        
        return JsonResponse({'url': url})
    return JsonResponse({'error': 'Failed to upload document'}, status=400)

def subscriber_details(request, subscriber_id):
    subscriber_ref = db.collection('subscribers').document(subscriber_id)
    subscriber = subscriber_ref.get().to_dict()
    
    return render(request, 'reports/subscriber_details.html', {'subscriber': subscriber, 'subscriber_id': subscriber_id})

def print_form(request, subscriber_id):
    subscriber_ref = db.collection('subscribers').document(subscriber_id)
    subscriber = subscriber_ref.get().to_dict()
    return render(request, 'reports/print_form.html', {'subscriber': subscriber})

def ended_subscriptions(request):
    subscribers_ref = db.collection('subscribers')
    
    from_date = request.GET.get('from_date')
    to_date = request.GET.get('to_date')
    branch = request.GET.get('branch')
    activity = request.GET.get('activity')
    
    filters = [('expiration_date', '<=', datetime.now().strftime('%Y-%m-%d'))]  # فقط الاشتراكات التي انتهت بالفعل
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
    for doc in docs:
        subscriber = doc.to_dict()
        subscriber['id'] = doc.id  # Adding the document ID for linking
        subscribers.append(subscriber)

    return render(request, 'reports/ended_subscriptions.html', {'subscribers': subscribers})

def active_subscriptions(request):
    subscribers_ref = db.collection('subscribers')
    
    from_date = request.GET.get('from_date')
    to_date = request.GET.get('to_date')
    branch = request.GET.get('branch')
    activity = request.GET.get('activity')
    
    today = datetime.now().strftime('%Y-%m-%d')
    filters = [('expiration_date', '>', today)]  # فقط الاشتراكات التي لم تنتهي بعد
    
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
    
    subscribers_ref = subscribers_ref.order_by('expiration_date', direction=firestore.Query.ASCENDING)
    docs = subscribers_ref.stream()

    subscribers = []
    for doc in docs:
        subscriber = doc.to_dict()
        subscriber['id'] = doc.id  # Adding the document ID for linking
        subscribers.append(subscriber)

    return render(request, 'reports/active_subscriptions.html', {'subscribers': subscribers})


def near_expiry_subscriptions(request):
    subscribers_ref = db.collection('subscribers')
    
    today = datetime.now()
    next_week = today + timedelta(days=7)
    
    from_date = request.GET.get('from_date')
    to_date = request.GET.get('to_date')
    branch = request.GET.get('branch')
    activity = request.GET.get('activity')
    
    filters = [('expiration_date', '>=', today.strftime('%Y-%m-%d')),
               ('expiration_date', '<=', next_week.strftime('%Y-%m-%d'))]  # الاشتراكات التي تنتهي خلال أسبوع
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
    
    subscribers_ref = subscribers_ref.order_by('expiration_date', direction=firestore.Query.ASCENDING)
    docs = subscribers_ref.stream()

    subscribers = []
    for doc in docs:
        subscriber = doc.to_dict()
        subscriber['id'] = doc.id  # Adding the document ID for linking
        subscribers.append(subscriber)

    return render(request, 'reports/near_expiry_subscriptions.html', {'subscribers': subscribers})

def new_subscriptions(request):
    # احصل على تاريخ اليوم
    today = datetime.now()
    current_month = today.month
    current_year = today.year

    # جلب المشتركين الذين تم تسجيلهم في الشهر الحالي
    subscribers_ref = db.collection('subscribers').where('registration_date', '>=', datetime(current_year, current_month, 1).strftime('%Y-%m-%d'))
    subscribers_ref = subscribers_ref.where('registration_date', '<', datetime(current_year, current_month + 1, 1).strftime('%Y-%m-%d'))
    
    docs = subscribers_ref.stream()

    subscribers = []
    for doc in docs:
        subscriber = doc.to_dict()
        subscriber['id'] = doc.id  # إضافة 'id' إلى البيانات
        subscribers.append(subscriber)

    return render(request, 'reports/new_subscriptions.html', {'subscribers': subscribers})

def renewed_subscriptions(request):
    # بنجيب كل الاشتراكات وبنرتبها بناءً على رقم اللاعب وتاريخ الانتهاء
    subscribers_ref = db.collection('subscribers').order_by('player_number').order_by('expiration_date', direction=firestore.Query.DESCENDING)
    
    docs = subscribers_ref.stream()

    subscribers = []
    for doc in docs:
        subscriber = doc.to_dict()
        subscriber['id'] = doc.id  # إضافة 'id' إلى البيانات
        subscribers.append(subscriber)

    return render(request, 'reports/renewed_subscriptions.html', {'subscribers': subscribers})


def remaining_amounts(request):
    subscribers_ref = db.collection('subscribers')
    
    from_date = request.GET.get('from_date')
    to_date = request.GET.get('to_date')
    branch = request.GET.get('branch')
    activity = request.GET.get('activity')
    
    docs = subscribers_ref.stream()

    subscribers = []
    for doc in docs:
        subscriber = doc.to_dict()
        subscriber['id'] = doc.id  # Adding the document ID for linking
        # تحويل القيمة إلى عدد صحيح إذا كانت موجودة
        if 'remaining' in subscriber and subscriber['remaining'].isdigit() and int(subscriber['remaining']) > 0:
            # تطبيق الفلاتر الإضافية
            if from_date and subscriber.get('expiration_date') < from_date:
                continue
            if to_date and subscriber.get('expiration_date') > to_date:
                continue
            if branch and subscriber.get('branch') != branch:
                continue
            if activity and subscriber.get('activity') != activity:
                continue
            subscribers.append(subscriber)

    # Debugging: طباعة عدد الاشتراكات اللي تم جلبها
    print(f"Number of subscribers with remaining amounts: {len(subscribers)}")
    
    return render(request, 'reports/remaining_amounts.html', {'subscribers': subscribers})

def add_subscriber(request):
    if request.method == 'POST':
        player_number = request.POST.get('player_number')
        subscription_number = request.POST.get('subscription_number')
        name = request.POST.get('name')
        phone = request.POST.get('phone')
        activity = request.POST.get('activity')
        branch = request.POST.get('branch')
        registration_date = request.POST.get('registration_date')
        amount = request.POST.get('amount')
        remaining = request.POST.get('remaining')
        expiration_date = request.POST.get('expiration_date')
        guardian_phone = request.POST.get('guardian_phone')
        birth_date = request.POST.get('birth_date')
        nationality = request.POST.get('nationality')
        id_document_url = request.POST.get('id_document_url')
        number_of_sessions = request.POST.get('number_of_sessions')
        payment_method = request.POST.get('payment_method')
        
        # تحويل التواريخ من نص إلى كائنات datetime إذا لم تكن كذلك وإذا كانت غير فارغة
        registration_date = datetime.strptime(registration_date, '%Y-%m-%d') if registration_date else None
        expiration_date = datetime.strptime(expiration_date, '%Y-%m-%d') if expiration_date else None
        birth_date = datetime.strptime(birth_date, '%Y-%m-%d') if birth_date else None
        
        # Get selected days
        selected_days = request.POST.getlist('days')
        
        subscriber_data = {
            'player_number': player_number,
            'subscription_number': subscription_number,
            'name': name,
            'phone': phone,
            'activity': activity,
            'branch': branch,
            'registration_date': registration_date.strftime('%Y-%m-%d') if registration_date else None,
            'amount': amount,
            'remaining': remaining,
            'expiration_date': expiration_date.strftime('%Y-%m-%d') if expiration_date else None,
            'guardian_phone': guardian_phone,
            'birth_date': birth_date.strftime('%Y-%m-%d') if birth_date else None,
            'nationality': nationality,
            'id_document_url': id_document_url,
            'number_of_sessions': number_of_sessions,
            'payment_method': payment_method,
            'selected_days': selected_days
        }

        db.collection('subscribers').add(subscriber_data)

        # Generate attendance dates
        attendance_dates = []
        current_date = registration_date
        days_mapping = {
            'السبت': 'Saturday',
            'الأحد': 'Sunday',
            'الاثنين': 'Monday',
            'الثلاثاء': 'Tuesday',
            'الأربعاء': 'Wednesday',
            'الخميس': 'Thursday',
            'الجمعة': 'Friday'
        }
        selected_days_english = [days_mapping[day] for day in selected_days]
        
        while current_date and current_date <= expiration_date:
            if calendar.day_name[current_date.weekday()] in selected_days_english:
                attendance_dates.append(current_date.strftime('%Y-%m-%d'))
            current_date += timedelta(days=1)
        
        attendance_data = {
            'player_number': player_number,
            'subscription_number': subscription_number,
            'name': name,
            'phone': phone,
            'activity': activity,
            'branch': branch,
            'attendance_dates': attendance_dates,
            'number_of_sessions': number_of_sessions,  # Add the number of sessions here
            'attendance_days': [],
            'status': {},
            'num_of_day_attendance': 0  # Add the new field with default value 0
        }

        db.collection('attendance_schedules').add(attendance_data)

        return redirect(reverse('total_subscribers'))

    return render(request, 'reports/add_subscriber.html')
