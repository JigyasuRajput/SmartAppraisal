from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import BaseUserManager


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get('is_superuser') is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    ROLE_CHOICES = [
        ('professor', 'Professor'),
        ('admin', 'Admin'),
    ]
    username = None
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='professor')
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='custom_user_set',  # Add related_name to avoid conflict
        blank=True,
        help_text='The groups this user belongs to.',
        verbose_name='groups',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='custom_user_set',  # Add related_name to avoid conflict
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions',
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    REQUIRED_FIELDS = []

    objects = CustomUserManager()
    
    
class FacultyProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    department = models.CharField(max_length=100)
    designation = models.CharField(max_length=100)
    university_code = models.CharField(max_length=50)
    # Other optional fields
    created_at = models.DateTimeField(default=timezone.now)

class AdminProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    department = models.CharField(max_length=100)
    designation = models.CharField(max_length=100)
    university_code = models.CharField(max_length=50)
    # Other optional fields

class Lecture(models.Model):
    faculty = models.ForeignKey(FacultyProfile, on_delete=models.CASCADE)
    subject = models.CharField(max_length=200)
    date = models.DateField()
    hours = models.IntegerField()  # Total hours taught
    # You can add more fields like topics covered, class size, etc.

class Attendance(models.Model):
    lecture = models.ForeignKey(Lecture, on_delete=models.CASCADE)
    date = models.DateField()
    total_students = models.IntegerField()
    present_students = models.IntegerField()
    absent_students = models.IntegerField()
    # You can also store attendance per student

class SeminarWorkshop(models.Model):
    faculty = models.ForeignKey(FacultyProfile, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    date = models.DateField()
    type_choices = [('seminar', 'Seminar'), ('workshop', 'Workshop')]
    type = models.CharField(max_length=50, choices=type_choices)
    description = models.TextField()
    # Additional fields like location, organizers can be added

class FacultyReport(models.Model):
    faculty = models.ForeignKey(FacultyProfile, on_delete=models.CASCADE)
    total_lectures = models.IntegerField()
    total_hours_taught = models.IntegerField()
    total_seminars = models.IntegerField()
    total_workshops = models.IntegerField()
    total_attendance = models.IntegerField()  # Total attendance count
    # You can also calculate averages, performance scores, etc.
    created_at = models.DateTimeField(default=timezone.now)
    status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('reviewed', 'Reviewed'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected')
    ], default='pending')
