from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.db import transaction, IntegrityError
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.utils import timezone
import csv
import io

from student_portal.models import Student, Course
from faculty_portal.models import Faculty, Exam
from .models import Room, ExamNotification
from .utils.email_utils import send_exam_notification


@login_required
def room_allocation(request):
    return render(request, 'admin_portal/roomalloc.html')


# --- Room Detail/Edit/Delete Views ---


@login_required
def room_view(request, pk):
    room = get_object_or_404(Room, pk=pk)
    return render(request, 'admin_portal/room_detail.html', {'room': room})


@login_required
def room_edit(request, pk):
    room = get_object_or_404(Room, pk=pk)
    # Add form handling logic here if needed
    return render(request, 'admin_portal/room_edit.html', {'room': room})


@login_required
def room_delete(request, pk):
    room = get_object_or_404(Room, pk=pk)
    # Add delete logic here if needed
    return render(request, 'admin_portal/room_delete.html', {'room': room})


# Updated Room CSV headers and mappings, improved error handling
EXPECTED_HEADERS = {
    'student': ['student id', 'name', 'department', 'study year', 'semester', 'mobile', 'email'],
    'faculty': ['faculty id', 'name', 'department', 'mobile', 'email'],
    'room': ['room id', 'block', 'room capacity', 'rows count', 'columns count']
}

# --- CSV Upload View ---


