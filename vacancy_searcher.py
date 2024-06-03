import argparse
import requests
import json
import sys
import time


def process_vacancy(vacancy: dict, vacancies_file):
    forbidden_words = [
        "c++", "frontend", "с++", "микроконтроллер", "data engineer",
        "системный программист", "data scientist", "fullstack"]
    vacancy_name = vacancy["name"].lower()
    vacancy_url = vacancy["url"].split("?")[0]
    response = requests.get(vacancy_url)
    if response.status_code == 403:
        time.sleep(4)
        print(
            f"Запрос на вакансию {vacancy_url} вернул код "
            f"{response.status_code}")
        return
    elif response.status_code != 200:
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
        time.sleep(2)


def process_company(company: dict, vacancies_file, date_from: str):
    time.sleep(0.7)
    url = f"https://api.hh.ru/vacancies?employer_id={company['id']}&"\
        "professional_role=96&experience=between1And3&experience=between3And6"\
        f"&text=python{f'&date_from={date_from}' if date_from else ''}"
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
        process_vacancy(vacancy, vacancies_file)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--date_from", required=False,
        help="Искать вакансии, начиная с этой даты (формат YYYY-MM-DD)"
    )

    arg_namespace = parser.parse_args(sys.argv[1:])
    date_from = arg_namespace.date_from or ""
    
    vacancies_file = open(
        "vacancies.jsonl", "w", encoding="utf8")

    with open("companies_old.jsonl", "r") as f:
        for line in f:
            try:
                company = json.loads(line)
            except json.JSONDecodeError:
                continue
            process_company(company, vacancies_file, date_from)

    vacancies_file.close()
