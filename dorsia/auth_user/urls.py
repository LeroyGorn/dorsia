from auth_user.views import SignUpView, LogoutView, SignInView
from django.urls import path

urlpatterns = [
    path('login', SignInView.as_view(), name='login'),
    path('logout', LogoutView.as_view(), name='logout'),
    path('register', SignUpView.as_view(), name='register')
]
