def create_exam_data():
    print("Creating sample exam data...")
    from faculty_portal.models import Exam
    from django.utils import timezone
    from datetime import timedelta
    
    # Create some upcoming exams
    exam1 = Exam.objects.create(
        exam_name="Mid Semester Examination",
        exam_type="THEORY",
        year=2,
        semester=1,
        exam_date=timezone.now().date() + timedelta(days=7),
        start_time="09:00:00",
        end_time="12:00:00",
        created_by=User.objects.get(username='admin')
    )
    
    exam2 = Exam.objects.create(
        exam_name="Final Examination",
        exam_type="THEORY",
        year=3,
        semester=1,
        exam_date=timezone.now().date() + timedelta(days=14),
        start_time="14:00:00",
        end_time="17:00:00",
        created_by=User.objects.get(username='admin')
    )
    
    # Associate courses with exams
    courses = Course.objects.all()
    for course in courses[:3]:  # First 3 courses for exam1
        ExamCourse.objects.create(exam=exam1, course=course)
    
    for course in courses[3:6]:  # Next 3 courses for exam2
        ExamCourse.objects.create(exam=exam2, course=course)
    
    return [exam1, exam2]