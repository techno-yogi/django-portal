from django.test import TestCase
from ..models import User, Job, JobType, Task, Log, Host, Environment, Tool, Config

class TestModels(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.job_type = JobType.objects.create(name='test')
        self.job = Job.objects.create(user=self.user, job_type=self.job_type)
        self.task = Task.objects.create(user=self.user, job=self.job)
        self.log = Log.objects.create(user=self.user, output='test')
        self.host = Host.objects.create(name='Test Host', ip_address='127.0.0.1')
    
    def test_models_can_be_retrieved(self):
        self.assertEqual(User.objects.first(), self.user)
        self.assertEqual(Job.objects.first(), self.job)
        self.assertEqual(Task.objects.first(), self.task)
        self.assertEqual(Log.objects.first(), self.log)
        self.assertEqual(Host.objects.first(), self.host)

    def test_related_name(self):
        self.assertEqual(self.job.tasks.first(), self.task)

    def test_str(self):
        self.assertEqual(str(self.job), f"Job {self.job.job_id}: {self.job.job_type}")
        self.assertEqual(str(self.task), f"Task {self.task.task_id} of Job {self.job.job_id}: {self.job.job_type} from User: {self.user}")

    def test_status_choices(self):
        for status in ('pending', 'running', 'completed', 'failed'):
            self.job.status = status
            self.job.save()
            self.assertEqual(self.job.status, status)

    def test_progress_float(self):
        self.task.progress = 0.5
        self.task.save()
        self.assertEqual(self.task.progress, 0.5)
        with self.assertRaises(Exception):
            self.task.progress = 'invalid'
            self.task.save()

    def test_name_label(self):
        host = Host.objects.get(id=1)
        field_label = host._meta.get_field('name').verbose_name
        self.assertEqual(field_label, 'name')

    def test_name_max_length(self):
        host = Host.objects.get(id=1)
        max_length = host._meta.get_field('name').max_length
        self.assertEqual(max_length, 255)

    def test_object_name_is_name(self):
        host = Host.objects.get(id=1)
        expected_object_name = host.name
        self.assertEqual(str(host), expected_object_name)