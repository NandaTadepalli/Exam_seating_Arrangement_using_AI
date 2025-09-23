from django.db import connection
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'exam_system.settings')
django.setup()


# List of old tables to drop
old_tables = [
    'attendance',
    'course',
    'exam',
    'faculty',
    'faculty_portal_attendance',
    'faculty_portal_exam',
    'faculty_portal_examcourse',
    'faculty_portal_examnotification',
    'faculty_portal_examroom',
    'faculty_portal_faculty',
    'faculty_portal_facultyexamassignment',
    'faculty_portal_room',
    'faculty_portal_seatallocation',
    'report',
    'room',
    'student',
    'student_portal_course',
    'student_portal_student',
    'student_portal_studentregcourse'
]

with connection.cursor() as cursor:
    # Drop old tables
    print("\nDropping old tables:")
    print("-" * 50)
    for table in old_tables:
        try:
            cursor.execute(f"DROP TABLE IF EXISTS {table};")
            print(f"Dropped table: {table}")
        except Exception as e:
            print(f"Error dropping {table}: {e}")

    # List remaining tables
    cursor.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'exam_db' 
        AND table_type = 'BASE TABLE'
        ORDER BY table_name;
    """)
    tables = cursor.fetchall()

    print("\nRemaining Tables:")
    print("-" * 50)
    for i, table in enumerate(tables, 1):
        print(f"{i}. {table[0]}")
    print("-" * 50)
    print(f"Total Tables: {len(tables)}")
