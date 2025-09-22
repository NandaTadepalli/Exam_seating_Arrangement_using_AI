from django.db import models
from accounts.models import User

class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    dob = models.DateField(null=True)
    GENDER_CHOICES = (
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    )
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, null=True)
    department = models.CharField(max_length=50)
    year = models.IntegerField()
    semester = models.IntegerField()
    phone = models.CharField(max_length=15)

    def __str__(self):
        return f"{self.user.username} - {self.department} Year {self.year}"

class Course(models.Model):
    course_code = models.CharField(max_length=20, unique=True)
    course_name = models.CharField(max_length=100)
    department = models.CharField(max_length=50)
    year = models.IntegerField()
    semester = models.IntegerField()

    def __str__(self):
        return f"{self.course_code} - {self.course_name}"

class StudentRegCourse(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('student', 'course')
        verbose_name = 'Student Course Registration'
        verbose_name_plural = 'Student Course Registrations'

    def __str__(self):
        return f"{self.student.user.username} - {self.course.course_code}"
