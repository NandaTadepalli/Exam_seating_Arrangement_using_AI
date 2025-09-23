import os
import django
from django.db import connection

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'exam_system.settings')
django.setup()


def reset_db():
    tables = [
        'faculty_portal_malpracticereport',
        'faculty_portal_attendance',
        'faculty_portal_seatallocation',
        'faculty_portal_facultyexamassignment',
        'faculty_portal_examroom',
        'faculty_portal_examcourse',
        'faculty_portal_faculty',
        'faculty_portal_exam',
        'faculty_portal_room',
        'student_portal_studentregcourse',
        'student_portal_student',
        'student_portal_course',
        'accounts_notification',
        'accounts_log',
        'accounts_user',
        'django_admin_log',
        'auth_user_user_permissions',
        'auth_user_groups',
        'auth_group_permissions',
        'auth_group',
        'auth_permission',
        'django_content_type',
        'django_migrations',
        'django_session'
    ]

    with connection.cursor() as cursor:
        for table in tables:
            try:
                cursor.execute(f'DROP TABLE IF EXISTS {table}')
            except Exception as e:
                print(f"Error dropping {table}: {str(e)}")


if __name__ == '__main__':
    reset_db()
