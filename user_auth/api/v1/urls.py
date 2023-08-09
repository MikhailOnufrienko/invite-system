from django.urls import path

from . import views


app_name = 'auth_api'

urlpatterns = [
    path('authorize/', views.authorize, name='authorize'),
    path('confirm-phone/<str:phone>/', views.confirm, name='confirm'),
    path('profile/<int:id>/', views.profile, name='profile'),
    path('profile/<int:id>/activate/', views.profile, name='activate'),
    path('out/', views.logout, name='out'),
]