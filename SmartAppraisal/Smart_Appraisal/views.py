from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.decorators.csrf import ensure_csrf_cookie
from django.db.models import Count
from django.utils import timezone
from .models import User, FacultyProfile, AdminProfile, Lecture, Attendance, SeminarWorkshop, FacultyReport
from .forms import CustomUserCreationForm, CustomAuthenticationForm

def index(request):
    return render(request, 'index.html')

def login_view(request):
    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('username')  # Retrieve the email
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=email, password=password)  # Authenticate with email
            if user is not None:
                login(request, user)
                if user.role == 'admin':
                    return redirect('admin_dashboard')
                else:
                    return redirect('faculty_dashboard')
            else:
                messages.error(request, 'Invalid email or password')
        else:
            messages.error(request, 'Invalid form submission')
    else:
        form = CustomAuthenticationForm()
    return render(request, 'login.html', {'form': form})

def register_admin(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.role = 'admin'
            user.save()
            AdminProfile.objects.create(user=user)
            messages.success(request, 'Admin registered successfully', extra_tags='alert-success')
            return redirect('login')
        else:
            messages.error(request, 'Error registering admin')
    else:
        form = CustomUserCreationForm()
    return render(request, 'register_admin.html', {'form': form})

def register_faculty(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.role = 'professor'
            user.save()
            FacultyProfile.objects.create(user=user)
            messages.success(request, 'Faculty registered successfully')
            return redirect('login')
        else:
            # Display form errors with improved aesthetics
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field.capitalize()}: {error}")
    else:
        form = CustomUserCreationForm()
    return render(request, 'register_faculty.html', {'form': form})


def is_admin(user):
    return user.is_authenticated and user.role == 'admin'

@login_required
@user_passes_test(is_admin)
@ensure_csrf_cookie
def admin_dashboard(request):
    # Get counts for stats cards
    faculty_count = FacultyProfile.objects.count()
    department_count = FacultyProfile.objects.values('department').distinct().count()
    active_appraisals = FacultyReport.objects.filter(
        created_at__month=timezone.now().month
    ).count()
    pending_reviews = FacultyReport.objects.filter(
        status='pending'
    ).count()

    # Get recent activities
    recent_activities = []
    
    # Recent faculty registrations
    new_faculty = FacultyProfile.objects.order_by('-created_at')[:5]
    for faculty in new_faculty:
        recent_activities.append({
            'title': 'New Faculty Registration',
            'description': f'{faculty.user.get_full_name()} joined as {faculty.designation}',
            'timestamp': faculty.created_at,
            'user': faculty.user.get_full_name()
        })

    # Recent lectures
    recent_lectures = Lecture.objects.order_by('-date')[:5]
    for lecture in recent_lectures:
        recent_activities.append({
            'title': 'Lecture Conducted',
            'description': f'{lecture.faculty.user.get_full_name()} conducted {lecture.subject}',
            'timestamp': lecture.date,
            'user': lecture.faculty.user.get_full_name()
        })

    context = {
        'faculty_count': faculty_count,
        'department_count': department_count,
        'active_appraisals': active_appraisals,
        'pending_reviews': pending_reviews,
        'recent_activities': sorted(recent_activities, key=lambda x: x['timestamp'], reverse=True)[:10]
    }
    
    return render(request, 'admin_dashboard.html', context)


# Ensure that only faculty users can access this view
def is_faculty(user):
    return user.role == 'faculty'

@login_required
@user_passes_test(is_faculty)
@ensure_csrf_cookie
def faculty_dashboard(request):
    # Get counts for stats cards
    active_appraisals = FacultyReport.objects.filter(
        created_at__month=timezone.now().month
    ).count()
    pending_reviews = FacultyReport.objects.filter(
        status='pending'
    ).count()

    # Get recent activities
    recent_activities = []
    
    # Recent lectures
    recent_lectures = Lecture.objects.filter(faculty__user=request.user).order_by('-date')[:5]
    for lecture in recent_lectures:
        recent_activities.append({
            'title': 'Lecture Conducted',
            'description': f'{lecture.faculty.user.get_full_name()} conducted {lecture.subject}',
            'timestamp': lecture.date,
            'user': lecture.faculty.user.get_full_name()
        })

    context = {
        'active_appraisals': active_appraisals,
        'pending_reviews': pending_reviews,
        'recent_activities': sorted(recent_activities, key=lambda x: x['timestamp'], reverse=True)[:5]
    }
    
    return render(request, 'faculty_dashboard.html', context)


@login_required
@user_passes_test(is_admin)
def faculty_list(request):
    faculties = FacultyProfile.objects.all().order_by('department', 'user__first_name')
    return render(request, 'faculty_list.html', {'faculties': faculties})

@login_required
@user_passes_test(is_admin)
def departments(request):
    departments = FacultyProfile.objects.values('department').annotate(
        faculty_count=Count('id')
    ).order_by('department')
    return render(request, 'departments.html', {'departments': departments})

@login_required
@user_passes_test(is_admin)
def evaluations(request):
    evaluations = FacultyReport.objects.all().order_by('-created_at')
    return render(request, 'evaluations.html', {'evaluations': evaluations})

@login_required
@user_passes_test(is_admin)
def reports(request):
    # Add your reporting logic here
    return render(request, 'reports.html')

@login_required
@user_passes_test(is_admin)
def settings(request):
    # Add your settings logic here
    return render(request, 'settings.html')

def logout_view(request):
    logout(request)
    return redirect('login')  # Redirect to the login page after logout

def faculty_detail(request, pk):
    faculty = get_object_or_404(FacultyProfile, pk=pk)
    lectures = Lecture.objects.filter(faculty=faculty)
    attendance_records = Attendance.objects.filter(lecture__faculty=faculty)
    seminars_workshops = SeminarWorkshop.objects.filter(faculty=faculty)
    return render(request, 'faculty_detail.html', {
        'faculty': faculty,
        'lectures': lectures,
        'attendance_records': attendance_records,
        'seminars_workshops': seminars_workshops,
    })
