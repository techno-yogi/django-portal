from django.contrib import admin
from .models import Job, JobType, Log, Host, Environment, Tool, Config 

admin.site.register(Log)
admin.site.register(Job)
admin.site.register(JobType)
admin.site.register(Host)
admin.site.register(Environment)
admin.site.register(Tool)
admin.site.register(Config)

