# views.py

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import ExpenseForm
import sys
import os
import json
import pandas as pd
from io import BytesIO
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from firebase_config import db
from firebase_admin import firestore
from collections import defaultdict
from datetime import datetime
import logging

# إعداد تسجيل النقاط للتحقق من الحذف
logger = logging.getLogger(__name__)

@login_required
def record(request):
    expenses = db.collection('expenses').order_by('date', direction='DESCENDING').stream()
    expenses_list = []
    for idx, expense in enumerate(expenses):
        expense_data = expense.to_dict()
        expense_data['id'] = expense.id
        expense_data['order'] = idx + 1
        expenses_list.append(expense_data)
    return render(request, 'expenses/record.html', {'expenses': expenses_list})

@login_required
def delete_record(request, expense_id):
    logger.info(f"Request to delete expense with ID: {expense_id}")
    try:
        expense_ref = db.collection('expenses').document(expense_id)
        expense_ref.delete()
        logger.info(f"Successfully deleted expense with ID: {expense_id}")
    except Exception as e:
        logger.error(f"Error deleting expense with ID: {expense_id}: {e}")
    return redirect('expense_record')


@login_required
def new_record(request):
    if request.method == 'POST':
        form = ExpenseForm(request.POST)
        if form.is_valid():
            expenses_count = len(db.collection('expenses').get())
            expense_data = {
                'item': form.cleaned_data['item'],
                'amount': form.cleaned_data['amount'],
                'date': form.cleaned_data['date'].strftime("%Y-%m-%d"),
                'expense_type': form.cleaned_data['expense_type'],
                'details': form.cleaned_data['details'],
                'user': request.user.username,
                'order': expenses_count + 1
            }
            db.collection('expenses').add(expense_data)
            return redirect('expense_record')
    else:
        form = ExpenseForm()
    return render(request, 'expenses/new_record.html', {'form': form})

@login_required
def edit_record(request, expense_id):
    expense_ref = db.collection('expenses').document(expense_id)
    expense = expense_ref.get()
    if not expense.exists:
        return redirect('expense_record')

    if request.method == 'POST':
        form = ExpenseForm(request.POST)
        if form.is_valid():
            expense_data = {
                'item': form.cleaned_data['item'],
                'amount': form.cleaned_data['amount'],
                'date': form.cleaned_data['date'].strftime("%Y-%m-%d"),
                'expense_type': form.cleaned_data['expense_type'],
                'details': form.cleaned_data['details'],
                'user': request.user.username
            }
            expense_ref.update(expense_data)
            return redirect('expense_record')
    else:
        expense_data = expense.to_dict()
        form = ExpenseForm(initial=expense_data)
    return render(request, 'expenses/edit_record.html', {'form': form, 'expense': expense_data, 'expense_id': expense_id})


def expenses_and_revenues_report(request):
    subscribers_ref = db.collection('subscribers')
    expenses_ref = db.collection('expenses')

    from_date = request.GET.get('from_date')
    to_date = request.GET.get('to_date')

    filters = []
    if from_date:
        filters.append(('registration_date', '>=', from_date))
    if to_date:
        filters.append(('registration_date', '<=', to_date))

    for field, op, value in filters:
        subscribers_ref = subscribers_ref.where(field, op, value)

    subscribers_ref = subscribers_ref.order_by('registration_date', direction=firestore.Query.ASCENDING)
    subscriber_docs = subscribers_ref.stream()

    expenses_filters = []
    if from_date:
        expenses_filters.append(('date', '>=', from_date))
    if to_date:
        expenses_filters.append(('date', '<=', to_date))

    for field, op, value in expenses_filters:
        expenses_ref = expenses_ref.where(field, op, value)

    expenses_docs = expenses_ref.stream()

    daily_data = defaultdict(lambda: {'amount': 0, 'remaining': 0, 'paid': 0, 'expenses': 0})

    for doc in subscriber_docs:
        subscriber = doc.to_dict()
        date = subscriber['registration_date']
        amount = int(subscriber.get('amount', 0))
        remaining = int(subscriber.get('remaining', 0))
        paid = amount - remaining

        daily_data[date]['amount'] += amount
        daily_data[date]['remaining'] += remaining
        daily_data[date]['paid'] += paid

    for doc in expenses_docs:
        expense = doc.to_dict()
        date = expense['date']
        amount = int(expense.get('amount', 0))
        
        if isinstance(date, datetime):
            date = date.strftime('%Y-%m-%d')

        daily_data[date]['expenses'] += amount

    aggregated_data = [{'date': date, 'amount': data['amount'], 'paid': data['paid'], 'expenses': data['expenses'], 'net': data['paid'] - data['expenses']} for date, data in daily_data.items()]
    aggregated_data = sorted(aggregated_data, key=lambda x: x['date'])

    show_table = bool(from_date or to_date)

    return render(request, 'expenses/report.html', {
        'aggregated_data': aggregated_data,
        'show_table': show_table,
        'from_date': from_date,
        'to_date': to_date,
    })

@csrf_exempt
def export_expenses_and_revenues_to_excel(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        subscribers = data.get('data', [])
        total_amount = data.get('total_amount', 0)
        total_paid = data.get('total_paid', 0)
        total_expenses = data.get('total_expenses', 0)
        total_net = data.get('total_net', 0)

        df = pd.DataFrame(subscribers)

        total_row = pd.DataFrame([{
            'تاريخ التسجيل': 'الإجمالي',
            'المبلغ': total_amount,
            'المدفوع': total_paid,
            'المصروفات': total_expenses,
            'الصافي': total_net,
        }])
        df = pd.concat([df, total_row], ignore_index=True)

        with BytesIO() as b:
            with pd.ExcelWriter(b, engine='openpyxl') as writer:
                df.to_excel(writer, index=False, sheet_name='Expenses and Revenues')
            b.seek(0)
            response = HttpResponse(
                b.getvalue(),
                content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
            response['Content-Disposition'] = 'attachment; filename=expenses_and_revenues_report.xlsx'
            return response

    return HttpResponse(status=400)
