from dotenv import load_dotenv
import os

class Config:
    def __init__(self):

        load_dotenv()
        
        self.HH_API_URL = "https://api.hh.ru/vacancies"
        self.BOT_TOKEN = os.getenv("BOT_TOKEN")  
        
        self.DEFAULT_SEARCH_QUERY = "Data Scientist"
        self.DEFAULT_AREA_ID = 78  
        self.MAX_VACANCIES = 100
        self.PROFESSIONAL_ROLES = (96, 10)


config = Config()