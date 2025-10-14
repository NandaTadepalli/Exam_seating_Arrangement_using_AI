import random
import string
from datetime import date

from django.core.management.base import BaseCommand
from django.db import transaction
from django.contrib.auth import get_user_model

from accounts.models import Department, Student, Faculty


def random_id(prefix, length=6):
    return f"{prefix}_{''.join(random.choices(string.ascii_uppercase + string.digits, k=length))}"


class Command(BaseCommand):
    help = 'Seed dummy data: departments, admin user, some faculty and students'

    def add_arguments(self, parser):
        parser.add_argument('--departments', type=int, default=3, help='Number of departments')
        parser.add_argument('--faculty', type=int, default=5, help='Number of faculty to create')
        parser.add_argument('--students', type=int, default=20, help='Number of students to create')

    def handle(self, *args, **options):
        User = get_user_model()
        deps = options['departments']
        fac_count = options['faculty']
        stu_count = options['students']

        with transaction.atomic():
            # Departments
            departments = []
            for i in range(deps):
                name = f"Dept_{i+1}"
                code = f"D{i+1}"
                dept, _ = Department.objects.get_or_create(name=name, defaults={'code': code})
                departments.append(dept)

            # Admin user: prefer to update by user_id, but if username already exists
            # use that record to avoid unique constraint errors on username.
            admin_uid = 'ADMIN_001'
            try:
                admin, created = User.objects.update_or_create(
                    user_id=admin_uid,
                    defaults={
                        'username': 'admin',
                        'email': 'admin@example.com',
                        'first_name': 'Site',
                        'last_name': 'Admin',
                        'role': 'ADMIN',
                    }
                )
            except Exception:
                # fallback: find by username and update fields
                admin = None
                try:
                    admin = User.objects.get(username='admin')
                    admin.email = 'admin@example.com'
                    admin.first_name = 'Site'
                    admin.last_name = 'Admin'
                    admin.role = 'ADMIN'
                    # ensure primary key user_id exists
                    if not getattr(admin, 'user_id', None):
                        admin.user_id = admin_uid
                except User.DoesNotExist:
                    # as last resort create new user with admin_uid
                    admin = User(user_id=admin_uid, username='admin', email='admin@example.com', first_name='Site', last_name='Admin', role='ADMIN')
                admin.set_password('adminpass')
                admin.is_superuser = True
                admin.is_staff = True
                admin.save()
            else:
                admin.set_password('adminpass')
                admin.is_superuser = True
                admin.is_staff = True
                admin.save()

            # Faculty
            faculties = []
            for i in range(fac_count):
                uid = random_id('FAC')
                username = f"faculty{i+1}"
                try:
                    user, _ = User.objects.update_or_create(
                        user_id=uid,
                        defaults={
                            'username': username,
                            'email': f"{username}@example.com",
                            'first_name': f"Fac{i+1}",
                            'last_name': 'Member',
                            'role': 'FACULTY',
                        }
                    )
                except Exception:
                    # fallback to find by username and update
                    try:
                        user = User.objects.get(username=username)
                        user.email = f"{username}@example.com"
                        user.first_name = f"Fac{i+1}"
                        user.last_name = 'Member'
                        user.role = 'FACULTY'
                        if not getattr(user, 'user_id', None):
                            user.user_id = uid
                    except User.DoesNotExist:
                        user = User(user_id=uid, username=username, email=f"{username}@example.com", first_name=f"Fac{i+1}", last_name='Member', role='FACULTY')
                user.set_password('facpass')
                user.save()
                emp_id = random_id('EMP', 5)
                faculty, _ = Faculty.objects.get_or_create(user=user, defaults={'emp_id': emp_id, 'department': random.choice(departments)})
                faculties.append(faculty)

            # Students
            for i in range(stu_count):
                uid = random_id('STU')
                username = f"student{i+1}"
                try:
                    user, _ = User.objects.update_or_create(
                        user_id=uid,
                        defaults={
                            'username': username,
                            'email': f"{username}@example.com",
                            'first_name': f"Stu{i+1}",
                            'last_name': 'Learner',
                            'role': 'STUDENT',
                        }
                    )
                except Exception:
                    try:
                        user = User.objects.get(username=username)
                        user.email = f"{username}@example.com"
                        user.first_name = f"Stu{i+1}"
                        user.last_name = 'Learner'
                        user.role = 'STUDENT'
                        if not getattr(user, 'user_id', None):
                            user.user_id = uid
                    except User.DoesNotExist:
                        user = User(user_id=uid, username=username, email=f"{username}@example.com", first_name=f"Stu{i+1}", last_name='Learner', role='STUDENT')
                user.set_password('stupass')
                user.save()
                reg_no = f"R{i+1:04d}"
                Student.objects.get_or_create(
                    user=user,
                    defaults={
                        'reg_no': reg_no,
                        'department': random.choice(departments),
                        'year': random.randint(1, 4),
                        'semester': random.randint(1, 8),
                    }
                )

        self.stdout.write(self.style.SUCCESS(
            f'Seeded: {len(departments)} departments, 1 admin, {len(faculties)} faculty, {stu_count} students'
        ))
