from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import AttendanceRecord, MalpracticeReport
from accounts.models import Faculty, User
from admin_portal.models.exam import Exam, Room, RoomAllocation, SeatAllocation
from student_portal.models import CourseRegistration


@login_required
def dashboard(request):
    faculty = get_object_or_404(Faculty, user=request.user)
    assignments = RoomAllocation.objects.filter(
        invigilator=faculty).select_related('exam', 'room')
    return render(request, 'faculty_portal/faculty.html', {
        'faculty': faculty,
        'assignments': assignments
    })


@login_required
def attendance(request, assignment_id):
    faculty = get_object_or_404(Faculty, user=request.user)
    assignment = get_object_or_404(
        RoomAllocation, id=assignment_id, invigilator=faculty)

    attendance_records = AttendanceRecord.objects.filter(
        exam=assignment.exam,
        room=assignment.room
    ).select_related('student')

    if request.method == 'POST':
        for record_id in request.POST.getlist('student_ids'):
            status = request.POST.get(f'status_{record_id}')
            if status in ['PRESENT', 'ABSENT']:
                # Update or create attendance record
                attendance, created = AttendanceRecord.objects.update_or_create(
                    exam=assignment.exam,
                    student_id=record_id,
                    room=assignment.room,
                    defaults={
                        'marked_by': faculty,
                        'status': status
                    }
                )

                # Handle malpractice report if any
                malpractice_desc = request.POST.get(f'malpractice_{record_id}')
                if malpractice_desc:
                    MalpracticeReport.objects.create(
                        exam=assignment.exam,
                        student_id=record_id,
                        faculty=faculty,
                        description=malpractice_desc
                    )

        return redirect('faculty-dashboard')

    return render(request, 'faculty_portal/attendance.html', {
        'assignment': assignment,
        'attendance_records': attendance_records
    })


@login_required
def profile(request):
    faculty = request.user
    if request.method == 'POST':
        faculty.email = request.POST.get('contact', faculty.email)
        faculty.save()
        return redirect('faculty-profile')
    return render(request, 'faculty_portal/profile.html', {'faculty': faculty})
