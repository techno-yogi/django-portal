from django.test import TestCase
from ..models import Host
from ..services import HostQueryService

class HostQueryServiceTest(TestCase):
    def test_get_host_info(self):
        service = HostQueryService()
        info = service.get_host_info(host_ip='http://127.0.0.1', host_port='5000')
        print(info)
        self.assertIsInstance(info, dict)

class HostModelTest(TestCase):
    def test_save_queries_host(self):
        host = Host(ip_address='http://127.0.0.1')
        host.save()
        self.assertIsNotNone(host.ip_address)
        
