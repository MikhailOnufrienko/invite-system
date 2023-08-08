from django.urls import path

from . import views


app_name = 'user_auth'

urlpatterns = [
    path('authorize/', views.authorize, name='authorize'),
    path('confirm-phone/<str:phone>', views.confirm, name='confirm'),
    path('profile/<int:id>', views.profile, name='profile'),
  #  path('out/', views.out, name='out'),
]