@csrf_exempt
def upload_csv(request):
    if request.method == 'POST':
        try:
            entity_type = request.GET.get('type')
            csv_file_content = request.body.decode('utf-8')
            csv_data = io.StringIO(csv_file_content)
            reader = csv.reader(csv_data)
            headers = [h.strip().lower() for h in next(reader)]
            expected_headers = EXPECTED_HEADERS.get(entity_type)
            if not expected_headers:
                return JsonResponse({'status': 'error', 'message': 'Invalid entity type specified.'}, status=400)
            missing_headers = [h for h in expected_headers if h not in headers]
            if missing_headers:
                return JsonResponse({
                    'status': 'error',
                    'message': f"Missing required columns in CSV: {', '.join(missing_headers)}. Expected: {', '.join(expected_headers)}."
                }, status=400)
            header_to_model_map = {
                'student': {
                    'student id': 'student_id', 'name': 'name', 'department': 'department',
                    'study year': 'study_year', 'semester': 'semester', 'mobile': 'mobile', 'email': 'email'
                },
                'faculty': {
                    'faculty id': 'faculty_id', 'name': 'name', 'department': 'department',
                    'mobile': 'mobile', 'email': 'email'
                },
                'room': {
                    'room id': 'room_id', 'block': 'block', 'room capacity': 'capacity',
                    'rows count': 'rowscount', 'columns count': 'columnscount'
                }
            }[entity_type]
            Model = {
                'student': Student,
                'faculty': Faculty,
                'room': Room
            }.get(entity_type)
            if not Model:
                return JsonResponse({'status': 'error', 'message': 'Unknown entity type for processing.'}, status=400)
            rows_to_create = []
            issues_detected = []
            line_num = 1
            existing_identifiers = set()
            if entity_type == 'student':
                existing_identifiers = set(
                    Student.objects.values_list('student_id', flat=True))
            elif entity_type == 'faculty':
                existing_identifiers = set(
                    Faculty.objects.values_list('faculty_id', flat=True))
            elif entity_type == 'room':
                existing_identifiers = set(
                    Room.objects.values_list('room_id', flat=True))
            existing_full_rows = set()
            for obj in Model.objects.all():
                existing_full_rows.add(obj.get_unique_row_tuple())
            for row in reader:
                line_num += 1
                row_data = {}
                current_row_errors = []
                if len(row) != len(headers):
                    current_row_errors.append(
                        f"Row has incorrect number of columns on line {line_num}. Expected {len(headers)}, got {len(row)}.")
                    issues_detected.extend(current_row_errors)
                    continue
                for i, cell_value in enumerate(row):
                    csv_header = headers[i]
                    model_field_name = header_to_model_map.get(csv_header)
                    if model_field_name:
                        row_data[model_field_name] = cell_value.strip()
                if entity_type == 'student':
                    required_fields = [
                        'student_id', 'name', 'department', 'study_year', 'semester', 'email']
                    for field in required_fields:
                        if not row_data.get(field):
                            current_row_errors.append(
                                f"Missing required data for '{field}' on line {line_num}.")
                    try:
                        if 'study_year' in row_data:
                            row_data['study_year'] = int(
                                row_data['study_year'])
                        else:
                            current_row_errors.append(
                                f"Missing 'study year' on line {line_num}.")
                    except (ValueError, TypeError):
                        current_row_errors.append(
                            f"Invalid 'study year' value on line {line_num}. Must be an integer.")
                    if not (row_data.get('student_id') and len(row_data['student_id']) == 10 and row_data['student_id'].isdigit()):
                        current_row_errors.append(
                            f"Invalid 'student id' format on line {line_num}. Must be a 10-digit number.")
                elif entity_type == 'faculty':
                    required_fields = ['faculty_id',
                                       'name', 'department', 'email']
                    for field in required_fields:
                        if not row_data.get(field):
                            current_row_errors.append(
                                f"Missing required data for '{field}' on line {line_num}.")
                    if not (row_data.get('faculty_id') and len(row_data['faculty_id']) == 4 and row_data['faculty_id'].isdigit()):
                        current_row_errors.append(
                            f"Invalid 'faculty id' format on line {line_num}. Must be a 4-digit number.")
                elif entity_type == 'room':
                    required_fields = ['room_id', 'block', 'capacity']
                    for field in required_fields:
                        if not row_data.get(field):
                            current_row_errors.append(
                                f"Missing required data for '{field}' on line {line_num}.")
                    try:
                        if 'capacity' in row_data:
                            row_data['capacity'] = int(row_data['capacity'])
                        else:
                            current_row_errors.append(
                                f"Missing 'room capacity' on line {line_num}.")
                    except (ValueError, TypeError):
                        current_row_errors.append(
                            f"Invalid 'room capacity' value on line {line_num}. Must be an integer.")
                    for optional_int_field in ['rowscount', 'columnscount']:
                        val = row_data.get(optional_int_field)
                        if val:
                            try:
                                row_data[optional_int_field] = int(val)
                            except (ValueError, TypeError):
                                current_row_errors.append(
                                    f"Invalid '{optional_int_field}' value on line {line_num}. Must be an integer or empty.")
                        else:
                            row_data[optional_int_field] = None
                if current_row_errors:
                    issues_detected.extend(current_row_errors)
                    continue
                model_fields_for_tuple = [
                    f.name for f in Model._meta.fields if f.name != 'id']
                temp_obj_data = {
                    k: v for k, v in row_data.items() if k in model_fields_for_tuple}
                for field_name in Model().get_unique_row_tuple()._fields if hasattr(Model().get_unique_row_tuple(), '_fields') else Model().get_unique_row_tuple():
                    if field_name not in temp_obj_data and hasattr(Model, field_name) and getattr(Model, field_name).field.null:
                        temp_obj_data[field_name] = None
                try:
                    current_row_tuple = Model(
                        **temp_obj_data).get_unique_row_tuple()
                except Exception as e:
                    issues_detected.append(
                        f"Error preparing row for duplicate check on line {line_num}: {e}")
                    continue
                if current_row_tuple in existing_full_rows:
                    issues_detected.append(
                        f"Skipping duplicate row (all fields match existing record) on line {line_num}.")
                    continue
                main_identifier_field = {
                    'student': 'student_id',
                    'faculty': 'faculty_id',
                    'room': 'room_id'
                }[entity_type]
                if row_data.get(main_identifier_field) in existing_identifiers:
                    issues_detected.append(
                        f"Skipping row with duplicate {main_identifier_field}: '{row_data.get(main_identifier_field)}' on line {line_num}.")
                    continue
                rows_to_create.append(row_data)
            if not rows_to_create and issues_detected:
                return JsonResponse({'status': 'error', 'message': 'No new valid data found in CSV to upload. Issues: ' + '; '.join(issues_detected)}, status=400)
            elif not rows_to_create and not issues_detected:
                return JsonResponse({'status': 'error', 'message': 'CSV file is empty or contains no valid data rows after headers.'}, status=400)
            with transaction.atomic():
                for data in rows_to_create:
                    Model.objects.create(**data)
            success_message = f"Successfully uploaded {len(rows_to_create)} new {entity_type} records."
            if issues_detected:
                success_message += f" (Note: {len(issues_detected)} row(s) had issues: {'; '.join(issues_detected[:5])}{'...' if len(issues_detected) > 5 else ''})"
            return JsonResponse({'status': 'success', 'message': success_message})
        except StopIteration:
            return JsonResponse({'status': 'error', 'message': 'CSV file is empty or contains only headers.'}, status=400)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': f'An unexpected error occurred during processing: {str(e)}'}, status=500)
    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'}, status=405)


def student_list(request):
    students = Student.objects.all()
    return render(request, 'admin_portal/student.html', {'students': students})


def student_view(request, pk):
    # Using id instead of student_id
    student = get_object_or_404(Student, id=pk)
    return render(request, 'admin_portal/student_detail.html', {'student': student})


