import os
import django
from django.db import connection

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'exam_system.settings')
django.setup()

def show_tables():
    with connection.cursor() as cursor:
        # Get the database name
        db_name = connection.settings_dict['NAME']
        
        # Show all tables
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        
        print(f"\nTables in database '{db_name}':")
        print("-" * 50)
        
        for table in tables:
            table_name = table[0]
            print(f"\nTable: {table_name}")
            
            # Show table structure
            cursor.execute(f"DESCRIBE {table_name}")
            columns = cursor.fetchall()
            
            print("-" * 30)
            print("Column Name".ljust(20) + "Type".ljust(20) + "Null".ljust(6) + "Key")
            print("-" * 30)
            
            for col in columns:
                name = col[0]
                type = col[1]
                null = "YES" if col[2] == "YES" else "NO"
                key = col[3] if col[3] else ""
                print(f"{name.ljust(20)}{str(type).ljust(20)}{null.ljust(6)}{key}")
            print()

if __name__ == '__main__':
    show_tables()