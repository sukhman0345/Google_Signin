from django.shortcuts import render

# Create your views here.
from google.oauth2 import id_token as google_id_token
from google.auth.transport import requests as google_requests
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from django.conf import settings
from django.shortcuts import render

from .models import User
from .serializers import (
    SignUpSerializer,
    LoginSerializer,
    GoogleAuthSerializer,
    UserOutSerializer,
)


def issue_tokens(user):
    refresh = RefreshToken.for_user(user)
    return {"access": str(refresh.access_token), "refresh": str(refresh)}


class SignUpView(APIView):
    def post(self, request):
        serializer = SignUpSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        tokens = issue_tokens(user)
        return Response({
            "user": UserOutSerializer(user).data,
            **tokens,
        }, status=status.HTTP_201_CREATED)


class LoginView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        tokens = issue_tokens(user)
        return Response({
            "user": UserOutSerializer(user).data,
            **tokens,
        }, status=status.HTTP_200_OK)


class GoogleLoginView(APIView):
    def post(self, request):
        print("\n--- Google Login Process Started ---")
        try:
            serializer = GoogleAuthSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            token = serializer.validated_data["id_token"]
            print(f"Token received (first 25 chars): {token[:25]}...")

            try:
                idinfo = google_id_token.verify_oauth2_token(
                    token, google_requests.Request(), settings.GOOGLE_CLIENT_ID
                )
                print("Token verified successfully by google-auth library!")
                print(f"Token contents: {idinfo}")
            except ValueError as ve:
                print(f"ValueError during token verification: {ve}")
                return Response({"error": f"Invalid Google token: {ve}"}, status=status.HTTP_400_BAD_REQUEST)
            except Exception as e:
                print(f"Unexpected exception during token verification: {e}")
                import traceback
                traceback.print_exc()
                return Response({"error": f"Verification failed: {e}"}, status=status.HTTP_400_BAD_REQUEST)

            email = idinfo.get("email")
            if not email:
                print("Error: Email missing from token payload")
                return Response({"error": "Email not found in token"}, status=status.HTTP_400_BAD_REQUEST)

            picture = idinfo.get("picture")
            name = idinfo.get("name") or email.split("@")[0]
            print(f"User info: Email={email}, Name={name}, Picture={picture}")

            user, created = User.objects.get_or_create(
                email=email,
                defaults={"username": name, "password": "", "profile_picture": picture},
            )
            print(f"User record lookup: Created={created}, UserID={user.id}, Username={user.username}")

            if not created and picture and user.profile_picture != picture:
                user.profile_picture = picture
                user.save()
                print("Updated user profile picture with new Google avatar URL.")

            tokens = issue_tokens(user)
            print("Successfully issued JWT access/refresh tokens.")
            return Response({
                "user": UserOutSerializer(user).data,
                "created": created,
                **tokens,
            }, status=status.HTTP_200_OK)
        except Exception as outer_e:
            print(f"Error in GoogleLoginView post handler: {outer_e}")
            import traceback
            traceback.print_exc()
            return Response({"error": f"Internal server error: {outer_e}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def signup_page(request):
    return render(request, "accounts/auth.html", {
        "initial_mode": "signup",
        "google_client_id": settings.GOOGLE_CLIENT_ID
    })

def login_page(request):
    return render(request, "accounts/auth.html", {
        "initial_mode": "login",
        "google_client_id": settings.GOOGLE_CLIENT_ID
    })

def success_page(request):
    return render(request, "accounts/success.html")