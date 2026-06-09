from django.contrib import admin
from django.urls import path, include

urlpatterns = [

    path(
        'admin/',
        admin.site.urls
    ),

    path(
        'api/',
        include(
            'apps.Student_attendance_management.urls'
        )
    ),

    path(
        '',
        include(
            'apps.admissions.urls'
        )
    ),
    

]