from django.contrib import admin
from .models import (
    User,
    FacultyProfile,
    AdminProfile,
    Lecture,
    Attendance,
    SeminarWorkshop,
    FacultyReport
)

# Register models with basic admin setup
admin.site.register(User)
admin.site.register(FacultyProfile)
admin.site.register(AdminProfile)
admin.site.register(Lecture)
admin.site.register(Attendance)
admin.site.register(SeminarWorkshop)
admin.site.register(FacultyReport)
