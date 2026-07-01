from rest_framework import serializers
from django.contrib.auth.hashers import make_password, check_password
from .models import User


class SignUpSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ["username", "password", "email"]

    def validate_username(self, value):
        if len(value.strip()) < 3:
            raise serializers.ValidationError("Username must be at least 3 characters.")
        if User.objects.filter(username__iexact=value).exists():
            raise serializers.ValidationError("This username is already taken.")
        return value

    def validate_email(self, value):
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("An account with this email already exists.")
        return value

    def validate_password(self, value):
        if value.isdigit():
            raise serializers.ValidationError("Password cannot be entirely numeric.")
        if value.lower() == value or value.upper() == value:
            raise serializers.ValidationError("Password must contain both uppercase and lowercase letters.")
        return value

    def create(self, validated_data):
        validated_data["password"] = make_password(validated_data["password"])
        return User.objects.create(**validated_data)


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        identifier = data.get("username")
        password = data.get("password")

        try:
            user = User.objects.get(username=identifier)
        except User.DoesNotExist:
            try:
                user = User.objects.get(email=identifier)
            except User.DoesNotExist:
                raise serializers.ValidationError("Invalid username or password.")

        if not user.password:
            raise serializers.ValidationError("This account uses Google Sign-In. Please log in with Google.")

        if not check_password(password, user.password):
            raise serializers.ValidationError("Invalid username or password.")

        data["user"] = user
        return data
    
    
class GoogleAuthSerializer(serializers.Serializer):
    id_token = serializers.CharField()


class UserOutSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email", "profile_picture"]