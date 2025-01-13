from django.urls import path, include
from . import views

urlpatterns = [
    # Existing URLs
    path('', views.index, name='home'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/faculty/', views.register_faculty, name='register_faculty'),
    path('register/admin/', views.register_admin, name='register_admin'),
    
    # Admin Dashboard URLs
    path('admin/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin/faculty/', views.faculty_list, name='faculty_list'),
    path('admin/departments/', views.departments, name='departments'),
    path('admin/evaluations/', views.evaluations, name='evaluations'),
    path('admin/reports/', views.reports, name='reports'),
    path('admin/settings/', views.settings, name='settings'),
]
