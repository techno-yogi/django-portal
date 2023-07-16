import logging
import requests

logger = logging.getLogger(__name__)

class HostQueryService:
    def get_host_info(self, host_ip, host_port=5000):
        try:
            response = requests.get(f'{host_ip}:{host_port}/info')
            response.raise_for_status()
        except requests.RequestException as e:
            logger.error(f'Failed to query host {host_ip}:{host_port}: {e}')
            return None
        else:
            return response.json()


