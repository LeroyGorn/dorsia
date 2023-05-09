from auth_user.forms import SignUpForm
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.views import LoginView
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import View, FormView


class SignUpView(FormView):
    template_name = "auth/register.html"
    form_class = SignUpForm
    success_url = reverse_lazy("chat")

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return super().form_valid(form)

    def form_invalid(self, form):
        response = super().form_invalid(form)
        messages.error(self.request, "Invalid form. Please try again.")
        return response


class SignInView(LoginView):
    template_name = "auth/login.html"
    redirect_authenticated_user = True

    def form_invalid(self, form):
        response = super().form_invalid(form)
        messages.error(self.request, "Invalid email or password. Please try again.")
        return response


class LogoutView(View):
    def get(self, request):
        logout(request)
        return redirect("chat")
