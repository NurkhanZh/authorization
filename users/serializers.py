from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.authtoken.models import Token
from rest_framework.exceptions import APIException

User = get_user_model()


class AlreadyRegistered(APIException):
    status_code = 406
    default_detail = 'User is already registered'
    default_code = 'user_already_registered'


class AlreadyActivated(APIException):
    status_code = 405
    default_detail = 'User is already activated'
    default_code = 'user_already_activated'


class PasswordsNotEqual(APIException):
    status_code = 400
    default_detail = 'Passwords are not same'
    default_code = 'passwords_not_equal'


class UserDoesNotExist(APIException):
    status_code = 400
    default_detail = 'Client does not exist'
    default_code = 'client does not exist'


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        style={'input_type': 'password'}, write_only=True
    )
    password2 = serializers.CharField(
        style={'input_type': 'password'}, write_only=True
    )

    class Meta:
        model = User
        fields = ('email', 'user_name', 'password', 'password2')

    def create(self, validated_data):
        password = validated_data['password']
        password2 = validated_data.pop('password2')

        if password != password2:
            raise PasswordsNotEqual

        email = validated_data['email']

        matched = User.objects.filter(email__exact=email)

        if matched.exists():
            user = matched.first()
            if user.is_active:
                raise AlreadyRegistered()
        else:
            user = User.objects.create(email=email, is_active=False)

        if not Token.objects.filter(user=user).exists():
            Token.objects.create(user=user)

        password = validated_data.pop('password')
        User.objects.filter(email=email).update(**validated_data)
        user = User.objects.get(email=email)
        user.set_password(password)
        user.save()
        return user


class AuthTokenSerialzier(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(style={'input_type': 'password'}, write_only=True)

    def validate(self, attrs):
        username = attrs.get('email')
        password = attrs.get('password')

        if username and password:
            try:
                username_field = User.USERNAME_FIELD
                user = User.objects.get(**{username_field: username})
            except User.DoesNotExist:
                msg = 'Unable to log in with provided credentials.'
                raise serializers.ValidationError(msg, code='authorization')
            if not user.check_password(password):
                msg = 'Unable to log in with provided credentials.'
                raise serializers.ValidationError(msg, code='authorization')
            if not user.is_active:
                msg = "Activate your account. Check your email."
                raise serializers.ValidationError(detail={
                    User.USERNAME_FIELD: [msg]
                })
        else:
            msg = 'Must include "username" and "password".'
            raise serializers.ValidationError(msg, code='authorization')

        attrs['user'] = user
        return attrs


class ChoiceValueDisplayField(serializers.Field):
    def to_representation(self, value):
        return value

    def to_internal_value(self, data):
        return data

    def get_attribute(self, instance):
        try:
            attr = self.source
            display_method = getattr(instance, 'get_%s_display' % attr)

            value = getattr(instance, attr)
            display_value = display_method()

            return {
                'value': value,
                'display': display_value
            }
        except Exception as e:
            print(e)
            return super(ChoiceValueDisplayField, self).get_attribute(instance)


class ProfileSerializer(serializers.ModelSerializer):
    gender = ChoiceValueDisplayField()
    rank = ChoiceValueDisplayField(read_only=True)

    class Meta:
        model = User
        fields = ('id', 'email', 'first_name', 'last_name', 'middle_name', 'avatar', 'date_of_birth', 'gender',
                  'points', 'rank', 'user_name')


class EmailSerializer(serializers.Serializer):
    email = serializers.EmailField()

