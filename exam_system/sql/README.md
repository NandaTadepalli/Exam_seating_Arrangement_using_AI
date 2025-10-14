This folder contains helper SQL to drop and recreate the `exam_db` and instructions to rebuild the schema and import users.

Steps (run locally on your development machine):

1. Drop & recreate DB (MySQL):

   mysql -u root -p < drop_create_db.sql

2. Run Django migrations to create schema and initial tables:

   python manage.py migrate

3. Import users from CSV using the management command:

   python manage.py import_users path/to/users.csv

  CSV must include at least columns: username,email,password,user_id. Include first_name,last_name,role if available.

4. Recreate any other data (seed scripts, fixtures) as needed.

Notes:
- This is destructive: it deletes the existing database. Make a backup if you ever want to keep existing data.
- After recreating DB and importing users, review relations: since we modified `accounts.models.User` to make `user_id` primary key, migrations should create the appropriate FK references pointing to `accounts_user.user_id`.
- If you face migration issues related to changing primary key fields, you can revert the change in `accounts/models.py` and re-run migrations on a fresh DB.
