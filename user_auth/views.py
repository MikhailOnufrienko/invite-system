from django.conf import settings
from django.contrib import messages
from django.http import HttpRequest, HttpResponse, HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods, require_POST, require_GET

from . import service
from .models import UserProfile
from .schemas import AuthorizeUser


@require_http_methods(['GET', 'POST'])
def authorize(request: HttpRequest) -> HttpResponse:
    if request.method == 'POST':
        phone = request.POST.get('phoneInput')
        if service.check_phone_number_valid(phone):
            auth_code = service.create_auth_code()
            messages.success(request, 'Введите полученный код авторизации.')
            messages.info(request, auth_code)
            return redirect('user_auth:confirm', phone=phone)
        error = 'Телефон должен состоять из 10 цифр без пробелов. Например: 9012005050.'
        messages.error(request, error)
        return redirect('user_auth:authorize')
    return render(request, 'authorize.html', status=200)


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
            token = result['header']['Authorization']
            response =  redirect('user_auth:profile', user_id)
            response.set_cookie(
                'token', token, httponly=True, max_age=settings.TOKEN_LIFE_IN_DAYS * 86400
            )
            return response
        error = result.get('error')
        if error:
            messages.error(request, error)
            return redirect('user_auth:authorize')
    return render(request, 'confirm.html', {'phone': phone}, status=200)


@require_GET
def profile(request: HttpRequest, id: int) -> HttpResponse:
    profile = get_object_or_404(UserProfile, pk=id)
    if profile:
        result = service.get_profile(request, profile)
        error = result.get('auth_error')
        if error:
            failed_user_id = result.get('user_id')
            return HttpResponseForbidden(
                render(request, '403.html',
                        {'user_id': failed_user_id, 'error': error}, status=403)
            )
        token_error = result.get('token_error')
        if token_error:
            messages.error(request, token_error)
            return redirect('user_auth:authorize')
        context = result
        return render(request, 'profile.html', context, status=200)


@require_POST
def activate(request: HttpRequest, id: int) -> HttpResponse:
    profile = get_object_or_404(UserProfile, pk=id)
    if profile:
        invite_code = request.POST.get('inviteCode')
        result = service.activate_invite_code(profile, invite_code)
        error = result.get('error')
        context = {
            'id': profile.id,
            'phone_number': profile.phone_number,
            'invite_code': profile.invite_code,
            'activated_code': profile.activated_code,
            'users_invited': profile.users_invited
        }
        if error:
            messages.error(request, error)
            return render(request, 'profile.html', context, status=401)
        success = result.get('success')
        if success:
            messages.success(request, success)
            return render(request, 'profile.html', context, status=201)


@require_POST
def logout(request: HttpRequest) -> HttpResponse:
    success = service.leave_system(request)
    response = redirect('user_auth:authorize')
    response.content = success
    response.delete_cookie('token')
    return response
