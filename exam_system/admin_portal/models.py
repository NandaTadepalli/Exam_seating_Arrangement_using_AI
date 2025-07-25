# --- Sample CSV Helper ---
def get_sample_csv(entity):
    if entity == 'student':
        return 'student id,name,department,study year,semester,mobile,email\n'
    elif entity == 'faculty':
        return 'faculty id,name,department,mobile,email\n'
    elif entity == 'room':
        return 'room id,block,room capacity,rows count,columns count\n'
    return ''

# --- Error Report Helper ---
def generate_error_csv(errors):
    import io, csv
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['Row', 'Error'])
    for err in errors:
        writer.writerow(err)
    return output.getvalue()
from django.db import models

# --- Faculty Model ---
class Faculty(models.Model):
    # Django will automatically create an 'id' AutoField as the primary key.
    # faculty_id will be a unique identifier, used for external reference.
    id = models.AutoField(primary_key=True) # Explicitly define Django's default PK for clarity
    faculty_id = models.CharField(max_length=20, unique=True, db_index=True) # Unique, indexed for lookups
    name = models.CharField(max_length=100)
    department = models.CharField(max_length=100)
    mobile = models.CharField(max_length=20, blank=True, null=True) # Mobile can be optional
    email = models.EmailField(max_length=254, unique=True) # Email should be unique and not null

    class Meta:
        db_table = 'faculty' # Explicitly set table name
        verbose_name_plural = 'Faculties' # Better plural name for Django Admin

    def __str__(self):
        return f"{self.name} ({self.faculty_id})"

    def get_unique_row_tuple(self):
        # Used for full row duplicate checking during CSV upload
        return (self.faculty_id, self.name, self.department, self.mobile, self.email)

# --- Student Model ---
class Student(models.Model):
    # 'id' is the auto-incrementing primary key (Django's default behavior)
    # 'student_id' is a separate unique identifier, used for display and lookups.
    id = models.AutoField(primary_key=True) # Django's default auto-incrementing PK
    student_id = models.CharField(max_length=20, unique=True, db_index=True) # Unique, indexed for lookups
    name = models.CharField(max_length=100)
    department = models.CharField(max_length=100)
    study_year = models.IntegerField()
    semester = models.CharField(max_length=20)
    mobile = models.CharField(max_length=20, blank=True, null=True) # Mobile can be optional
    email = models.EmailField(max_length=254, unique=True) # Email should be unique and not null

    class Meta:
        db_table = 'student' # Explicitly set table name
        verbose_name_plural = 'Students'

    def __str__(self):
        return f"{self.name} ({self.student_id})"

    def get_unique_row_tuple(self):
        # Used for full row duplicate checking during CSV upload
        return (self.student_id, self.name, self.department, self.study_year, self.semester, self.mobile, self.email)

# --- Room Model ---
class Room(models.Model):
    # 'id' is the auto-incrementing primary key (Django's default behavior)
    # 'room_id' is a separate unique identifier, matching your HTML and previous CSVs.
    id = models.AutoField(primary_key=True) # Django's default auto-incrementing PK
    room_id = models.CharField(max_length=20, unique=True, db_index=True) # Unique, indexed for lookups
    block = models.CharField(max_length=50)
    capacity = models.IntegerField()
    rowscount = models.IntegerField(blank=True, null=True) # Matches HTML template
    columnscount = models.IntegerField(blank=True, null=True) # Matches HTML template

    class Meta:
        db_table = 'room' # Explicitly set table name
        verbose_name_plural = 'Rooms'

    def __str__(self):
        return self.room_id

    def get_unique_row_tuple(self):
        # Used for full row duplicate checking during CSV upload
        return (self.room_id, self.block, self.capacity, self.rowscount, self.columnscount)

# --- Course Model ---
class Course(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, unique=True)
    # faculty is optional, so null=True and blank=True
    faculty = models.ForeignKey(Faculty, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        db_table = 'course'
        verbose_name_plural = 'Courses'

    def __str__(self):
        return f"{self.name} ({self.code})"

# --- Exam Model ---
class Exam(models.Model):
    name = models.CharField(max_length=100)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    date = models.DateField()
    # room is optional, so null=True and blank=True
    room = models.ForeignKey(Room, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        db_table = 'exam'
        verbose_name_plural = 'Exams'

    def __str__(self):
        return f"{self.name} ({self.date})"

# --- Notification Model ---
class Notification(models.Model):
    title = models.CharField(max_length=200)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True) # Automatically sets creation timestamp

    class Meta:
        db_table = 'notification'
        verbose_name_plural = 'Notifications'
        ordering = ['-created_at'] # Default ordering: newest notifications first

    def __str__(self):
        return self.title

# --- Attendance Model ---
class Attendance(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE)
    present = models.BooleanField(default=False)

    class Meta:
        db_table = 'attendance'
        verbose_name_plural = 'Attendance'
        # Ensures that a student can only have one attendance record per exam
        unique_together = ('student', 'exam')

    def __str__(self):
        return f"{self.student.name} - {self.exam.name}: {'Present' if self.present else 'Absent'}"

# --- Report Model ---
class Report(models.Model):
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE)
    generated_at = models.DateTimeField(auto_now_add=True)
    file = models.FileField(upload_to='reports/') # Files will be stored in your MEDIA_ROOT/reports/ directory

    class Meta:
        db_table = 'report'
        verbose_name_plural = 'Reports'
        ordering = ['-generated_at'] # Default ordering: newest reports first

    def __str__(self):
        return f"Report for {self.exam.name} on {self.generated_at.strftime('%Y-%m-%d')}"