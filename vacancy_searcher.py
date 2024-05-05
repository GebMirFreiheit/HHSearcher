import requests
import json
import time


def process_vacancy(vacancy: dict, vacancies_file):
    forbidden_words = ["c++", "frontend", "с++"]
    vacancy_name = vacancy["name"].lower()
    vacancy_url = vacancy["url"].split("?")[0]
    response = requests.get(vacancy_url)
    if response.status_code != 200:
        print(
            f"Запрос на вакансию {vacancy_url} вернул код "
            f"{response.status_code}")
        return
    full_vacancy = response.json()
    if "description" not in full_vacancy:
        print(f"В вакансии {vacancy_url} нет ключа description")
        return
    
    if "python" in vacancy_name or "python" in full_vacancy["description"].lower():
        if any([word in vacancy_name for word in forbidden_words]):
            return
        vacancy_dict = {
            "company": full_vacancy["employer"]["name"],
            "url": full_vacancy["alternate_url"],
            "title": full_vacancy["name"],
        }
        vacancies_file.write(json.dumps(vacancy_dict))
        vacancies_file.write("\n")
        # vacancies.append(vacancy_dict)


def process_company(company: dict, vacancies_file):
    time.sleep(0.5)
    url = f"https://api.hh.ru/vacancies?employer_id={company['id']}&"\
        "professional_role=96&experience=between1And3&experience=between3And6"
    response = requests.get(url)
    if not response.ok:
        print(f"Запрос вернул статус-код {company['id']}")
        return
    info = response.json()
    # если у компании нет вакансий, переходим к следующей
    if not info["found"]:
        return
    print(company["name"])
    for vacancy in info["items"]:
        time.sleep(0.2)
        process_vacancy(vacancy, vacancies_file)


if __name__ == "__main__":
    vacancies_file = open(
        "vacancies.jsonl", "w", encoding="utf8")

    with open("companies.jsonl", "r") as f:
        for line in f:
            try:
                company = json.loads(line)
            except json.JSONDecodeError:
                continue
            process_company(company, vacancies_file)

    vacancies_file.close()
