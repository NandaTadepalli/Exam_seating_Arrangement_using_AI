import os
import django
import random
from datetime import datetime, timedelta
from django.utils import timezone

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'exam_system.settings')
django.setup()

from django.contrib.auth.hashers import make_password
from accounts.models import User, Notification, Log
from student_portal.models import Student, Course, StudentRegCourse
from faculty_portal.models import (
    Faculty, Room, Exam, ExamCourse, ExamRoom,
    SeatAllocation, FacultyExamAssignment, Attendance, MalpracticeReport
)

def create_users():
    print("Creating users...")
    # Create admin
    admin = User.objects.create(
        username='admin',
        password=make_password('admin123'),
        email='admin@example.com',
        role='admin',
        is_staff=True,
        is_superuser=True
    )

    # Create students
    students = []
    for i in range(1, 31):  # 30 students
        username = f'STU{str(i).zfill(3)}'
        student = User.objects.create(
            username=username,
            password=make_password('student123'),
            email=f'{username.lower()}@example.com',
            first_name=f'Student{i}',
            last_name=f'Last{i}',
            role='student'
        )
        students.append(student)

    # Create faculty
    faculty = []
    for i in range(1, 11):  # 10 faculty members
        username = f'FAC{str(i).zfill(3)}'
        faculty_user = User.objects.create(
            username=username,
            password=make_password('faculty123'),
            email=f'{username.lower()}@example.com',
            first_name=f'Faculty{i}',
            last_name=f'Last{i}',
            role='faculty'
        )
        faculty.append(faculty_user)

    return admin, students, faculty

def create_students(student_users):
    print("Creating student profiles...")
    departments = ['CSE', 'ECE', 'EEE', 'MECH', 'CIVIL']
    students = []
    
    for user in student_users:
        student = Student.objects.create(
            user=user,
            dob=datetime.now().date() - timedelta(days=random.randint(7000, 8000)),
            gender=random.choice(['M', 'F']),
            department=random.choice(departments),
            year=random.randint(1, 4),
            semester=random.randint(1, 2),
            phone=f'9{str(random.randint(100000000, 999999999))}'
        )
        students.append(student)
    return students

def create_faculty(faculty_users):
    print("Creating faculty profiles...")
    departments = ['CSE', 'ECE', 'EEE', 'MECH', 'CIVIL']
    designations = ['Professor', 'Associate Professor', 'Assistant Professor']
    faculty_list = []
    
    for user in faculty_users:
        faculty = Faculty.objects.create(
            user=user,
            department=random.choice(departments),
            designation=random.choice(designations),
            phone=f'9{str(random.randint(100000000, 999999999))}',
            available=True
        )
        faculty_list.append(faculty)
    return faculty_list

def create_rooms():
    print("Creating rooms...")
    blocks = ['A', 'B', 'C']
    rooms = []
    
    for block in blocks:
        for i in range(1, 5):  # 4 rooms per block
            room = Room.objects.create(
                block=block,
                room_number=f'{block}{i}01',
                rows_count=5,
                columns_count=6
            )
            rooms.append(room)
    return rooms

def create_courses():
    print("Creating courses...")
    departments = ['CSE', 'ECE', 'EEE', 'MECH', 'CIVIL']
    courses = []
    
    course_names = [
        'Programming', 'Database Systems', 'Networks', 'Operating Systems',
        'Digital Logic', 'Electronics', 'Circuits', 'Mechanics',
        'Structures', 'Materials', 'Thermodynamics', 'Control Systems'
    ]
    
    for i, name in enumerate(course_names):
        dept = departments[i % len(departments)]
        year = (i % 4) + 1
        Course.objects.create(
            course_code=f'{dept}{str(i+1).zfill(3)}',
            course_name=name,
            department=dept,
            year=year,
            semester=random.randint(1, 2)
        )

def create_student_registrations(students):
    print("Creating student course registrations...")
    courses = Course.objects.all()
    
    for student in students:
        # Register each student for 5 random courses
        student_courses = random.sample(list(courses), 5)
        for course in student_courses:
            StudentRegCourse.objects.create(
                student=student,
                course=course
            )

def create_exam():
    print("Creating sample exams...")
    courses = list(Course.objects.all())
    rooms = list(Room.objects.all())
    faculty_list = list(Faculty.objects.all())
    admin_user = User.objects.get(username='admin')
    
    exam_types = ['THEORY', 'PRACTICAL']
    exam_names = ['Mid Semester Examination', 'Final Examination', 'Internal Assessment']
    
    # Create multiple exams with different dates
    for i in range(5):  # Create 5 different exams
        days_ahead = i * 3 + 1  # Spread exams over next few days
        exam_name = f"{random.choice(exam_names)} - {random.choice(courses).department}"
        
        exam = Exam.objects.create(
            exam_name=exam_name,
            exam_type=random.choice(exam_types),
            year=2025,
            semester=random.randint(1, 2),
            exam_date=datetime.now().date() + timedelta(days=days_ahead),
            start_time=random.choice(['09:00:00', '14:00:00']),
            end_time=random.choice(['12:00:00', '17:00:00']),
            created_by=admin_user
        )
        
        # Assign 2-3 courses to each exam
        for course in random.sample(courses, random.randint(2, 3)):
            ExamCourse.objects.create(
                exam=exam,
                course=course
            )
        
        # Assign 2-3 rooms to each exam
        assigned_rooms = random.sample(rooms, random.randint(2, 3))
        for room in assigned_rooms:
            exam_room = ExamRoom.objects.create(
                exam=exam,
                room=room,
                allocated_capacity=room.rows_count * room.columns_count
            )
            
            # Assign faculty to each room
            if faculty_list:  # If we have available faculty
                assigned_faculty = random.choice(faculty_list)
                FacultyExamAssignment.objects.create(
                    exam=exam,
                    faculty=assigned_faculty,
                    room=room
                )

def create_notifications():
    print("Creating sample notifications...")
    users = User.objects.all()
    
    for user in random.sample(list(users), 5):
        Notification.objects.create(
            user=user,
            title='Exam Schedule Update',
            message='New exam schedule has been published',
            status='UNREAD'
        )

def create_logs():
    print("Creating sample logs...")
    users = User.objects.all()
    actions = ['LOGIN', 'LOGOUT', 'CREATE_EXAM', 'UPDATE_PROFILE']
    
    for _ in range(10):
        Log.objects.create(
            user=random.choice(users),
            action=random.choice(actions),
            description='Sample log entry'
        )

def populate_db():
    # Clear existing data
    print("Clearing existing data...")
    Exam.objects.all().delete()
    Room.objects.all().delete()
    Course.objects.all().delete()
    Faculty.objects.all().delete()
    Student.objects.all().delete()
    User.objects.all().delete()
    
    # Create data
    admin, student_users, faculty_users = create_users()
    students = create_students(student_users)
    faculty = create_faculty(faculty_users)
    rooms = create_rooms()
    create_courses()
    create_student_registrations(students)
    create_exam()
    create_notifications()
    create_logs()
    
    print("\nDatabase populated successfully!")
    print(f"Admin credentials: username='admin', password='admin123'")
    print(f"Student credentials: username='STU001', password='student123'")
    print(f"Faculty credentials: username='FAC001', password='faculty123'")

if __name__ == '__main__':
    populate_db()