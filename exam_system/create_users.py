import os
import django
import sys

# Set up Django environment
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'exam_system.settings')
django.setup()

from django.contrib.auth import get_user_model
from accounts.models import Department, Faculty, Student
from django.db import transaction

User = get_user_model()

def create_users():
    try:
        with transaction.atomic():
            # Create Departments
            cs_dept = Department.objects.create(
                name="Computer Science",
                code="CS"
            )
            it_dept = Department.objects.create(
                name="Information Technology",
                code="IT"
            )
            
            # Create Admin User
            admin_user = User.objects.create_superuser(
                username='admin',
                email='admin@example.com',
                password='admin123',
                first_name='Admin',
                last_name='User',
                role='ADMIN'
            )
            
            # Create Faculty Users
            faculty1_user = User.objects.create_user(
                username='faculty1',
                email='faculty1@example.com',
                password='faculty123',
                first_name='John',
                last_name='Doe',
                is_staff=True,
                role='FACULTY'
            )
            
            faculty2_user = User.objects.create_user(
                username='faculty2',
                email='faculty2@example.com',
                password='faculty123',
                first_name='Jane',
                last_name='Smith',
                is_staff=True,
                role='FACULTY'
            )
            
            # Create Faculty Profiles
            Faculty.objects.create(
                user=faculty1_user,
                department=cs_dept,
                emp_id='FAC001',
                designation='Professor',
                specialization='Software Engineering'
            )
            
            Faculty.objects.create(
                user=faculty2_user,
                department=it_dept,
                emp_id='FAC002',
                designation='Associate Professor',
                specialization='Data Science'
            )
            
            # Create Student Users
            student1_user = User.objects.create_user(
                username='student1',
                email='student1@example.com',
                password='student123',
                first_name='Alice',
                last_name='Johnson',
                role='STUDENT'
            )
            
            student2_user = User.objects.create_user(
                username='student2',
                email='student2@example.com',
                password='student123',
                first_name='Bob',
                last_name='Wilson',
                role='STUDENT'
            )
            
            # Create Student Profiles
            Student.objects.create(
                user=student1_user,
                department=cs_dept,
                reg_no='STU001',
                year=2023,
                semester=3,
                section='A'
            )
            
            Student.objects.create(
                user=student2_user,
                department=it_dept,
                reg_no='STU002',
                year=2023,
                semester=3,
                section='B'
            )
            
            print("Successfully created all users!")
            print("\nLogin Credentials:")
            print("Admin:")
            print("Username: admin")
            print("Password: admin123")
            print("\nFaculty:")
            print("Username: faculty1 or faculty2")
            print("Password: faculty123")
            print("\nStudents:")
            print("Username: student1 or student2")
            print("Password: student123")
            
    except Exception as e:
        print(f"Error creating users: {e}")

if __name__ == '__main__':
    create_users()