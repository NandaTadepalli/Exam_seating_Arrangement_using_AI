from django.db import models
from django.utils import timezone
from faculty_portal.models import Exam


class ExamNotification(models.Model):
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE)
    sent_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=[
        ('PENDING', 'Pending'),
        ('SENT', 'Sent'),
        ('FAILED', 'Failed')
    ])
    recipients_count = models.IntegerField(default=0)
    error_message = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ['-sent_at']

    def __str__(self):
        return f"Notification for {self.exam.exam_name} - {self.get_status_display()}"
