from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import InvigilationDuty, Attendance, MalpracticeReport
from accounts.models import User


@login_required
def dashboard(request):
    faculty = request.user
    duties = InvigilationDuty.objects.filter(
        faculty=faculty).select_related('exam')
    return render(request, 'faculty_portal/faculty.html', {'faculty': faculty, 'duties': duties})


@login_required
def attendance(request, duty_id):
    duty = get_object_or_404(
        InvigilationDuty, id=duty_id, faculty=request.user)
    attendance_records = Attendance.objects.filter(
        invigilation=duty).select_related('student')
    if request.method == 'POST':
        for record in attendance_records:
            present = request.POST.get(f'present_{record.id}') == 'on'
            record.present = present
            record.save()
            # Malpractice handling
            if request.POST.get(f'mal_type_{record.id}'):
                MalpracticeReport.objects.create(
                    attendance=record,
                    malpractice_type=request.POST.get(f'mal_type_{record.id}'),
                    description=request.POST.get(f'mal_desc_{record.id}', ''),
                    evidence=request.FILES.get(f'mal_evidence_{record.id}')
                )
        return redirect('faculty-dashboard')
    return render(request, 'faculty_portal/attendance.html', {'duty': duty, 'attendance': attendance_records})


@login_required
def profile(request):
    faculty = request.user
    if request.method == 'POST':
        faculty.email = request.POST.get('contact', faculty.email)
        faculty.save()
        return redirect('faculty-profile')
    return render(request, 'faculty_portal/profile.html', {'faculty': faculty})
