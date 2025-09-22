
from django.db import models
from django.utils import timezone
from accounts.models import User
from student_portal.models import Student, Course

class Faculty(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    department = models.CharField(max_length=50)
    designation = models.CharField(max_length=50)
    phone = models.CharField(max_length=15)
    available = models.BooleanField(default=True)

    class Meta:
        verbose_name_plural = 'Faculty'

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.department}"

class Room(models.Model):
    block = models.CharField(max_length=50)
    room_number = models.CharField(max_length=20, unique=True)
    rows_count = models.IntegerField()
    columns_count = models.IntegerField()

    @property
    def capacity(self):
        return self.rows_count * self.columns_count

    def __str__(self):
        return f"{self.block} - {self.room_number}"

class Exam(models.Model):
    EXAM_TYPES = (
        ('THEORY', 'Theory'),
        ('PRACTICAL', 'Practical'),
    )
    exam_name = models.CharField(max_length=100)
    exam_type = models.CharField(max_length=10, choices=EXAM_TYPES, default='THEORY')
    year = models.IntegerField(default=1)
    semester = models.IntegerField(default=1)
    exam_date = models.DateField(null=True, blank=True)
    start_time = models.TimeField(null=True, blank=True)
    end_time = models.TimeField(null=True, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.PROTECT, null=True, blank=True)


class ExamCourse(models.Model):
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('exam', 'course')

    def __str__(self):
        return f"{self.exam.exam_name} - {self.course.course_code}"

class ExamRoom(models.Model):
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    allocated_capacity = models.IntegerField()

    class Meta:
        unique_together = ('exam', 'room')

    def __str__(self):
        return f"{self.exam.exam_name} - {self.room.room_number}"

class SeatAllocation(models.Model):
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    row_number = models.IntegerField()
    column_number = models.IntegerField()

    @property
    def seat_id(self):
        return f"R{self.room.id}{self.row_number}{self.column_number}"

    class Meta:
        unique_together = ('exam', 'student')

    def __str__(self):
        return f"{self.student.user.username} - {self.seat_id}"

class FacultyExamAssignment(models.Model):
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE)
    faculty = models.ForeignKey(Faculty, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('exam', 'faculty', 'room')

    def __str__(self):
        return f"{self.faculty.user.get_full_name()} - {self.exam.exam_name} - {self.room.room_number}"

class Attendance(models.Model):
    ATTENDANCE_STATUS = (
        ('PRESENT', 'Present'),
        ('ABSENT', 'Absent'),
    )
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, null=True, blank=True)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE, null=True, blank=True)
    marked_by = models.ForeignKey(Faculty, on_delete=models.CASCADE, null=True, blank=True)
    status = models.CharField(max_length=10, choices=ATTENDANCE_STATUS, default='ABSENT')
    marked_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.student.user.username} - {self.status}"

class MalpracticeReport(models.Model):
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, null=True, blank=True)
    student = models.ForeignKey(Student, on_delete=models.CASCADE, null=True, blank=True)
    faculty = models.ForeignKey(Faculty, on_delete=models.CASCADE, null=True, blank=True)
    description = models.TextField()
    proof_url = models.URLField(max_length=255, blank=True)
    reported_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.student.user.username} - {self.exam.exam_name}"

class ExamNotification(models.Model):
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name='faculty_notifications')
    sent_at = models.DateTimeField(auto_now_add=True)
    recipients_count = models.IntegerField(default=0)
    status = models.CharField(max_length=20, choices=[
        ('PENDING', 'Pending'),
        ('SENT', 'Sent'),
        ('FAILED', 'Failed')
    ], default='PENDING')
    error_message = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = 'Faculty Exam Notification'
        verbose_name_plural = 'Faculty Exam Notifications'

    def __str__(self):
        return f"{self.exam.exam_name} - {self.get_status_display()} - {self.sent_at.strftime('%Y-%m-%d %H:%M')}"
