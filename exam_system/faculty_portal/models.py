
from django.db import models
from django.utils import timezone
from django.conf import settings
from accounts.models import User, Faculty, Student
from admin_portal.models.exam import Exam, Room


class ExamLog(models.Model):
    """
    Audit log for exam-related actions
    """
    ACTION_TYPES = [
        ('START', 'Started'),
        ('PAUSE', 'Paused'),
        ('RESUME', 'Resumed'),
        ('END', 'Ended'),
        ('INCIDENT', 'Incident'),
        ('OTHER', 'Other')
    ]

    exam = models.ForeignKey(Exam, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE, null=True)
    action = models.CharField(max_length=10, choices=ACTION_TYPES)
    description = models.TextField()
    logged_by = models.ForeignKey(
        Faculty, on_delete=models.SET_NULL, null=True)
    logged_at = models.DateTimeField(auto_now_add=True)
    affected_students = models.ManyToManyField(Student, blank=True)

    class Meta:
        ordering = ['-logged_at']
        verbose_name = 'Exam Log'
        verbose_name_plural = 'Exam Logs'

    def __str__(self):
        return f"{self.exam.name} - {self.get_action_display()} - {self.logged_at}"


class AttendanceRecord(models.Model):
    """
    Student attendance for exams marked by faculty
    """
    ATTENDANCE_STATUS = (
        ('PRESENT', 'Present'),
        ('ABSENT', 'Absent'),
        ('LATE', 'Late')
    )

    exam = models.ForeignKey(Exam, on_delete=models.CASCADE)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    status = models.CharField(
        max_length=10, choices=ATTENDANCE_STATUS, default='ABSENT')
    marked_by = models.ForeignKey(Faculty, on_delete=models.CASCADE)
    marked_at = models.DateTimeField(default=timezone.now)
    remarks = models.TextField(blank=True)

    class Meta:
        unique_together = ('exam', 'student')
        ordering = ['-marked_at']
        verbose_name = 'Attendance Record'
        verbose_name_plural = 'Attendance Records'

    def __str__(self):
        return f"{self.student.reg_no} - {self.exam.name} - {self.get_status_display()}"


class MalpracticeReport(models.Model):
    """
    Reports of malpractice during exams submitted by faculty
    """
    SEVERITY_LEVELS = (
        ('LOW', 'Low'),
        ('MEDIUM', 'Medium'),
        ('HIGH', 'High'),
        ('SEVERE', 'Severe')
    )

    STATUS_CHOICES = (
        ('REPORTED', 'Reported'),
        ('INVESTIGATING', 'Under Investigation'),
        ('ACTION_PENDING', 'Action Pending'),
        ('RESOLVED', 'Resolved'),
        ('DISMISSED', 'Dismissed')
    )

    exam = models.ForeignKey(
        Exam, on_delete=models.CASCADE, null=True, blank=True)
    student = models.ForeignKey(
        Student, on_delete=models.CASCADE, null=True, blank=True)
    reported_by = models.ForeignKey(
        Faculty, on_delete=models.CASCADE, null=True, blank=True, related_name='reported_incidents')
    room = models.ForeignKey(
        Room, on_delete=models.CASCADE, null=True, blank=True)
    severity = models.CharField(
        max_length=10, choices=SEVERITY_LEVELS, default='LOW')
    description = models.TextField(blank=True)
    status = models.CharField(
        max_length=15, choices=STATUS_CHOICES, default='REPORTED')

    # Evidence files
    primary_evidence = models.FileField(
        upload_to='malpractice_evidence/',
        help_text="Main evidence file",
        null=True,
        blank=True
    )
    additional_evidence = models.ManyToManyField(
        'MalpracticeEvidence', blank=True)
    witness_statements = models.ManyToManyField('WitnessStatement', blank=True)

    # Timestamps
    reported_at = models.DateTimeField(default=timezone.now)
    investigation_started_at = models.DateTimeField(null=True, blank=True)
    action_taken_at = models.DateTimeField(null=True, blank=True)
    resolved_at = models.DateTimeField(null=True, blank=True)

    # Resolution details
    action_taken = models.TextField(blank=True)
    penalty_imposed = models.TextField(blank=True)
    resolved = models.BooleanField(default=False)
    resolved_by = models.ForeignKey(
        Faculty, on_delete=models.SET_NULL, null=True, related_name='resolved_incidents')
    committee_remarks = models.TextField(blank=True)
    appeal_filed = models.BooleanField(default=False)
    appeal_status = models.TextField(blank=True)

    # Audit fields
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
                                   null=True, blank=True, related_name='created_reports')
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
                                   null=True, blank=True, related_name='updated_reports')

    class Meta:
        ordering = ['-reported_at']
        verbose_name = 'Malpractice Report'
        verbose_name_plural = 'Malpractice Reports'

    def __str__(self):
        return f"{self.student.reg_no} - {self.exam.name} - {self.severity}"


class MalpracticeEvidence(models.Model):
    """
    Additional evidence files for malpractice reports
    """
    file = models.FileField(
        upload_to='malpractice_evidence/',
        null=True,
        blank=True
    )
    description = models.TextField(blank=True)
    uploaded_at = models.DateTimeField(default=timezone.now)
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)

    class Meta:
        ordering = ['-uploaded_at']

    def __str__(self):
        return f"Evidence uploaded at {self.uploaded_at}"


class WitnessStatement(models.Model):
    """
    Witness statements for malpractice reports
    """
    witness = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='witness_statements')
    statement = models.TextField()
    recorded_at = models.DateTimeField(auto_now_add=True)
    recorded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='recorded_statements')
    is_verified = models.BooleanField(default=False)
    verification_date = models.DateTimeField(null=True, blank=True)
    verification_remarks = models.TextField(blank=True)

    class Meta:
        ordering = ['-recorded_at']

    def __str__(self):
        return f"Statement by {self.witness.get_full_name()} at {self.recorded_at}"
