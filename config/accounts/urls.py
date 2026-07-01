from django.urls import path
from .views import SignUpView, LoginView, GoogleLoginView, signup_page, login_page, success_page

urlpatterns = [
    # Pages
    path("signup-page/", signup_page, name="signup-page"),
    path("login-page/", login_page, name="login-page"),
    path("success/", success_page, name="success-page"),

    # API
    path("signup/", SignUpView.as_view(), name="signup"),
    path("login/", LoginView.as_view(), name="login"),
    path("google-login/", GoogleLoginView.as_view(), name="google-login"),
]