import csv
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from accounts.models import User


class Command(BaseCommand):
    help = 'Import users from CSV with columns: username,email,password,user_id,first_name,last_name,role'

    def add_arguments(self, parser):
        parser.add_argument('csv_path', type=str, help='Path to users CSV file')

    def handle(self, *args, **options):
        path = options['csv_path']
        created = 0
        with open(path, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            required = {'username', 'email', 'password', 'user_id'}
            if not required.issubset(reader.fieldnames):
                raise CommandError('CSV must include at least: username,email,password,user_id')
            with transaction.atomic():
                for row in reader:
                    user_id = row['user_id'].strip()
                    username = row['username'].strip()
                    email = row['email'].strip()
                    password = row['password'].strip()
                    first_name = row.get('first_name', '').strip()
                    last_name = row.get('last_name', '').strip()
                    role = row.get('role', 'STUDENT').strip().upper()

                    user, created_flag = User.objects.update_or_create(
                        user_id=user_id,
                        defaults={
                            'username': username,
                            'email': email,
                            'first_name': first_name,
                            'last_name': last_name,
                            'role': role,
                        }
                    )
                    # set password
                    user.set_password(password)
                    user.save()
                    if created_flag:
                        created += 1
        self.stdout.write(self.style.SUCCESS(f'Imported/updated users. New created: {created}'))