def student_edit(request, pk):
    student = get_object_or_404(Student, student_id=pk)
    # Add form handling logic here if needed
    return render(request, 'admin_portal/student_edit.html', {'student': student})


def student_delete(request, pk):
    student = get_object_or_404(Student, student_id=pk)
    # Add delete logic here if needed
    return render(request, 'admin_portal/student_delete.html', {'student': student})


def student_list(request):
    students = Student.objects.select_related('user').all()
    return render(request, 'admin_portal/student.html', {'students': students})


def faculty_list(request):
    faculties = Faculty.objects.select_related('user').all()
    return render(request, 'admin_portal/faculty.html', {'faculties': faculties})


def faculty_view(request, pk):
    faculty = Faculty.objects.get(faculty_id=pk)
    return render(request, 'admin_portal/faculty_detail.html', {'faculty': faculty})


def faculty_edit(request, pk):
    faculty = Faculty.objects.get(faculty_id=pk)
    # Add form handling logic here if needed
    return render(request, 'admin_portal/faculty_edit.html', {'faculty': faculty})


def faculty_delete(request, pk):
    faculty = Faculty.objects.get(faculty_id=pk)
    # Add delete logic here if needed
    return render(request, 'admin_portal/faculty_delete.html', {'faculty': faculty})


@login_required
def dashboard(request):
    return render(request, 'admin_portal/dashboard.html')


@login_required
def students(request):
    return render(request, 'admin_portal/student.html')


@login_required
def faculty(request):
    return render(request, 'admin_portal/faculty.html')


@login_required
def courses(request):
    courses = Course.objects.all()
    return render(request, 'admin_portal/courses.html', {'courses': courses})


@login_required
def rooms(request):
    from .models import Room
    rooms = Room.objects.all()
    return render(request, 'admin_portal/rooms.html', {'rooms': rooms})


@login_required
def exams(request):
    return render(request, 'admin_portal/exams.html')


@login_required
def notifications(request):
    # Get upcoming exams (exams that haven't happened yet)
    upcoming_exams = Exam.objects.filter(
        exam_date__gte=timezone.now().date()
    ).prefetch_related(
        'examcourse_set__course'  # Use prefetch_related for many-to-many through relationship
    ).order_by('exam_date', 'start_time')

    # Add last notification information to each exam
    for exam in upcoming_exams:
        exam.last_notification = ExamNotification.objects.filter(
            exam=exam,
            status='SENT'
        ).order_by('-sent_at').first()

    # Get notification history
    notification_history = ExamNotification.objects.select_related(
        'exam'
    ).prefetch_related(
        'exam__examcourse_set__course'  # Prefetch related courses for each exam
    ).order_by('-sent_at')[:50]

    context = {
        'upcoming_exams': upcoming_exams,
        'notification_history': notification_history,
    }
    return render(request, 'admin_portal/notifications.html', context)


@login_required
@require_POST
def send_exam_notification_view(request, exam_id):
    try:
        exam = Exam.objects.get(id=exam_id)

        # Create notification record
        notification = ExamNotification.objects.create(
            exam=exam,
            status='PENDING'
        )

        try:
            # Send notifications
            recipients_count = send_exam_notification(exam)

            # Update notification record
            notification.status = 'SENT'
            notification.recipients_count = recipients_count
            notification.save()

            return JsonResponse({
                'success': True,
                'message': f'Successfully sent notifications to {recipients_count} recipients'
            })

        except Exception as e:
            notification.status = 'FAILED'
            notification.error_message = str(e)
            notification.save()
            return JsonResponse({
                'success': False,
                'error': str(e)
            })

    except Exam.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Exam not found'
        }, status=404)


@login_required
@require_POST
def resend_notification_view(request, notification_id):
    try:
        notification = ExamNotification.objects.get(id=notification_id)
        exam = notification.exam

        try:
            # Send notifications
            recipients_count = send_exam_notification(exam)

            # Create new notification record
            ExamNotification.objects.create(
                exam=exam,
                status='SENT',
                recipients_count=recipients_count
            )

            return JsonResponse({
                'success': True,
                'message': f'Successfully resent notifications to {recipients_count} recipients'
            })

        except Exception as e:
            ExamNotification.objects.create(
                exam=exam,
                status='FAILED',
                error_message=str(e)
            )
            return JsonResponse({
                'success': False,
                'error': str(e)
            })

    except ExamNotification.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Notification not found'
        }, status=404)


@login_required
def attendance(request):
    return render(request, 'admin_portal/attendence.html')


@login_required
def report(request):
    return render(request, 'admin_portal/report.html')


@login_required
def settings(request):
    return render(request, 'admin_portal/settings.html')


@login_required
def coursereg(request):
    return render(request, 'admin_portal/coursereg.html')
