from django.db import models
from accounts.models import Student
from admin_portal.models.exam import Course, Exam


class CourseRegistration(models.Model):
    """
    Student course registrations
    """
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    registered_on = models.DateTimeField(auto_now_add=True)
    semester = models.IntegerField()
    year = models.IntegerField()

    class Meta:
        unique_together = ('student', 'course', 'semester', 'year')
        ordering = ['-year', '-semester']
        verbose_name = 'Course Registration'
        verbose_name_plural = 'Course Registrations'

    def __str__(self):
        return f"{self.student.reg_no} - {self.course.code} ({self.semester})"


class ExamResult(models.Model):
    """
    Student exam results/grades
    """
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE)
    marks = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True)
    grade = models.CharField(max_length=2, blank=True)
    remarks = models.TextField(blank=True)
    published = models.BooleanField(default=False)

    class Meta:
        unique_together = ('student', 'exam')
        ordering = ['-exam__date']
        verbose_name = 'Exam Result'
        verbose_name_plural = 'Exam Results'

    def __str__(self):
        return f"{self.student.reg_no} - {self.exam.name} - {self.grade or 'N/A'}"
