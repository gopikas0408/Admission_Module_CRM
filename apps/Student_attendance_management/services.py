from .models import Attendance, AbsentTracker
from apps.admissions.models import Enrollment
from django.db.models import Q


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
        
        tracker = AbsentTracker.objects.filter(
            enrollment=enrollment
        ).first()

        total_absences = attendance_records.filter(
            status='Absent'
        ).count()

        present_count = attendance_records.filter(
            Q(status='Present') |
            Q(status='Late')
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
            tracker.admin_notes if tracker else "",
            
            "tracker_id": tracker.id if tracker else None,

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
        ).order_by('-attendance_date')
        
        if attendance_records.count() < 3:
            continue

        present_count = attendance_records.filter(
            Q(status='Present') |
            Q(status='Late')
        ).count()

        total_absences = attendance_records.filter(
            status='Absent'
        ).count()

        # Consecutive Absences
        consecutive_absences = 0

        for record in attendance_records:

            if record.status == 'Absent':
                consecutive_absences += 1
            else:
                break

        # Attendance Percentage
        if total_working_days > 0:

            attendance_percentage = round(
                (present_count / total_working_days) * 100,
                1
            )

        else:
            attendance_percentage = 100

        # Alert Logic
        if (
            attendance_percentage < 60
            or consecutive_absences >= 3
            or total_absences >= 8
        ):

            alert_level = "Critical"

        elif (
            attendance_percentage < 75
            or consecutive_absences == 2
            or total_absences >= 5
        ):

            alert_level = "Warning"

        else:
            continue

        students_data.append({

            "id": enrollment.id,

            "student": enrollment.student,

            "course": enrollment.course,

            "batch": enrollment.batch,

            "attendance_percentage": attendance_percentage,

            "total_absences": total_absences,

            "consecutive_absences": consecutive_absences,

            "alert_level": alert_level,

        })

    return students_data