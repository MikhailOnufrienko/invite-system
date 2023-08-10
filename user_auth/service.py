import random
import re
import string

from django.http import HttpRequest
from jose import JWTError

from . import token_service
from .models import UserProfile


auth_code = ''


def check_phone_number_valid(value: str) -> bool:
    pattern = r'^\d{10}$'
    if not re.match(pattern, value):
        return False
    return True


def create_auth_code() -> str:
    characters = string.digits
    code_length = 4
    global auth_code
    auth_code = ''.join(random.choice(characters) for _ in range(code_length))
    return auth_code


def authorize_user(phone_number: str, code: str) -> dict:
    if code == auth_code:
        if check_phone_not_exists(phone_number):
            invite_code = create_invite_code()
            save_user_to_database(phone_number, invite_code)
        profile = UserProfile.objects.get(phone_number=phone_number)
        token = token_service.generate_tokens(profile.id, phone_number)
        success = 'Вы авторизованы.'
        header = {'Authorization': token}
        return {'success': success, 'header': header, 'user_id': profile.id}
    return {'error': 'Вы ввели неверный код. Попробуйте снова.'}
    

def check_phone_not_exists(phone_number: str) -> bool:
    try:
        profile = UserProfile.objects.get(phone_number=phone_number)
        if profile:
            return False
    except UserProfile.DoesNotExist:
        return True
    

def create_invite_code() -> str:
    characters = string.digits + string.ascii_letters
    code_length = 6
    return ''.join(random.choice(characters) for _ in range(code_length))

    
def save_user_to_database(phone_number: str, invite: str) -> None:
    UserProfile.objects.create(
        phone_number=phone_number,
        invite_code=invite
    )


def leave_system(request: HttpRequest) -> str:
        token = request.COOKIES.get('token')
        token_service.add_invalid_token_to_cache(token)
        return 'Вы вышли из системы.'


def get_profile(request: HttpRequest, profile: UserProfile) -> dict:
    result = check_token_OK_and_get_claims_or_return_error(request, profile)
    token, phone, user_id = (
        result.get('token'), result.get('phone_number'), result.get('user_id')
    )
    if token and token != '':
        if token_service.check_profile_view_permission(token, phone):
            if token_service.check_token_not_used_for_logout(token):
                if token_service.check_token_signature_valid(token):
                    success = {
                        'id': profile.id,
                        'phone_number': profile.phone_number,
                        'invite_code': profile.invite_code,
                        'activated_code': profile.activated_code,
                        'users_invited': profile.users_invited
                    }
                    return success
            return {
                'token_error': ('''Токен авторизации не валиден или просрочен. '''
                                '''Авторизуйтесь снова.''')
            }
        return {
            'auth_error': 'Вы не можете просматривать профили других пользователей.',
            'user_id': user_id
        }
    return result


def activate_invite_code(profile: UserProfile, invite_code: str) -> dict:
    if invite_code:
        friend_profile = get_profile_or_zero(invite_code)
        if friend_profile:
            if profile.activated_code:
                return {'error': 'У вас уже есть активированный инвайт-код.'}
            if friend_profile == profile:
                return {'error': 'Вы не можете активировать собственный инвайт-код.'}
            profile.activated_code = invite_code
            profile.save()
            add_phone_to_invited_users(friend_profile, profile.phone_number)
            return {'success': 'Вы успешно активировали инвайт-код.'}
        return {'error': 'Введенный вами инвайт-код не существует.'}
    return {'error': 'Вы не ввели инвайт-код.'}


def get_profile_or_zero(invite_code: str) -> UserProfile | int:
    try:
        return UserProfile.objects.get(invite_code=invite_code)
    except UserProfile.DoesNotExist:
        return 0
    

def add_phone_to_invited_users(profile: UserProfile, phone: str) -> None:
    if profile.users_invited:
        profile.users_invited += f', {phone}'
        profile.save()
    else:
        profile.users_invited = phone
        profile.save()

def check_token_OK_and_get_claims_or_return_error(
        request: HttpRequest, profile: UserProfile
) -> dict:
    try:
        token = request.COOKIES['token']
        phone = profile.phone_number
        user_id = token_service.get_id_by_token(token)
        return {'token': token, 'phone_number': phone, 'user_id': user_id}
    except KeyError:
        return {'token_error': 'Сервер не получил токен авторизации. Авторизуйтесь снова.'}
    except JWTError:
        return {'token_error': 'Токен авторизации не валиден. Авторизуйтесь снова.'}
