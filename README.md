# Exam Seating & Invigilation System

## Project Overview
A Django-based web application for managing exam seating, invigilation duties, attendance, and malpractice reporting. Includes portals for admin, faculty, and students.

## Features
- Custom user model with roles (admin, faculty, student)
- Faculty dashboard with invigilation schedule and notifications
- Attendance and malpractice reporting for exams
- Password reset and profile management
- MySQL database support

## Setup Instructions

### 1. Clone the repository
```sh
git clone <your-repo-url>
cd exam_system
```

### 2. Install dependencies
```sh
pip install -r requirements.txt
```

### 3. Configure MySQL Database
Edit `exam_system/settings.py`:
```
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': '<your_db_name>',
        'USER': '<your_mysql_user>',
        'PASSWORD': '<your_mysql_password>',
        'HOST': 'localhost',
        'PORT': '3306',
    }
}
```

### 4. Run migrations
```sh
python manage.py makemigrations
python manage.py migrate
```

### 5. Create a superuser
```sh
python manage.py createsuperuser
```

### 6. (Optional) Load sample data
```sh
python manage.py loaddata data.json
```

### 7. Run the development server
```sh
python manage.py runserver
```

## Contributing
- Fork the repo and create a feature branch
- Commit your changes and open a pull request

## Notes
- Do NOT commit your actual database or sensitive info
- Each collaborator should set up their own MySQL instance
- Use `data.json` for sharing sample data
