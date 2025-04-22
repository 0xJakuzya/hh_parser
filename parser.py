import requests

def get_vacancy_api():
    
    url = 'https://api.hh.ru/vacancies'
    
    params = {
    "text": "Data Scientist",  
    "area": 78,  
    "per_page": 10,  
    "professional_roles": [96, 10]
    }   
    
    response = requests.get(url, params=params)

    if response.status_code == 200:

        data = response.json()
        vacancies = []

        for item in data.get("items", []):

            vacancies.append({
                "Вакансия": item.get("name"),
                "Компания": item.get("employer", {}).get("name"),
                "Зарплата": (
                    f"{item['salary']['from']} - {item['salary']['to']} {item['salary']['currency']}"
                    if item.get("salary") else "Не указана"
                ),
                "experience": item.get("experience", {}).get("name"),
                "schedule": item.get("schedule", {}).get("name"),
                "Ссылка": item.get("alternate_url")
            })


        return vacancies
    else:
        print(f"Error: {response.status_code}")

        return []
    
if __name__ == "__main__":

    vacancies = get_vacancy_api()
    for vacancy in vacancies:
        print(vacancy, '\n')