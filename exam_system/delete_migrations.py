import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'exam_system.settings')
django.setup()


def delete_migrations():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    apps = ['accounts', 'faculty_portal', 'student_portal']

    for app in apps:
        migrations_dir = os.path.join(base_dir, app, 'migrations')
        if os.path.exists(migrations_dir):
            for filename in os.listdir(migrations_dir):
                if filename.endswith('.py') and filename != '__init__.py':
                    os.remove(os.path.join(migrations_dir, filename))
                    print(f"Deleted {app}/migrations/{filename}")


if __name__ == '__main__':
    delete_migrations()
