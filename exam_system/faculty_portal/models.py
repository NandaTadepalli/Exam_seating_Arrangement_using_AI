
from django.db import models
from accounts.models import User
from .student_models import Student


class Exam(models.Model):
    date = models.DateField()
    time = models.TimeField()
    room_number = models.CharField(max_length=20)
    block_name = models.CharField(max_length=50)
    course = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.course} on {self.date} at {self.time}"


class InvigilationDuty(models.Model):
    faculty = models.ForeignKey(
        User, on_delete=models.CASCADE, limit_choices_to={'role': 'faculty'})
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE)
    notification = models.TextField(blank=True)

    def __str__(self):
        return f"{self.faculty.username} - {self.exam}"


class Attendance(models.Model):
    invigilation = models.ForeignKey(
        InvigilationDuty, on_delete=models.CASCADE)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    present = models.BooleanField(default=False)


class MalpracticeReport(models.Model):
    attendance = models.ForeignKey(Attendance, on_delete=models.CASCADE)
    malpractice_type = models.CharField(max_length=100)
    description = models.TextField()
    evidence = models.FileField(
        upload_to='malpractice_evidence/', blank=True, null=True)
    reported_at = models.DateTimeField(auto_now_add=True)
