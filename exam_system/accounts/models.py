from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from django.core.validators import RegexValidator


class Department(models.Model):
    """
    Academic departments in the institution
    """
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=10, unique=True)
    established_date = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Department'
        verbose_name_plural = 'Departments'
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.code})"


class User(AbstractUser):
    ROLES = [
        ('ADMIN', 'Administrator'),
        ('FACULTY', 'Faculty Member'),
        ('STUDENT', 'Student'),
        ('STAFF', 'Non-Teaching Staff')
    ]

    role = models.CharField(max_length=10, choices=ROLES, default='STUDENT')
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    last_login_ip = models.GenericIPAddressField(null=True, blank=True)

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def __str__(self):
        return f"{self.get_full_name()} ({self.get_role_display()})"


class Student(models.Model):
    """
    Student profile with academic details
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    reg_no = models.CharField(max_length=20, unique=True)
    department = models.ForeignKey(
        Department, on_delete=models.PROTECT, null=True, blank=True)
    year = models.IntegerField(null=True, blank=True)
    semester = models.IntegerField(null=True, blank=True)
    section = models.CharField(max_length=1, blank=True, default='A')
    date_of_birth = models.DateField(null=True, blank=True)
    phone = models.CharField(max_length=15, validators=[
        RegexValidator(regex=r'^\+?1?\d{9,15}$')
    ], blank=True, null=True)
    guardian_name = models.CharField(
        max_length=100, blank=True, null=True, default='')
    guardian_phone = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True, default='')
    blood_group = models.CharField(max_length=5, blank=True, null=True)
    medical_conditions = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = 'Student'
        verbose_name_plural = 'Students'
        ordering = ['reg_no']
        unique_together = ['department', 'year',
                           'semester', 'section', 'reg_no']

    def __str__(self):
        return f"{self.reg_no} - {self.user.get_full_name()}"

    @property
    def email(self):
        return self.user.email


class Faculty(models.Model):
    """
    Faculty members (teachers, professors, etc.)
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    emp_id = models.CharField(max_length=20, unique=True)
    department = models.ForeignKey(
        Department, on_delete=models.PROTECT, null=True, blank=True)
    designation = models.CharField(max_length=100, blank=True, default='')
    specialization = models.CharField(max_length=200, blank=True)
    qualification = models.CharField(max_length=100, blank=True, default='')
    date_joined = models.DateField(null=True, blank=True)
    phone = models.CharField(max_length=15, validators=[
        RegexValidator(regex=r'^\+?1?\d{9,15}$')
    ], blank=True, null=True)
    emergency_contact = models.CharField(max_length=15, blank=True)
    available_for_invigilation = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Faculty'
        verbose_name_plural = 'Faculty'
        ordering = ['emp_id']

    def __str__(self):
        return f"{self.emp_id} - {self.user.get_full_name()}"

    @property
    def email(self):
        return self.user.email


class StudentProfile(models.Model):
    """
    Additional student details that aren't essential for the core system
    """
    student = models.OneToOneField(Student, on_delete=models.CASCADE)
    extra_curricular = models.TextField(blank=True)
    achievements = models.TextField(blank=True)
    certifications = models.TextField(blank=True)
    internships = models.TextField(blank=True)
    projects = models.TextField(blank=True)
    skills = models.TextField(blank=True)
    hobbies = models.TextField(blank=True)
    linkedin = models.URLField(blank=True)
    github = models.URLField(blank=True)
    portfolio = models.URLField(blank=True)

    class Meta:
        verbose_name = 'Student Profile'
        verbose_name_plural = 'Student Profiles'

    def __str__(self):
        return f"Profile of {self.student.reg_no}"


class FacultyProfile(models.Model):
    """
    Additional faculty details that aren't essential for the core system
    """
    faculty = models.OneToOneField(Faculty, on_delete=models.CASCADE)
    research_interests = models.TextField(blank=True)
    publications = models.TextField(blank=True)
    projects = models.TextField(blank=True)
    awards = models.TextField(blank=True)
    teaching_experience = models.TextField(blank=True)
    industry_experience = models.TextField(blank=True)
    memberships = models.TextField(blank=True)
    linkedin = models.URLField(blank=True)
    google_scholar = models.URLField(blank=True)
    personal_website = models.URLField(blank=True)

    class Meta:
        verbose_name = 'Faculty Profile'
        verbose_name_plural = 'Faculty Profiles'

    def __str__(self):
        return f"Profile of {self.faculty.emp_id}"


class Notification(models.Model):
    """
    System notifications for users
    """
    NOTIFICATION_TYPES = [
        ('INFO', 'Information'),
        ('WARNING', 'Warning'),
        ('ERROR', 'Error'),
        ('SUCCESS', 'Success')
    ]

    recipient = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    message = models.TextField()
    notification_type = models.CharField(
        max_length=10, choices=NOTIFICATION_TYPES, default='INFO')
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.recipient.username} - {self.title}"


class Log(models.Model):
    """
    System-wide audit log
    """
    ACTION_TYPES = [
        ('CREATE', 'Create'),
        ('UPDATE', 'Update'),
        ('DELETE', 'Delete'),
        ('LOGIN', 'Login'),
        ('LOGOUT', 'Logout'),
        ('OTHER', 'Other')
    ]

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    action = models.CharField(max_length=10, choices=ACTION_TYPES)
    # e.g., 'Student', 'Exam', etc.
    entity_type = models.CharField(max_length=100, default='OTHER')
    entity_id = models.IntegerField(null=True)
    description = models.TextField(blank=True, default='')
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username if self.user else 'System'} - {self.action} - {self.created_at}"
