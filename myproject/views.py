from django.shortcuts import render, redirect
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from .forms import ProfileForm

@login_required
def profile_edit(request):
    if request.method == 'POST':
        profile_form = ProfileForm(request.POST, instance=request.user)
        if profile_form.is_valid():
            profile_form.save()
            messages.success(request, 'تم تحديث الملف الشخصي بنجاح.')
            return redirect('statistics_report')
        else:
            messages.error(request, 'يرجى تصحيح الأخطاء أدناه.')
    else:
        profile_form = ProfileForm(instance=request.user)

    return render(request, 'profile_edit.html', {
        'profile_form': profile_form,
    })

def logout_view(request):
    logout(request)
    return redirect('login')
