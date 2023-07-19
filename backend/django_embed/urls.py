"""django_embed URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.urls import path
from django.contrib.auth import views as auth_views

from bokeh_django import autoload, directory, document, static_extensions

from tasks.views import get_status, home, run_task

from . import views


urlpatterns = [
    path(r"", views.index, name="index"),
    path("admin/", admin.site.urls),
    path("tasks/<task_id>/", get_status, name="get_status"),
    path("tasks/", run_task, name="run_task"),
    path("logs/<int:job_id>/", views.stream_logs, name="stream_logs"),
    path("sea-surface-temp", views.sea_surface),
    path("my-sea-surface", views.sea_surface_custom_uri),
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('accounts/login/', auth_views.LoginView.as_view(template_name='login.html'), name='login-alias'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('register/', views.register, name='register'),
    path('profile/', views.profile, name='profile'),
    path('accounts/profile/', auth_views.LoginView.as_view(template_name='profile.html'), name='profile-alias'),
    path('run_subprocess/', views.run_subprocess, name='run_subprocess'),
    path('view_logs/', views.view_logs, name='view_logs'),
    *static_extensions(),
    *staticfiles_urlpatterns(),
]

base_path = settings.BASE_DIR
apps_path = base_path / "bokeh_apps"

bokeh_apps = [
    *directory(apps_path),
    document("sea_surface_direct", views.sea_surface_handler),
    document("job_visualizer_with_template", views.job_visualizer_with_template),
    document("sea_surface_bokeh", apps_path / "sea_surface.py"),
    autoload("temp", views.sea_surface_handler),
    autoload("sea_surface_custom_uri", views.sea_surface_handler),
]


