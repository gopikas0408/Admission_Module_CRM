from django.contrib import admin

from .models import (
    Trainer,
    Batch,
    Attendance,
    SyllabusLog,
)


@admin.register(Trainer)
class TrainerAdmin(admin.ModelAdmin):

    list_display = (
        'trainer_name',
        'specialization',
        'phone_no',
        'email'
    )


@admin.register(Batch)
class BatchAdmin(admin.ModelAdmin):

    list_display = (
        'batch_name',
        'course',
        'trainer',
        'student_count'
    )


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):

    list_display = (
        'enrollment',
        'batch',
        'status',
        'timestamp'
    )

    list_filter = (
        'batch',
        'status'
    )

    search_fields = (
        'enrollment__admission__student__first_name',
        'enrollment__admission__student__last_name',
    )

@admin.register(SyllabusLog)
class SyllabusLogAdmin(admin.ModelAdmin):

    list_display = (
        'batch',
        'trainer',
        'date',
        'topic_covered'
    )

    list_filter = (
        'batch',
        'trainer',
        'date'
    )

    search_fields = (
        'topic_covered',
        'next_topic'
    )