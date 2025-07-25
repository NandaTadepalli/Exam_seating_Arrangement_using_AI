# faculty_portal/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='faculty-dashboard'),
    path('attendance/<int:duty_id>/', views.attendance, name='faculty-attendance'),
    path('profile/', views.profile, name='faculty-profile'),
]
