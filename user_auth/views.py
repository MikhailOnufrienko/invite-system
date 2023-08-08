from django.conf import settings
from django.contrib import messages
from django.http import HttpRequest, HttpResponse, HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods, require_POST, require_GET

from . import service
from .schemas import AuthorizeUser


@require_http_methods(['GET', 'POST'])
def authorize(request: HttpRequest) -> HttpResponse:
    if request.method == 'POST':
        auth_code = service.create_auth_code()
        messages.success(request, 'Введите полученный код авторизации.')
        messages.info(request, auth_code)
        phone = request.POST.get('phoneInput')
        return redirect('user_auth:confirm', phone=phone)
    return render(request, 'authorize.html')


@require_http_methods(['GET', 'POST'])
def confirm(request: HttpRequest, phone: str) -> HttpResponse:
    if request.method == 'POST':
        user = AuthorizeUser(
            phone_number=phone,
            auth_code=request.POST.get('auth_code')
        )
        result: dict = service.authorize_user(user.phone_number, user.auth_code)
        success = result.get('success')
        if success:
            user_id = result.get('user_id')
            return redirect('user_auth:profile', user_id)
        error = result.get('error')
        if error:
            messages.error(request, error)
            return redirect('user_auth:authorize')
    return render(request, 'confirm.html', {'phone': phone})


def profile(request: HttpRequest, id: int) -> HttpResponse:
    return render(request, 'profile.html')