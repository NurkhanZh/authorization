from django.db import models
from django.contrib.auth.models import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver


class User(AbstractBaseUser, PermissionsMixin):
    UNDEFINED, MALE, FEMALE = 0, 1, 2
    GENDERS = (
        (UNDEFINED, 'Undefined'),
        (MALE, 'Male'),
        (FEMALE, 'Female'),
    )
    I, II, III, IV, IO, IOO, IOOO = 0, 1, 2, 3, 4, 5, 6

    RANK = (
        (I, 'I'),
        (II, 'II'),
        (III, 'III'),
        (IV, 'IV'),
        (IO, 'Master Candidate'),
        (IOO, 'Master of Sport'),
        (IOOO, 'Grandmaster')
    )

    email = models.EmailField(max_length=100, unique=True)
    first_name = models.CharField(max_length=150, help_text='Имя', null=True, blank=True)
    last_name = models.CharField(max_length=150, help_text='Фамилия', null=True, blank=True)
    middle_name = models.CharField(max_length=150, help_text='Отчество', null=True, blank=True)
    user_name = models.CharField(max_length=100, help_text='Ник')

    avatar = models.ImageField(null=True, blank=True, default="user_default.jpeg", upload_to="static/photo")
    date_of_birth = models.DateField(blank=True, null=True)
    gender = models.SmallIntegerField(choices=GENDERS, default=UNDEFINED)
    date_joined = models.DateTimeField('Дата регистрации', auto_now_add=True)
    points = models.IntegerField(default=1000, help_text='Очки')
    rank = models.SmallIntegerField(choices=RANK, default=I)
    is_active = models.BooleanField(default=False)

    REQUIRED_FIELDS = ['first_name', 'last_name', 'middle_name']
    USERNAME_FIELD = 'email'

    def __str__(self):
        return f'{self.email}'


class FileModel(models.Model):
    file = models.FileField(null=True, upload_to="media/files")
    bin_file = models.BinaryField(null=True)
    image = models.ImageField(null=True)
    name = models.CharField(max_length=255, null=True)

# @receiver(post_save, sender=FileModel, dispatch_uid='example_for_signals')
# def example(sender, instance, update_fields, **kwargs):
#     print(update_fields)
#     print(instance)
#     print(sender)
#     print(kwargs)


class ExampleModel(models.Model):
    name = models.CharField(max_length=100, db_index=True)
    age = models.IntegerField(db_index=True)
    z = models.CharField(max_length=100, default='')
    y = models.IntegerField(default=0)

