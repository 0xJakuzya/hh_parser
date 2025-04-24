class Vacancy:
    def __init__(self, data: dict):
        self.name = data.get("name", "Без названия")
        self.employer = data.get("employer", {}).get("name", "Компания не указана")
        self.salary = data.get("salary")
        self.experience = data.get("experience", {}).get("name", "Не указан")
        self.url = data.get("alternate_url", "#")

    def _parse_salary(self, salary_data: dict) -> str:
        if not salary_data:
            return "не указана"
            
        salary_from = salary_data.get("from")
        salary_to = salary_data.get("to")
        currency = salary_data.get("currency", "")
        
        if salary_from and salary_to:
            return f"{salary_from}-{salary_to} {currency}"
        elif salary_from:
            return f"от {salary_from} {currency}"
        elif salary_to:
            return f"до {salary_to} {currency}"
        return "не указана"
    
    def formatted(self) -> str:
        return (
            f"🏢 {self.name}\n"
            f"🏛 {self.employer}\n"
            f"💰 {self.salary}\n"
            f"📊 {self.experience}\n"
            f"🔗 {self.url}"
        )