import requests
from config import config
from typing import List

from parser.models import Vacancy

class API:
    def __init__(self):

        self.base_url = config.HH_API_URL
        self.default_roles = config.PROFESSIONAL_ROLES   

    def get_vacancies(self, query: str, area: int, count: int) -> List[Vacancy]:

        params = {
            "text": query,
            "area": area,
            "per_page": count,
            "professional_roles": self.default_roles
        }

        response = requests.get(self.base_url, params=params)
        
        if response.status_code != 200:
            return []
            
        return [Vacancy(item) for item in response.json().get("items", [])]