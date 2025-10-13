from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='student-dashboard'),
    path('profile/', views.profile, name='student-profile'),
]
