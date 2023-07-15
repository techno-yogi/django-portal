from django.test import TestCase
from ..models import User, Job, Task, Log

class TestModels(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.job = Job.objects.create(user=self.user, job_type='test')
        self.task = Task.objects.create(user=self.user, job=self.job)
        self.log = Log.objects.create(user=self.user, output='test')

    def test_models_can_be_retrieved(self):
        self.assertEqual(User.objects.first(), self.user)
        self.assertEqual(Job.objects.first(), self.job)
        self.assertEqual(Task.objects.first(), self.task)
        self.assertEqual(Log.objects.first(), self.log)

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
        # with self.assertRaises(Exception):
        #     self.job.status = 'invalid'
        #     self.job.save()

    def test_progress_float(self):
        self.task.progress = 0.5
        self.task.save()
        self.assertEqual(self.task.progress, 0.5)
        with self.assertRaises(Exception):
            self.task.progress = 'invalid'
            self.task.save()
