import os

from django import forms
from .models import *
from datetime import date

from django.core.exceptions import ValidationError

def validate_image(file):
    ext = os.path.splitext(file.name)[1].lower()
    if ext not in ['.jpg', '.jpeg', '.png']:
        raise ValidationError("Only JPG, JPEG, PNG allowed")

    if file.size > 2 * 1024 * 1024:
        raise ValidationError("Image must be under 2MB")


def validate_document(file):
    ext = os.path.splitext(file.name)[1].lower()
    if ext not in ['.pdf', '.doc', '.docx']:
        raise ValidationError("Only PDF, DOC, and DOCX files allowed")

    if file.size > 5 * 1024 * 1024:
        raise ValidationError("File must be under 5MB")

class StudentForm(forms.ModelForm):

    photo = forms.FileField(validators=[validate_image], required=False)

    id_proof = forms.FileField(validators=[validate_document], required=False)

    certificate = forms.FileField(validators=[validate_document], required=False)

    class Meta:
        model = Student
        fields = '__all__'

        widgets = {
            'first_name': forms.TextInput(attrs={'placeholder': 'Enter first name', 'required': True}),
            'last_name': forms.TextInput(attrs={'placeholder': 'Enter last name', 'required': True}),
            'email': forms.EmailInput(attrs={'placeholder': 'Enter email', 'required': True}),
            'phone_no': forms.TextInput(attrs={'placeholder': 'Enter phone number', 'required': True}),
            'dob': forms.DateInput(attrs={'type': 'date', 'required': True}),
            'guardian_name': forms.TextInput(attrs={'placeholder': 'Enter guardian name', 'required': True}),
            'guardian_phone_no': forms.TextInput(attrs={'placeholder': 'Enter guardian phone', 'required': True}),
            'address': forms.Textarea(attrs={'placeholder': 'Enter address', 'rows': 2, 'cols': 30, 'style': 'font-size:14px; padding:5px;', 'required': True}),
            'photo': forms.FileInput(attrs={'accept': '.jpg,.jpeg,.png'}),
            'id_proof': forms.FileInput(attrs={ 'accept': '.pdf,doc,.docx'}),
            'certificate': forms.FileInput(attrs={ 'accept': '.pdf,doc,.docx'}),

        }

    
    def clean_first_name(self):
        value = self.cleaned_data.get('first_name')

        if not value.replace(" ", "").isalpha():
            raise forms.ValidationError("Only letters allowed")

        return value

    def clean_last_name(self):
        value = self.cleaned_data.get('last_name')

        if not value.replace(" ", "").isalpha():
            raise forms.ValidationError("Only letters allowed (no numbers/symbols)")

        return value
    



    def clean_phone_no(self):
        phone = self.cleaned_data.get('phone_no')
        
        if Student.objects.filter(phone_no=phone).exists():

            raise forms.ValidationError(
                "Phone number already exists"
            )

        return phone


    def clean_dob(self):
        dob = self.cleaned_data['dob']
        
        if dob >= date.today():
            raise forms.ValidationError("DOB must be a past date!")

        return dob
    
    def clean_email(self):

        email = self.cleaned_data.get('email')

        if Student.objects.filter(email=email).exists():

            raise forms.ValidationError(
                "Email already exists"
            )

        return email
    
    def clean_guardian_phone_no(self):
        phone = self.cleaned_data.get('guardian_phone_no')

        if Student.objects.filter(phone_no=phone).exists():

            raise forms.ValidationError(
                "Phone number already exists"
            )
        
        return phone
    
class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = '__all__'
        widgets = {
            'course_name': forms.TextInput(attrs={'placeholder': 'Enter course name', 'required': True}),
            'duration': forms.TextInput(attrs={'placeholder': 'Enter course duration', 'required': True}),      
            'course_fee': forms.NumberInput(attrs={'placeholder': 'Enter course fee', 'required': True}),
        }


class AdmissionForm(forms.ModelForm):
    class Meta:
        model = Admission
        fields = ['course_name', 'status']
        widgets = {
            'status': forms.RadioSelect()
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['course_name'].empty_label = "Select Course"



class EnrollmentForm(forms.ModelForm):

    def clean_batch(self):
        batch = self.cleaned_data['batch']

        if batch.enrollments.count() >= 30:
            raise forms.ValidationError(
                "This batch is full. Maximum 30 students allowed."
        )

        return batch

    start_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))

    def clean_start_date(self):
        start_date = self.cleaned_data['start_date']
        if start_date <= date.today():
            raise forms.ValidationError("Start date must be future!")
        return start_date

    class Meta:
        model = Enrollment
        fields = ['batch', 'start_date']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['batch'].widget.attrs.update({
            'id': 'id_batch'
        })

   