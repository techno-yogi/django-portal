from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from ..models import Log, Job, JobType

class TestViews(TestCase):
    def setUp(self):
        self.client = Client()
        self.admin_user = User.objects.create_superuser(username='postgres', password='postgresadmin')
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.other_view = User.objects.create_user(username='other_user', password='12345')
        self.job = Job.objects.create(user=self.user, job_id=1, job_type=JobType.objects.create(name='test'), log_file='/path/to/log')
        login = self.client.login(username='postgres', password='postgresadmin')

    def test_stream_logs(self):
        response = self.client.get(f'/logs/{self.job.job_id}/')
        self.assertEqual(response.status_code, 200)

    def test_stream_logs_not_owner(self):
        self.client.login(username='other_user', password='12345')
        response = self.client.get(f'/logs/{self.job.job_id}/')
        self.assertEqual(response.status_code, 403)

    def test_run_subprocess(self):
        response = self.client.get(reverse('run_subprocess'))
        self.assertEqual(response.status_code, 302)  # Expecting a redirect
        log = Log.objects.filter(user=self.admin_user).first()
        self.assertIsNotNone(log)
        self.assertIn('Python', log.output)

    def test_view_logs(self):
        Log.objects.create(user=self.admin_user, output="Test log")
        response = self.client.get(reverse('view_logs'))
        print(response)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "log")

    def test_register(self):
        response = self.client.post(reverse('register'), {
            'username': 'testuser2',
            'password1': 'abcdef123456',
            'password2': 'abcdef123456',
        })
        self.assertEqual(response.status_code, 302)  # Expecting a redirect
        self.assertTrue(User.objects.filter(username='testuser2').exists())

    def test_profile(self):
        response = self.client.get(reverse('profile'))
        self.assertEqual(response.status_code, 200)  # Expecting a redirect

    def test_index(self):
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)
