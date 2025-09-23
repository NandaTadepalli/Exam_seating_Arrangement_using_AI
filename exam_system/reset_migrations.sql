USE exam_db;
DELETE FROM django_migrations WHERE app IN ('admin_portal', 'faculty_portal', 'student_portal', 'accounts');