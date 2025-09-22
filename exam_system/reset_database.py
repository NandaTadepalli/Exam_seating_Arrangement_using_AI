import os
import pymysql
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'exam_system.settings')
django.setup()

from django.conf import settings

def reset_db():
    # Get database settings
    db_settings = settings.DATABASES['default']
    
    # Create a connection to MySQL without selecting a database
    connection = pymysql.connect(
        host=db_settings['HOST'] or 'localhost',
        user=db_settings['USER'],
        password=db_settings['PASSWORD']
    )
    
    try:
        with connection.cursor() as cursor:
            # Drop database if it exists
            cursor.execute(f"DROP DATABASE IF EXISTS {db_settings['NAME']}")
            # Create database with proper character set
            cursor.execute(
                f"CREATE DATABASE {db_settings['NAME']} "
                "CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
            )
            print(f"Database {db_settings['NAME']} has been reset successfully.")
    finally:
        connection.close()

if __name__ == '__main__':
    reset_db()