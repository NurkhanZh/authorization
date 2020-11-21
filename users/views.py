from pprint import pprint
import hashlib

from django.core.mail import EmailMessage
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.contrib.auth import get_user_model
from django.template.loader import render_to_string
from rest_framework import generics, status
from rest_framework.parsers import FileUploadParser, MultiPartParser
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from rest_framework.authtoken.models import Token
from rest_framework.views import APIView

from authorization import settings
from users.models import FileModel
from users.serializers import UserRegistrationSerializer, AuthTokenSerialzier, ProfileSerializer, EmailSerializer, \
    UserDoesNotExist, ExampleSerializer
from users.token import account_activation_token

from django.contrib.auth import authenticate, logout, login

User = get_user_model()


class UserRegistrationView(generics.CreateAPIView):
    serializer_class = UserRegistrationSerializer
    permission_classes = (AllowAny,)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        return serializer.save()


class SendEmailMessage(generics.CreateAPIView):
    serializer_class = EmailSerializer
    permission_classes = (AllowAny,)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data.get('email')
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise UserDoesNotExist
        mail_subject = 'Activate your account.'
        current_site = get_current_site(request)
        pprint(current_site.domain)
        pprint(urlsafe_base64_encode(force_bytes(user.id)))
        message = render_to_string('acc_activate.html', {
            'user': user,
            'domain': current_site.domain,
            'uid': urlsafe_base64_encode(force_bytes(user.id)),
            'token': account_activation_token.make_token(user),
        })
        pprint(message)
        email = EmailMessage(
            mail_subject, message, to=[email]
        )
        try:
            email.send()
            return Response({'success': "Message sent"})
        except Exception as e:
            pprint(e)
            return Response({'error': "Message did not send"})


class ActivateUserAPIView(generics.RetrieveAPIView):
    permission_classes = (AllowAny,)

    def get(self, request, *args, **kwargs):
        uidb64 = kwargs.pop('uidb64')
        token = kwargs.pop('token')
        try:
            uid = force_text(urlsafe_base64_decode(uidb64))
            user = User.objects.get(id=uid)
        except(TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None
        if user is not None and account_activation_token.check_token(user, token):
            user.is_active = True
            user.save()
            return HttpResponseRedirect(redirect_to="http://autochess.kz/")
        return Response({'error': 'Client cant activated'}, status=status.HTTP_400_BAD_REQUEST)


class AuthTokenAPIView(generics.CreateAPIView):
    permission_classes = (AllowAny,)
    serializer_class = AuthTokenSerialzier

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        un = data.get('email')
        p = data.get('password')
        user_obj = authenticate(username=un,
                                password=p)
        login(request, user_obj, backend='django_auth_ldap.backend.LDAPBackend')
        data = {'detail': 'User logged in successfully'}
        return data
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response({'token': token.key})


class ProfileAPIView(generics.RetrieveUpdateAPIView):
    serializer_class = ProfileSerializer

    def get_object(self):
        pprint(settings.BASE_DIR)
        pprint(settings.MEDIA_ROOT)
        # print("from user")
        return self.request.user


class ResetAPIView(generics.RetrieveAPIView):
    permission_classes = (AllowAny,)

    def get(self, request, *args, **kwargs):
        try:
            User.objects.all().delete()
            return Response({"success"})
        except Exception:
            return Response({"problems"})


class ResetPasswordAPIView(generics.UpdateAPIView):

    def get_object(self):
        return self.request.user

    def update(self, request, *args, **kwargs):
        password = "Password!"
        obj = self.get_object()
        mail_subject = 'Your password changed.'
        message = render_to_string('reset_password.html', {
            'user': obj,
            "password": password
        })
        email = EmailMessage(
            mail_subject, message, to=[obj.email]
        )
        try:
            email.send()
        except Exception as e:
            pprint(e)
            return Response({"error": "password not changed"})

        response = {}
        try:
            obj.set_password(password)
            obj.save()
        except Exception as e:
            print(e)
        response["ok"] = "password changed"
        return Response(response)


class ExampleView(generics.CreateAPIView, generics.UpdateAPIView):
    permission_classes = (AllowAny,)
    parser_classes = (MultiPartParser,)
    serializer_class = ExampleSerializer
    lookup_field = 'pk'

    def get_queryset(self):
        return FileModel.objects.all()

    def post(self, request, *args, **kwargs):

        return super(ExampleView, self).post(request, *args, **kwargs)

    # def post(self, request, *args, **kwargs):
    #     print('*'*40)
    #     f = self.request.FILES['file']
    #     print(f)
    #     # for ch in f.chunks():
    #     #     print(ch)
    #     f = f.read()
    #     print(f)
    #     print(f[0])
    #     print(f[1])
    #     return Response('hello')
