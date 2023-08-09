from collections import OrderedDict

from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.request import Request
from rest_framework.response import Response

from .serializers import (ActivateInviteCodeSerializer, UserAuthCodeSerializer,
                          UserPhoneSerializer, UserProfileViewSerializer)
from user_auth import service, token_service
from user_auth.models import UserProfile


@api_view(['POST'])
def authorize(request: Request) -> Response:
    serializer = UserPhoneSerializer(data=request.data)
    if serializer.is_valid():
        auth_code = service.create_auth_code()
        return Response({'auth_code': auth_code}, status=status.HTTP_200_OK)


@api_view(['POST'])
def confirm(request: Request, phone: str) -> Response:
    serializer = UserAuthCodeSerializer(data=request.data)
    if serializer.is_valid():
        auth_code_serialized: OrderedDict = serializer.validated_data
        auth_code = auth_code_serialized.get('auth_code')
        result: dict = service.authorize_user(phone, auth_code)
        success = result.get('success')
        if success:
            user_id = result.get('user_id')
            token = result['header']['Authorization']
            return Response(
                {'success': success, 'user_id': user_id}, 
                status=status.HTTP_200_OK,
                headers={'Authorization': token}
            )
        error = result.get('error')
        if error:
            return Response({'error': error}, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['GET', 'POST'])
def profile(request: Request, id: int) -> Response:
    result = check_profile_exists_and_return_profile_or_error(id)
    if isinstance(result, dict):
        return Response(result, status=status.HTTP_404_NOT_FOUND)
    profile = result
    token = request.headers.get('Authorization')
    if not token:
        return Response(
            {'error': 'Не предоставлен токен авторизации.'},
            status=status.HTTP_401_UNAUTHORIZED
        )
    result = check_auth_valid(token, profile)
    if isinstance(result, dict):
        if result.get('error_invalid'):
            return Response(result, status=status.HTTP_401_UNAUTHORIZED)
        if result.get('error_auth'):
            return Response(result, status=status.HTTP_403_FORBIDDEN)
    if request.method == 'GET':
        serializer = UserProfileViewSerializer(profile)
        return Response(serializer.data, status=status.HTTP_200_OK)
    if request.method == 'POST':
        serializer = ActivateInviteCodeSerializer(data=request.data)
        if serializer.is_valid():
            invite_code_serialized: OrderedDict = serializer.validated_data
            invite_code = invite_code_serialized.get('invite_code')
            result = service.activate_invite_code(profile, invite_code)
            if result.get('error'):
                return Response(result, status=status.HTTP_401_UNAUTHORIZED)
            if result.get('success'):
                return Response(result, status=status.HTTP_201_CREATED)

def check_profile_exists_and_return_profile_or_error(id: int) -> UserProfile | dict:
    try:
        profile = UserProfile.objects.get(id=id)
        return profile
    except UserProfile.DoesNotExist:
        return {'error': 'Пользователя с таким ID не существует.'}


def check_auth_valid(token: str, profile: UserProfile) -> bool | dict:
    if token_service.check_token_signature_valid(token):
        if token_service.check_profile_view_permission(token, profile.phone_number):
            if token_service.check_token_not_used_for_logout(token):
                return True
        return {'error_auth': '''Вы не можете просматривать и изменять профили других '''
                          '''пользователей.'''}
    return {'error_invalid': '''Токен авторизации не валиден или просрочен. '''
                         '''Авторизуйтесь снова.'''}


@api_view(['POST'])
def logout(request: Request) -> Response:
    token = request.headers.get('Authorization')
    if token and token != '':
        token_service.add_invalid_token_to_cache(token)
        return Response(
            {'success': 'Вы вышли из системы.'},
            status=status.HTTP_200_OK
        )
    return Response(
            {'error': 'Токен авторизации не валиден или просрочен. Авторизуйтесь снова.'},
            status=status.HTTP_401_UNAUTHORIZED
    )
