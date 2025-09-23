from django.db import connection
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'exam_system.settings')
django.setup()


with connection.cursor() as cursor:
    cursor.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'exam_db' 
        AND table_type = 'BASE TABLE'
        ORDER BY table_name;
    """)
    tables = cursor.fetchall()

print("\nDatabase Tables:")
print("-" * 50)
for i, table in enumerate(tables, 1):
    print(f"{i}. {table[0]}")
print("-" * 50)
print(f"Total Tables: {len(tables)}")
