import random
import string

from django.http import HttpRequest

from .models import UserProfile


auth_code = ''


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
        success = 'Вы авторизованы.'
        profile = UserProfile.objects.get(phone_number=phone_number)
        return {'success': success, 'user_id': profile.id}
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
