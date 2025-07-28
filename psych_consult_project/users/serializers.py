# users/serializers.py
from rest_framework import serializers
from django.contrib.auth import authenticate, password_validation
from django.core.exceptions import ValidationError
from .models import User, SocialAccount

class UserRegistrationSerializer(serializers.ModelSerializer):
    name = serializers.CharField(max_length=255, required=True)
    password = serializers.CharField(
        write_only=True,
        min_length=8,
        validators=[password_validation.validate_password]
    )
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('name', 'email', 'password', 'password_confirm')
        extra_kwargs = {
            'email': {'required': True},
        }

    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({"password": "Passwords don't match"})
        return attrs

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("User with this email already exists")
        return value

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        # Create a unique username from the email
        username = validated_data['email'].split('@')[0]
        original_username = username
        counter = 1
        while User.objects.filter(username=username).exists():
            username = f"{original_username}{counter}"
            counter += 1
        
        user = User.objects.create_user(
            username=username,
            email=validated_data['email'],
            password=validated_data['password'],
            name=validated_data['name'],
            is_active=False
        )
        return user

class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')
        
        if email and password:
            user = authenticate(
                request=self.context.get('request'),
                username=email,
                password=password
            )
            if not user:
                raise serializers.ValidationError('Invalid credentials')
            if not user.is_active:
                raise serializers.ValidationError('User account is disabled')
            attrs['user'] = user
        else:
            raise serializers.ValidationError('Must include email and password')
        
        return attrs

class SocialAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = SocialAccount
        fields = ('id', 'provider', 'uid', 'extra_data')

class UserProfileSerializer(serializers.ModelSerializer):
    social_accounts = SocialAccountSerializer(many=True, read_only=True)

    class Meta:
        model = User
        fields = (
            'id', 'username', 'email', 'name',
            'phone', 'profile_image', 'date_joined',
            'social_accounts'
        )
        read_only_fields = ('id', 'email', 'date_joined', 'social_accounts')

class UserProfileUpdateSerializer(serializers.ModelSerializer):
    username = serializers.CharField(required=False)
    name = serializers.CharField(required=False)
    old_password = serializers.CharField(write_only=True, required=False)
    new_password = serializers.CharField(write_only=True, required=False)
    confirm_password = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = User
        fields = ('username', 'name', 'old_password', 'new_password', 'confirm_password')

    def validate_username(self, value):
        # Check if the username is already taken by another user
        if User.objects.filter(username=value).exclude(pk=self.instance.pk).exists():
            raise serializers.ValidationError("This username is already taken.")
        return value

    def validate(self, data):
        # Handle password change validation
        new_password = data.get('new_password')
        confirm_password = data.get('confirm_password')
        old_password = data.get('old_password')

        if new_password or confirm_password:
            if not old_password:
                raise serializers.ValidationError({'old_password': 'This field is required when changing the password.'})
            if not self.instance.check_password(old_password):
                raise serializers.ValidationError({'old_password': 'Your old password was entered incorrectly.'})
            if new_password != confirm_password:
                raise serializers.ValidationError({'new_password': 'The two password fields didn’t match.'})
            
            # Validate the new password against Django's password validators
            password_validation.validate_password(new_password, self.instance)

        return data

    def update(self, instance, validated_data):
        # Update username if provided
        instance.username = validated_data.get('username', instance.username)
        # Update name if provided
        instance.name = validated_data.get('name', instance.name)

        # Set new password if provided
        new_password = validated_data.get('new_password')
        if new_password:
            instance.set_password(new_password)
        
        instance.save()
        return instance

class PasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField()

class PasswordResetConfirmSerializer(serializers.Serializer):
    new_password = serializers.CharField(
        min_length=8,
        validators=[password_validation.validate_password]
    )
    new_password_confirm = serializers.CharField()
    
    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError("Passwords don't match")
        return attrs