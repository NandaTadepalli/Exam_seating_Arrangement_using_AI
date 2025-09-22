from django.core.mail import send_mass_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from student_portal.models import StudentRegCourse
from faculty_portal.models import Faculty, FacultyExamAssignment

def send_exam_notification(exam):
    """
    Send exam notifications to all relevant students and faculty members
    """
    # Get all courses associated with this exam
    exam_courses = exam.examcourse_set.all().prefetch_related('course__student_set', 'course__faculty_set')
    
    # Collect all students from all courses (using a set to avoid duplicates)
    student_emails = set()
    for exam_course in exam_courses:
        for student in exam_course.course.student_set.all():
            if student.email:  # Only add if email exists
                context = {
                    'recipient_name': student.name,
                    'exam_name': exam.exam_name,
                    'courses': ', '.join([ec.course.course_name for ec in exam_courses]),
                    'exam_date': exam.exam_date,
                    'start_time': exam.start_time,
                    'end_time': exam.end_time,
                    'is_student': True
                }
                
                html_message = render_to_string('admin_portal/email/exam_notification.html', context)
                plain_message = strip_tags(html_message)
                
                student_emails.add((
                    f'Exam Notification: {exam.exam_name}',
                    plain_message,
                    settings.DEFAULT_FROM_EMAIL,
                    [student.email]
                ))
    
    # Collect all faculty members involved in the exam
    faculty_emails = set()
    for exam_course in exam_courses:
        for faculty in exam_course.course.faculty_set.all():
            if faculty.email:  # Only add if email exists
                context = {
                    'recipient_name': faculty.name,
                    'exam_name': exam.exam_name,
                    'courses': ', '.join([ec.course.course_name for ec in exam_courses]),
                    'exam_date': exam.exam_date,
                    'start_time': exam.start_time,
                    'end_time': exam.end_time,
                    'is_faculty': True
                }
                
                html_message = render_to_string('admin_portal/email/exam_notification.html', context)
                plain_message = strip_tags(html_message)
                
                faculty_emails.add((
                    f'Exam Duty Notification: {exam.exam_name}',
                    plain_message,
                    settings.DEFAULT_FROM_EMAIL,
                    [faculty.email]
                ))
    
    # Send all emails
    all_emails = list(student_emails) + list(faculty_emails)
    if not all_emails:
        raise ValueError("No recipients found for this exam notification")
    
    send_mass_mail(all_emails, fail_silently=False)
    return len(all_emails)