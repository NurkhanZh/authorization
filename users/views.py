from pprint import pprint

from django.core.mail import EmailMessage
from django.shortcuts import render
from django.contrib.auth import get_user_model
from django.template.loader import render_to_string
from rest_framework import generics, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from rest_framework.authtoken.models import Token
from rest_framework.parsers import MultiPartParser

from users.serializers import UserRegistrationSerializer, AuthTokenSerialzier, ProfileSerializer, EmailSerializer, \
    UserDoesNotExist
from users.token import account_activation_token

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


class SendEmailMessage(generics.RetrieveAPIView):
    serializer_class = EmailSerializer
    permission_classes = (AllowAny, )

    def get(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data.get('email')
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise UserDoesNotExist
        mail_subject = 'Activate your account.'
        current_site = get_current_site(request)
        print('fisking you')
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
        except Exception:
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
            return Response({'success': 'Client is successfully activated'}, status=status.HTTP_200_OK)
        return Response({'error': 'Client cant activated'}, status=status.HTTP_400_BAD_REQUEST)


class AuthTokenAPIView(generics.CreateAPIView):
    permission_classes = (AllowAny,)
    serializer_class = AuthTokenSerialzier

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response({'token': token.key})


class ProfileAPIView(generics.RetrieveUpdateAPIView):
    serializer_class = ProfileSerializer

    def get_object(self):
        # print("from user")
        return self.request.user
