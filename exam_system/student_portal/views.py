from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def profile(request):
    user = request.user
    from accounts.models import Student
    try:
        student = Student.objects.get(user=user)
    except Student.DoesNotExist:
        student = None
    return render(request, 'student_portal/profile.html', {'student': student, 'user': user})

@login_required
def dashboard(request):
    return render(request, 'student_portal/dashboard.html')
