from django.db import models
from django.utils import timezone
from django.conf import settings

from accounts.models import Department


class Course(models.Model):
    """
    Courses offered by departments
    """
    code = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=100)
    department = models.ForeignKey(
        Department, on_delete=models.CASCADE, null=True, blank=True)
    year = models.IntegerField(default=1)
    semester = models.IntegerField(default=1)

    def __str__(self):
        return f"{self.code} - {self.name}"


class Room(models.Model):
    """
    Examination rooms/halls
    """
    room_id = models.CharField(max_length=20, unique=True)
    block = models.CharField(max_length=50, null=True, blank=True)
    floor = models.IntegerField(default=0)
    rows = models.IntegerField(default=0)
    columns = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    has_power_backup = models.BooleanField(default=False)
    is_accessible = models.BooleanField(
        default=True, help_text="Wheelchair accessible")
    ac_available = models.BooleanField(default=False)
    projector_available = models.BooleanField(default=False)
    remarks = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def capacity(self):
        return self.rows * self.columns if self.rows > 0 and self.columns > 0 else 0

    def clean(self):
        from django.core.exceptions import ValidationError
        if self.rows < 0 or self.columns < 0:
            raise ValidationError("Rows and columns must be non-negative")

    def __str__(self):
        return f"{self.block} - {self.room_id} ({self.capacity} seats)"

    class Meta:
        ordering = ['block', 'room_id']


class Exam(models.Model):
    """
    Main examination model
    """
    EXAM_TYPES = [
        ('MID', 'Mid Semester'),
        ('END', 'End Semester'),
        ('SPL', 'Special Exam')
    ]

    name = models.CharField(max_length=200)
    exam_type = models.CharField(
        max_length=3, choices=EXAM_TYPES, default='END')
    date = models.DateField(null=True, blank=True)
    start_time = models.TimeField(null=True, blank=True)
    end_time = models.TimeField(null=True, blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.name} - {self.date}"


class ExamCourse(models.Model):
    """
    Courses included in an exam with their schedules
    """
    exam = models.ForeignKey(
        Exam, on_delete=models.CASCADE, related_name='courses')
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    max_marks = models.DecimalField(
        max_digits=5, decimal_places=2, default=100)
    pass_marks = models.DecimalField(
        max_digits=5, decimal_places=2, default=40)
    duration_mins = models.IntegerField(default=180)
    instructions = models.TextField(blank=True)
    question_paper_code = models.CharField(max_length=20, blank=True)
    has_practical = models.BooleanField(default=False)
    practical_date = models.DateField(null=True, blank=True)
    practical_duration_mins = models.IntegerField(null=True, blank=True)
    examiner = models.ForeignKey(
        'accounts.Faculty', on_delete=models.SET_NULL, null=True, related_name='examiner_courses')
    evaluator = models.ForeignKey(
        'accounts.Faculty', on_delete=models.SET_NULL, null=True, related_name='evaluator_courses')
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='created_exam_courses')

    class Meta:
        unique_together = ['exam', 'course']
        ordering = ['exam', 'course']

    def __str__(self):
        return f"{self.exam.name} - {self.course.code}"


class RoomAllocation(models.Model):
    """
    Room allocation for exams
    """
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    capacity_allocated = models.IntegerField()
    invigilator = models.ForeignKey(
        'accounts.Faculty', on_delete=models.SET_NULL, null=True)
    relief_invigilator = models.ForeignKey(
        'accounts.Faculty', on_delete=models.SET_NULL, null=True, related_name='relief_duties')
    start_time = models.TimeField(null=True, blank=True)
    end_time = models.TimeField(null=True, blank=True)
    reporting_time = models.TimeField(null=True, blank=True)
    instructions = models.TextField(blank=True)
    is_final = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='created_room_allocations')
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='updated_room_allocations')

    class Meta:
        unique_together = ['exam', 'room']
        ordering = ['exam', 'room']

    def clean(self):
        from django.core.exceptions import ValidationError
        if self.capacity_allocated > self.room.capacity:
            raise ValidationError(
                "Allocated capacity cannot exceed room capacity")
        if self.invigilator and self.relief_invigilator and self.invigilator == self.relief_invigilator:
            raise ValidationError(
                "Invigilator and relief invigilator cannot be the same person")

    def __str__(self):
        return f"{self.exam.name} - {self.room.room_id}"


class SeatAllocation(models.Model):
    """
    Student seating arrangements
    """
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE)
    student = models.ForeignKey('accounts.Student', on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    row = models.IntegerField()
    column = models.IntegerField()
    special_arrangement = models.BooleanField(default=False)
    arrangement_notes = models.TextField(
        blank=True, help_text="Any special seating requirements")
    qr_code = models.ImageField(
        upload_to='seat_qrcodes/', null=True, blank=True)
    allocated_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    allocated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='created_seat_allocations')

    class Meta:
        unique_together = [
            ['exam', 'student'],
            ['exam', 'room', 'row', 'column']
        ]
        ordering = ['exam', 'room', 'row', 'column']

    def clean(self):
        from django.core.exceptions import ValidationError
        if self.row < 0 or self.column < 0:
            raise ValidationError("Row and column must be non-negative")
        if self.row >= self.room.rows:
            raise ValidationError(
                f"Row number cannot exceed room's rows ({self.room.rows})")
        if self.column >= self.room.columns:
            raise ValidationError(
                f"Column number cannot exceed room's columns ({self.room.columns})")

    def get_seat_label(self):
        """Returns human-readable seat label like 'A1', 'B2' etc"""
        row_label = chr(65 + self.row) if self.row < 26 else f"R{self.row+1}"
        return f"{row_label}{self.column+1}"

    def __str__(self):
        return f"{self.student.reg_no} - {self.room.room_id} ({self.get_seat_label()})"


class ExamNotification(models.Model):
    """
    Exam notifications and announcements
    """
    NOTIFICATION_STATUS = [
        ('DRAFT', 'Draft'),
        ('SCHEDULED', 'Scheduled'),
        ('SENT', 'Sent'),
        ('FAILED', 'Failed')
    ]

    exam = models.ForeignKey(Exam, on_delete=models.CASCADE)
    title = models.CharField(max_length=200, null=True, blank=True)
    message = models.TextField(null=True, blank=True)
    send_to_students = models.BooleanField(default=True)
    send_to_faculty = models.BooleanField(default=True)
    scheduled_for = models.DateTimeField(null=True, blank=True)
    status = models.CharField(
        max_length=10, choices=NOTIFICATION_STATUS, default='DRAFT')
    recipients_count = models.IntegerField(default=0)
    error_message = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    sent_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.exam.name} - {self.title}"
