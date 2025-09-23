from django.db import models
from django.utils import timezone
from .base import BaseModel


class ExamCourse(BaseModel):
    """
    Course model for exams with improved relationships
    """
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, unique=True)
    credits = models.IntegerField(default=3)
    description = models.TextField(blank=True)

    # Faculty relationships
    coordinator = models.ForeignKey(
        'accounts.Faculty',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='coordinated_courses'
    )
    instructors = models.ManyToManyField(
        'accounts.Faculty',
        related_name='teaching_courses',
        blank=True
    )

    # Academic information
    prerequisites = models.ManyToManyField(
        'self',
        symmetrical=False,
        blank=True,
        related_name='is_prerequisite_for'
    )

    # Status
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'admin_portal_examcourse'
        verbose_name = 'Course'
        verbose_name_plural = 'Courses'
        ordering = ['code']

    def __str__(self):
        return f"{self.code} - {self.name}"


class ExamSession(BaseModel):
    """
    Represents an exam session for a course
    """
    course = models.ForeignKey(
        ExamCourse,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='exam_sessions'
    )
    name = models.CharField(max_length=100)
    date = models.DateTimeField(default=timezone.now)
    duration = models.DurationField(null=True, blank=True)
    max_marks = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True
    )
    passing_marks = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True
    )

    # Room allocation will be handled by separate model
    instructions = models.TextField(blank=True)
    materials_allowed = models.TextField(blank=True)

    # Status fields
    status = models.CharField(
        max_length=20,
        choices=[
            ('SCHEDULED', 'Scheduled'),
            ('IN_PROGRESS', 'In Progress'),
            ('COMPLETED', 'Completed'),
            ('CANCELLED', 'Cancelled')
        ],
        default='SCHEDULED'
    )

    class Meta:
        db_table = 'admin_portal_examsession'
        verbose_name = 'Exam Session'
        verbose_name_plural = 'Exam Sessions'
        ordering = ['-date']

    def __str__(self):
        return f"{self.course.code} - {self.name} ({self.date})"


class RoomAllocation(BaseModel):
    """
    Room allocation for exam sessions with seating arrangement
    """
    exam_session = models.ForeignKey(
        ExamSession,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='room_allocations'
    )
    room = models.ForeignKey(
        'admin_portal.Room',
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='exam_allocations'
    )
    invigilator = models.ForeignKey(
        'accounts.Faculty',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='invigilating_rooms'
    )

    # Seating arrangement
    capacity_used = models.IntegerField(null=True, blank=True, default=0)
    seating_plan = models.JSONField(default=dict, null=True, blank=True)

    # Status
    status = models.CharField(
        max_length=20,
        choices=[
            ('ALLOCATED', 'Allocated'),
            ('IN_USE', 'In Use'),
            ('COMPLETED', 'Completed'),
            ('CANCELLED', 'Cancelled')
        ],
        default='ALLOCATED'
    )

    # Notes and special instructions
    notes = models.TextField(blank=True)
    special_arrangements = models.TextField(blank=True)

    class Meta:
        db_table = 'admin_portal_roomallocation'
        verbose_name = 'Room Allocation'
        verbose_name_plural = 'Room Allocations'
        ordering = ['exam_session', 'room']
        # A room can only be allocated once per session
        unique_together = ['exam_session', 'room']

    def __str__(self):
        return f"{self.exam_session} - {self.room}"
