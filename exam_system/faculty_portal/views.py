from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Faculty, FacultyExamAssignment, Attendance, MalpracticeReport, Exam, Room
from accounts.models import User


@login_required
def dashboard(request):
    faculty = get_object_or_404(Faculty, user=request.user)
    assignments = FacultyExamAssignment.objects.filter(
        faculty=faculty).select_related('exam', 'room')
    return render(request, 'faculty_portal/faculty.html', {
        'faculty': faculty,
        'assignments': assignments
    })


@login_required
def attendance(request, assignment_id):
    faculty = get_object_or_404(Faculty, user=request.user)
    assignment = get_object_or_404(
        FacultyExamAssignment, id=assignment_id, faculty=faculty)
    
    attendance_records = Attendance.objects.filter(
        exam=assignment.exam,
        room=assignment.room
    ).select_related('student')
    
    if request.method == 'POST':
        for record_id in request.POST.getlist('student_ids'):
            status = request.POST.get(f'status_{record_id}')
            if status in ['PRESENT', 'ABSENT']:
                # Update or create attendance record
                attendance, created = Attendance.objects.update_or_create(
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
