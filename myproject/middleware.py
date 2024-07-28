from django.shortcuts import redirect
from django.urls import resolve

class LoginRequiredMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # المسارات المستثناة من تسجيل الدخول
        exempt_urls = [
            'login',  # اسم النمط لصفحة تسجيل الدخول
            'logout',  # اسم النمط لصفحة تسجيل الخروج
        ]

        # احصل على اسم النمط الحالي
        current_url_name = resolve(request.path_info).url_name

        # تحقق إذا كان المسار يبدأ بـ /admin/ أو إذا كان المسار من ضمن المستثنيات
        if not request.user.is_authenticated and (request.path.startswith('/admin/') or current_url_name not in exempt_urls):
            return redirect('login')

        response = self.get_response(request)
        return response
