from django.urls import path, include

from . import views 
from rest_framework.routers import DefaultRouter

from .views import (
    AttendanceSubmitAPIView,
    SyllabusLogViewSet,
    TrainerViewSet,
    BatchViewSet,
    AttendanceViewSet,
    attendance_export,
    attendance_report_page,
    batches_page,
    mark_attendance_page,
    bulk_attendance,
    today_attendance_summary,
)

router = DefaultRouter()

router.register(r'trainers', TrainerViewSet)

router.register(r'batches', BatchViewSet)

router.register(r'attendance', AttendanceViewSet)

router.register(r'syllabus-logs',SyllabusLogViewSet)

urlpatterns = [

    path(
        'batches-page/',
        batches_page,
        name='batches_page'
    ),

    path(
    'mark-attendance/<int:batch_id>/',
    mark_attendance_page,
    name='mark_attendance_page'
    ),

    path('today-attendance/<int:batch_id>/', today_attendance_summary),

    path(
    'attendance/bulk/',
    bulk_attendance,
    name='bulk_attendance'
    ),

    path(
        "attendance/submit/",
        AttendanceSubmitAPIView.as_view(),
        name="attendance-submit"
    ),

    path(
    'attendance-report/',
    attendance_report_page,
    name='attendance_report'
),
path('attendance-export/', views.attendance_export, name='attendance_export'),

path(
        "student-attendance-summary/<int:student_id>/",
        views.student_attendance_summary,
        name="student_attendance_summary"
    ),
    path('get-batches/', views.get_batches_by_course, name='get-batches'),

    path(
    "dashboard/",
    views.dashboard,
    name="dashboard"
),
    path(
    'absent-tracker/',
    views.absent_tracker,
    name='absent_tracker'
),
    path(
    'get-admin-notes/<int:tracker_id>/',
    views.get_admin_notes,
    name='get_admin_notes'
),
    path(
    "save-admin-notes/",
    views.save_admin_notes,
    name="save_admin_notes"
),
    path(
    'low-attendance-alerts/',
    views.low_attendance_alerts,
    name='low_attendance_alerts'
),
    path(
    'send-sms-notification/<int:enrollment_id>/',
    views.send_sms_notification,
    name='send_sms_notification'
),

path(
    'send-low-attendance-email/<int:enrollment_id>/',
    views.send_low_attendance_email,
    name='send_low_attendance_email'
),

path(
    'send-email-all/',
    views.send_email_all,
    name='send_email_all'
),

path(
    'send-sms-all/',
    views.send_sms_all,
    name='send_sms_all'
),

path(
    'send-monthly-report/',
    views.send_monthly_report,
    name='send_monthly_report'
),

path(
    'reports/',
    views.reports,
    name='reports'
),

path(
    'analytics-pdf/',
    views.analytics_pdf,
    name='analytics_pdf'
),

path(
    'analytics-excel/',
    views.analytics_excel,
    name='analytics_excel'
),

path(
    'report-pdf/',
    views.report_pdf,
    name='report_pdf'
),

path(
    'report-excel/',
    views.report_excel,
    name='report_excel'
),


    path(
        '',
        include(router.urls)
    ),

]