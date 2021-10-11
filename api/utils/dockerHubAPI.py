import logging
import requests
from django.conf import settings
from rest_framework import response

# Get an instance of a logger
logger = logging.getLogger(__name__)

BASE_URL = "https://hub.docker.com/v2/repositories/cuebook/"
URL_SUFFIX = "/tags/?page_size=100&page=1&ordering=last_updated"

class DockerHubAPI:
    """
    Functionalities around docker hub APIs
    """
    def getImageTags(self, repository: str):
        try:
            response = requests.get(f"{BASE_URL}{repository}{URL_SUFFIX}")
            return response.json().get('results', [])
        except Exception as ex:
            return []

# Export initalized class
dockerHubAPI = DockerHubAPI()
