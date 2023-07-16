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

class Host(models.Model):
    name = models.CharField(max_length=255)
    ip_address = models.GenericIPAddressField()

    def __str__(self):
        return self.name
    
    # add any other fields as needed
    class Meta:
        app_label = 'django_embed'

class Environment(models.Model):
    name = models.CharField(max_length=255)
    host = models.ForeignKey(Host, on_delete=models.CASCADE)
    # add any other fields as needed
    class Meta:
        app_label = 'django_embed'

class JobType(models.Model):
    name = models.CharField(max_length=255)
    # add any other fields as needed
    class Meta:
        app_label = 'django_embed'

class Tool(models.Model):
    name = models.CharField(max_length=255)
    job_type = models.ForeignKey(JobType, on_delete=models.CASCADE)
    environments = models.ManyToManyField(Environment)
    class Meta:
        app_label = 'django_embed'

class Config(models.Model):
    name = models.CharField(max_length=255)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    tool = models.ForeignKey(Tool, on_delete=models.CASCADE)
    config_data = models.TextField()  # or use JSONField
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
    job_type = models.ForeignKey(JobType, on_delete=models.CASCADE, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    submit_time = models.DateTimeField(auto_now_add=True)
    tool = models.ForeignKey(Tool, on_delete=models.CASCADE, null=True)
    host = models.ForeignKey(Host, on_delete=models.CASCADE, null=True)
    complete_time = models.DateTimeField(null=True, blank=True)
    output_dir = models.CharField(max_length=255, null=True, blank=True)
    output = models.TextField(null=True, blank=True)
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

