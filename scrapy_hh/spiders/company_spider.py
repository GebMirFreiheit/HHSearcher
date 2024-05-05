import scrapy
import json
import re


target_industries = [
    {"id": "13.663", "name": "Архитектура, проектирование"},
    {"id": "39.441", "name": "Научно-исследовательская, научная, академическая деятельность"},
    {"id": "39.446", "name": "Тренинговые компании"},
    {"id": "44.397", "name": "Контроль качества, экспертиза, испытания и сертификация"},
    {"id": "36.403", "name": "Государственные организации"},
    {"id": "8.485", "name": "Электронно-вычислительная, оптическая, контрольно-измерительная техника, радиоэлектроника, автоматика (монтаж, сервис, ремонт)"},
    {"id": "9.399", "name": "Мобильная связь"},
    {"id": "9.402", "name": "Спутниковая связь"},
    {"id": "8.484", "name": "Электронно-вычислительная, оптическая, контрольно-измерительная техника, радиоэлектроника, автоматика (производство)"},
    {"id": "7.538", "name": "Интернет-провайдер"},
    {"id": "9.400", "name": "Фиксированная связь"},
    {"id": "44.393", "name": "Консалтинговые услуги"},
    {"id": "9.401", "name": "Оптоволоконная связь"},
    {"id": "8.486", "name": "Электронно-вычислительная, оптическая, контрольно-измерительная техника, радиоэлектроника, автоматика (продвижение, оптовая торговля)"},
    {"id": "7.541", "name": "Интернет-компания (поисковики, платежные системы, соц.сети, информационно-познавательные и развлекательные ресурсы, продвижение сайтов и прочее)"},
    {"id": "7.540", "name": "Разработка программного обеспечения"},
    {"id": "7.539", "name": "Системная интеграция,  автоматизации технологических и бизнес-процессов предприятия, ИТ-консалтинг"},
    {"id": "11.459", "name": "Маркетинговые, рекламные, BTL, дизайнерские, Event-, PR-агентства, организация выставок"},
    {"id": "39.442", "name": "Вуз, ссуз колледж, ПТУ"},
]


def find_keywords(content: str) -> bool:
    if re.findall(r"информационн.{2}([^<{}]*)\sбезопасност", content) or \
            "кибербезопасност" in content or " security" in content \
            or re.findall(r"защит.{1}([^<]*)\sинформаци", content) \
            or re.findall(r"информационн.{2}([^<]*)\sзащит", content):
        return True
    else:
        return False


def check_industries(industries: list) -> bool:
    if not industries:
        return True
    intersection = [
        industry for industry in industries if industry in target_industries]
    return bool(intersection)


class CompanySpider(scrapy.Spider):
    name = "companies"

    def start_requests(self):
        urls = [
            f"https://api.hh.ru/employers/{i}"
            for i in range(1100852, 10000000)
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        info = response.json()
        company_name = info["name"]
        if "банк" in company_name.lower() or "bank" in company_name.lower():
            return
        content = info["description"]
        branded_content = info["branded_description"] or ""
        not_api_url = info["alternate_url"]
        if (find_keywords(content) or find_keywords(branded_content)) and\
                check_industries(info["industries"]):
            with open("companies.jsonl", "a") as f:
                company_json = {
                    "name": company_name,
                    "human_url": not_api_url,
                    "id": int(info["id"]),
                    "api_url": response.url
                }
                f.write(f"{json.dumps(company_json)}\n")
