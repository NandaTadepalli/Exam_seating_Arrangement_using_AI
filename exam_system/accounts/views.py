from django.contrib.auth.views import LoginView
from django.shortcuts import redirect
from django.urls import reverse_lazy
from .models import User

class RoleBasedLoginView(LoginView):
    template_name = 'accounts/login.html'

    def get_success_url(self):
        user = self.request.user
        if user.role == 'admin':
            return reverse_lazy('admin-dashboard')
        elif user.role == 'faculty':
            return reverse_lazy('faculty-dashboard')
        elif user.role == 'student':
            return reverse_lazy('student-dashboard')
        return reverse_lazy('login')
