import os
import django
from django.db import connection

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'exam_system.settings')
django.setup()


def reset_db():
    with connection.cursor() as cursor:
        cursor.execute("DROP DATABASE IF EXISTS exam_system")
        cursor.execute(
            "CREATE DATABASE exam_system CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")


if __name__ == '__main__':
    reset_db()
