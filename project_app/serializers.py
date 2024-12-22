from .models import *
from rest_framework import serializers
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model, authenticate

User = get_user_model()

class RegisterSerializer(serializers.ModelSerializer):
    confirm_password = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = [
            'username', 'password', 'confirm_password', 'email', 
            'user_type', 'contact_number', 'is_approved', 
            'is_email_verified', 'is_active', 'created_at'
        ]
        extra_kwargs = {
            'password': {'write_only': True},
            'contact_number': {'required': False},
            'is_approved': {'read_only': True},
            'is_email_verified': {'read_only': True},
            'is_active': {'read_only': True},
            'created_at': {'read_only': True}
        }

    def validate(self, data):
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError({"confirm_password": "Passwords do not match."})
        return data

    def validate_email(self, value):
        if CustomUser.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value

    def create(self, validated_data):
        validated_data.pop('confirm_password')
        
        user = CustomUser.objects.create_user(**validated_data)
        return user


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

    def validate(self, data):
        user = authenticate(username=data['username'], password=data['password'])
        if user is None:
            raise serializers.ValidationError('Invalid credentials')
        return {'user': user}


class UserApprovalSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'user_type', 'contact_number', 'is_approved', 'created_at']