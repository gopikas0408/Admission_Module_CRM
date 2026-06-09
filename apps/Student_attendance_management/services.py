from .models import Attendance
from apps.admissions.models import Enrollment


def get_absent_tracker_data():

    students_data = []

    total_working_days = (
        Attendance.objects
        .values('attendance_date')
        .distinct()
        .count()
    )

    enrollments = Enrollment.objects.select_related(
        'admission__student',
        'batch'
    )

    for enrollment in enrollments:

        attendance_records = (
            Attendance.objects
            .filter(enrollment=enrollment)
            .order_by('-attendance_date')
        )

        total_absences = attendance_records.filter(
            status='Absent'
        ).count()

        present_count = attendance_records.filter(
            status='Present'
        ).count()

        consecutive_absences = 0

        for record in attendance_records:

            if record.status == 'Absent':
                consecutive_absences += 1
            else:
                break

        if total_working_days > 0:

            attendance_percentage = (
                present_count / total_working_days
            ) * 100

        else:
            attendance_percentage = 100

        if consecutive_absences >= 5:
            alert_level = "Critical"

        elif consecutive_absences >= 3 or total_absences >= 5:
            alert_level = "Medium"

        else:
            alert_level = "Low"

        if consecutive_absences >= 5:
            observation_note = "Critical Follow-up"

        elif consecutive_absences >= 3:
            observation_note = "Monitoring Required"

        elif total_absences >= 5:
            observation_note = "Frequent Absences"

        else:
            observation_note = "Normal Attendance"
        
        student_attendance_count = attendance_records.count()
        
        if student_attendance_count < total_working_days:
            attendance_status = "Incomplete"
        else:
            attendance_status = "Complete"

        students_data.append({
            
            "id":
            enrollment.id,
            
            "notification_sent":
            False,

            "student":
            enrollment.student,

            "course":
            enrollment.course,

            "batch":
            enrollment.batch,

            "total_absences":
            total_absences,

            "consecutive_absences":
            consecutive_absences,

            "attendance_percentage":
            round(attendance_percentage, 1),

            "alert_level":
            alert_level,

            "observation_note":
            observation_note,
            
            "attendance_status":
            attendance_status,
            
            "admin_notes":
            "",

        })

    return students_data

def get_low_attendance_data():

    students_data = []

    total_working_days = (
        Attendance.objects
        .values('attendance_date')
        .distinct()
        .count()
    )

    enrollments = Enrollment.objects.select_related(
        'admission__student',
        'batch'
    )

    for enrollment in enrollments:

        attendance_records = Attendance.objects.filter(
            enrollment=enrollment
        )

        present_count = attendance_records.filter(
            status='Present'
        ).count()

        total_absences = attendance_records.filter(
            status='Absent'
        ).count()

        if total_working_days > 0:

            attendance_percentage = round(
                (present_count / total_working_days) * 100,
                1
            )

        else:
            attendance_percentage = 100

        if attendance_percentage < 75:

            students_data.append({
                
                "id": enrollment.id,
                "student": enrollment.student,
                "course": enrollment.course,
                "batch": enrollment.batch,
                "attendance_percentage": attendance_percentage,
                "total_absences": total_absences,

            })

    return students_data

  #Reports 
    
from django.shortcuts import render
from django.utils import timezone
from django.db.models import Count

from apps.admissions.models import Enrollment, Course
from .models import Attendance, Batch
from .services import get_low_attendance_data


def reports(request):

    today = timezone.now().date()

    # Top cards

    total_students = Enrollment.objects.count()

    present_today = Attendance.objects.filter(
        attendance_date=today,
        status='Present'
    ).count()

    absent_today = Attendance.objects.filter(
        attendance_date=today,
        status='Absent'
    ).count()

    low_attendance = len(
        get_low_attendance_data()
    )

    # Report table

    report_students = []

    enrollments = Enrollment.objects.select_related(
        'admission__student',
        'admission__course_name',
        'batch'
    )

    total_days = Attendance.objects.values(
        'attendance_date'
    ).distinct().count()

    for enrollment in enrollments:

        present_count = Attendance.objects.filter(
            enrollment=enrollment,
            status='Present'
        ).count()

        absent_count = Attendance.objects.filter(
            enrollment=enrollment,
            status='Absent'
        ).count()

        late_count = Attendance.objects.filter(
            enrollment=enrollment,
            status='Late'
        ).count()

        attendance_rate = (
            round(
                (present_count / total_days) * 100,
                1
            )
            if total_days > 0 else 0
        )

        if attendance_rate >= 75:
            status = "Good"

        elif attendance_rate >= 60:
            status = "Warning"

        else:
            status = "Critical"

        report_students.append({

            "student":
            enrollment.student,

            "course":
            enrollment.course,

            "batch":
            enrollment.batch,

            "present_count":
            present_count,

            "absent_count":
            absent_count,

            "late_count":
            late_count,

            "attendance_rate":
            attendance_rate,

            "status":
            status,
            
            "total_days": total_days,

        })

    # Monthly Chart

    monthly_present = []
    monthly_absent = []
    monthly_late = []

    for month in range(1, 13):

        monthly_present.append(

            Attendance.objects.filter(
                attendance_date__month=month,
                status='Present'
            ).count()

        )

        monthly_absent.append(

            Attendance.objects.filter(
                attendance_date__month=month,
                status='Absent'
            ).count()

        )

        monthly_late.append(

            Attendance.objects.filter(
                attendance_date__month=month,
                status='Late'
            ).count()

        )

    # Course Analytics

    course_labels = []
    course_counts = []

    courses = Course.objects.all()

    for course in courses:

        course_labels.append(
            course.course_name
        )

        course_counts.append(

            Enrollment.objects.filter(
                admission__course_name=course
            ).count()

        )

    # Batch Analytics

    batch_labels = []
    batch_counts = []
    batch_present_counts = []
    batch_performance_labels = []
    batch_performance_counts = []

    batches = Batch.objects.all()

    for batch in batches:

        batch_labels.append(
            batch.batch_name
        )

        batch_counts.append(

            Enrollment.objects.filter(
                batch=batch
            ).count()

        )
        
        present_count = Attendance.objects.filter(
            batch=batch,
            status="Present"
        ).count()

        total_count = Attendance.objects.filter(
            batch=batch
        ).count()

        percentage = round(
            (present_count / total_count) * 100,
            1
        ) if total_count else 0

        batch_present_counts.append(
            present_count
        )

        batch_performance_labels.append(
            batch.batch_name
        )

        batch_performance_counts.append(
            percentage
        )

    context = {

        "total_students":
        total_students,

        "present_today":
        present_today,

        "absent_today":
        absent_today,

        "low_attendance":
        low_attendance,

        "report_students":
        report_students,

        "monthly_present":
        monthly_present,

        "monthly_absent":
        monthly_absent,

        "monthly_late":
        monthly_late,

        "course_labels":
        course_labels,

        "course_counts":
        course_counts,

        "batch_labels":
        batch_labels,

        "batch_counts":
        batch_counts,
        
        "batches": batches,
        
        "courses": courses,
        
        "batch_present_counts": batch_present_counts,
        
        "batch_performance_labels": batch_performance_labels,
        
        "batch_performance_counts": batch_performance_counts,
        
        
            

    }

    return render(
        request,
        "attendance/reports.html",
        context
    )