from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError

# from apps.admissions.models import (
#     Course,
#     Enrollment
# )
from django.core.validators import RegexValidator

name_validator = RegexValidator(
    regex=r'^[A-Za-z ]+$',
    message="Only alphabets and spaces are allowed."
)

phone_validator = RegexValidator(
    regex=r'^\d{10}$',
    message="Phone number must be exactly 10 digits."
)

email_validator = RegexValidator(
    regex=r'^[\w\.-]+@[\w\.-]+\.\w+$',
    message="Enter a proper email (example: name@gmail.com)"
)


class Trainer(models.Model):

    trainer_name = models.CharField(max_length=100,validators=[name_validator])

    specialization = models.CharField(max_length=100)

    phone_no = models.CharField(
        max_length=10,
        unique=True,
        validators=[phone_validator]
    )

    email = models.EmailField(unique=True,validators=[email_validator])

    joined_date = models.DateField(
        default=timezone.now
    )

    def __str__(self):
        return self.trainer_name

class Batch(models.Model):

    TIMING_CHOICES = [
        ('Morning', 'Morning'),
        ('Afternoon', 'Afternoon'),
        ('Evening', 'Evening')
    ]

    STATUS_CHOICES = [
        ('Upcoming', 'Upcoming'),
        ('Ongoing', 'Ongoing'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled')
    ]

    batch_name = models.CharField(
        max_length=100
    )

    course = models.ForeignKey(
        'admissions.Course',
        on_delete=models.CASCADE,
        related_name='batches'
    )

    trainer = models.ForeignKey(
        'Trainer',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    timing = models.CharField(
        max_length=20,
        choices=TIMING_CHOICES
    )

    start_time = models.TimeField()

    end_time = models.TimeField()

    start_date = models.DateField()

    end_date = models.DateField(
        null=True,
        blank=True
    )

    max_students = models.PositiveIntegerField(
        default=30
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='Upcoming'
    )

    is_active = models.BooleanField(
        default=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def clean(self):
        
        # Start Time < End Time
        if self.start_time and self.end_time:
            if self.start_time >= self.end_time:
                raise ValidationError({
                    'end_time': 'End time must be greater than start time.'
                })

        # End Date > Start Date
        if self.end_date:
            if self.end_date < self.start_date:
                raise ValidationError({
                    'end_date': 'End date cannot be before start date.'
                })

        # Max Students
        if self.max_students <= 0:
            raise ValidationError({
                'max_students': 'Maximum students must be greater than 0.'
            })

        # Same trainer cannot have overlapping batch timings
        if self.trainer:
            existing_batch = Batch.objects.exclude(pk=self.pk).filter(
                trainer=self.trainer,
                start_date=self.start_date,
                timing=self.timing
            )

            if existing_batch.exists():
                raise ValidationError({
                    'trainer': 'Trainer already assigned to another batch in this time slot.'
                })

        # Completed batch must have end date
        if self.status == 'Completed' and not self.end_date:
            raise ValidationError({
                'end_date': 'Completed batch must have an end date.'
            })

        # Cancelled batch cannot be active
        if self.status == 'Cancelled' and self.is_active:
            raise ValidationError({
                'is_active': 'Cancelled batch cannot be active.'
            })
        
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
    
    @property
    def student_count(self):
        return self.enrollments.count()

    @property
    def available_seats(self):
        return self.max_students - self.student_count

    def __str__(self):
        return f"{self.batch_name} - {self.course.course_name}"


class Attendance(models.Model):

    class AttendanceStatus(models.TextChoices):

        PRESENT = 'Present', 'Present'
        ABSENT = 'Absent', 'Absent'
        LATE = 'Late', 'Late'

    enrollment = models.ForeignKey(
        'admissions.Enrollment',
        on_delete=models.CASCADE
    )

    batch = models.ForeignKey(
        Batch,
        on_delete=models.CASCADE
    )

    trainer = models.ForeignKey(
        Trainer,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )


    status = models.CharField(
        max_length=10,
        choices=AttendanceStatus.choices
    )

    attendance_date = models.DateField(default=timezone.now) 

    timestamp = models.DateTimeField(
        auto_now_add=True
    )

    remarks = models.TextField(
        blank=True,
        null=True
    )

    def clean(self):
        # Batch validation
        if self.enrollment.batch_id != self.batch_id:
            raise ValidationError(
                "Attendance batch must match enrollment batch."
            )

        # Future date validation
        if self.attendance_date > timezone.now().date():
            raise ValidationError(
                "Future attendance not allowed."
            )
        
        # Trainer validation
        if self.trainer:
            if self.batch.trainer_id != self.trainer_id:
                raise ValidationError(
                    "Selected trainer is not assigned to this batch."
                )


    def save(self, *args, **kwargs):

        self.full_clean()

        super().save(*args, **kwargs)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['enrollment', 'batch', 'attendance_date'],
                name='unique_attendance'
            )
        ]

    def __str__(self):

        return (
            f"{self.enrollment.student}"
            f"- {self.attendance_date}"
            f" - {self.status}"
        )
    


class SyllabusLog(models.Model):

    batch = models.ForeignKey(
        'Batch',
        on_delete=models.CASCADE,
        related_name='syllabus_logs'
    )

    trainer = models.ForeignKey(
        'Trainer',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='syllabus_logs'
    )

    date = models.DateField(
        default=timezone.now
    )

    topic_covered = models.CharField(max_length=255)

    duration = models.PositiveIntegerField(
        help_text="Duration in minutes"
    )

    next_topic = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )

    trainer_notes = models.TextField(
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        ordering = ['-date', '-created_at']

    def clean(self):
        if self.duration <= 0:
            raise ValidationError("Duration must be greater than 0")

    def save(self, *args, **kwargs):
        # auto-assign trainer from batch if not given
        if not self.trainer and self.batch and self.batch.trainer:
            self.trainer = self.batch.trainer

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.batch.batch_name} | {self.topic_covered} | {self.date}"
    
    
    #absnet tracker model
    

class AbsentTracker(models.Model):

    ALERT_CHOICES = [
        ('Low', 'Low'),
        ('Medium', 'Medium'),
        ('Critical', 'Critical'),
    ]

    NOTIFICATION_CHOICES = [
        ('SMS Pending', 'SMS Pending'),
        ('Dispatched', 'Dispatched'),
    ]

    enrollment = models.OneToOneField(
        'admissions.Enrollment',
        on_delete=models.CASCADE
    )

    total_absences = models.IntegerField(
        default=0
    )

    consecutive_absences = models.IntegerField(
        default=0
    )

    attendance_percentage = models.FloatField(
        default=100
    )

    alert_level = models.CharField(
        max_length=10,
        choices=ALERT_CHOICES,
        default='Low'
    )

    observation_notes = models.TextField(
        blank=True,
        null=True
    )

    notification_status = models.CharField(
        max_length=20,
        choices=NOTIFICATION_CHOICES,
        default='SMS Pending'
    )

    attendance_status = models.CharField(
        max_length=20,
        default='Complete'
    )

    admin_notes = models.TextField(
        blank=True,
        null=True
    )

    notification_sent = models.BooleanField(
        default=False
    )

    last_notified_at = models.DateTimeField(
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):

        return (
            f"{self.enrollment.student.first_name}"
            f" - {self.alert_level}"
        )