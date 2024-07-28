from django.shortcuts import render

def daily_revenue(request):
    # من هنا يتم عرض الصفحة أو معالجة البيانات
    return render(request, 'daily_revenue/index.html')
