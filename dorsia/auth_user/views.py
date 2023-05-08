from auth_user.forms import SignUpForm
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.views import LoginView
from django.shortcuts import render, redirect
from django.views.generic import View


class SignUpView(View):
    def get(self, request):
        form = SignUpForm()
        return render(request, 'auth/register.html', {'form': form})

    def post(self, request):
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('chat')
        else:
            return render(request, 'auth/register.html', {'form': form})


class SignInView(LoginView):
    template_name = 'auth/login.html'
    redirect_authenticated_user = True

    def form_invalid(self, form):
        # Call parent's form_invalid() method to trigger default error handling
        response = super().form_invalid(form)

        # Add error message to the message queue
        messages.error(self.request, 'Invalid username or password. Please try again.')

        # Return the response object with the error message
        return response


class LogoutView(View):
    def get(self, request):
        logout(request)
        return redirect('chat')
