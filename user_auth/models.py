from django.db import models


class UserProfile(models.Model):
    phone_number = models.CharField(
        verbose_name='Номер телефона', unique=True, db_index=True
    )
    invite_code = models.CharField(
        verbose_name='Личный инвайт-код пользователя', max_length=6, db_index=True
    )
    activated_code = models.CharField(
        verbose_name='Активированный код', max_length=6, null=True, blank=True
    )
    users_invited = models.TextField(
        verbose_name='Клиенты, использовавшие код данного пользователя',
        null=True, blank=True
    )

    class Meta:
        db_table = "auth\".\"user_profile"
        verbose_name = 'User Profile'
        verbose_name_plural = 'User Profiles'

    def __str__(self):
        return self.phone_number
