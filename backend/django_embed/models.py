from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User


User = get_user_model()

class Log(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    output = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'django_embed'

class Job(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('running', 'Running'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    job_id = models.AutoField(primary_key=True)
    job_type = models.CharField(max_length=100)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    submit_time = models.DateTimeField(auto_now_add=True)
    complete_time = models.DateTimeField(null=True, blank=True)
    output_dir = models.CharField(max_length=255, null=True, blank=True)
    system_config = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"Job {self.job_id}: {self.job_type}"

    class Meta:
        app_label = 'django_embed'

class Task(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='tasks')
    task_id = models.AutoField(primary_key=True)
    status = models.CharField(max_length=20, choices=Job.STATUS_CHOICES, default='pending')
    progress = models.FloatField(default=0.0)
    start_time = models.DateTimeField(null=True, blank=True)
    complete_time = models.DateTimeField(null=True, blank=True)
    output = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"Task {self.task_id} of Job {self.job.job_id}: {self.job.job_type} from User: {self.user}"

    class Meta:
        app_label = 'django_embed'