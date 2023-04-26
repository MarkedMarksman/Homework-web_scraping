import requests
from fake_headers import Headers
from bs4 import BeautifulSoup
import json
from tqdm import tqdm

def get_params(page):
    params = {
        'area': ['1', '2'],
        'text': 'python',
        'page': page
    }
    return params

def get_headers():
    return Headers(browser="chrome", os="win").generate()

def get_data_sorted_by_keywords(url):
    data = requests.get(url, headers=get_headers()).text
    soup = BeautifulSoup(data, 'html.parser')
    discription = soup.find(attrs={"data-qa": "vacancy-description"}).text
    if "django" in discription.lower() or "flask" in discription.lower():
        return True

def parse_page(url, pages):
    jobs = []
    for page in range(pages):
        response = requests.get(url, headers=get_headers(), params=get_params(page)).text
        soup = BeautifulSoup(response, 'html.parser')
        vacancy_info = soup.find_all(class_="vacancy-serp-item-body__main-info")
        for job in tqdm(vacancy_info, desc=f'Проанализировано вакансий на странице {page+1}: '):
            link = job.find(class_='serp-item__title')
            if get_data_sorted_by_keywords(link['href']):
                salary = job.find('span', class_='bloko-header-section-3')
                salary = salary.text.replace('\u202f', ' ') if salary else "не указана"
                city = job.find(attrs={"data-qa": "vacancy-serp__vacancy-address"}, class_='bloko-text')
                if city:
                    city = city.text.partition(',')[0]
                jobs.append(
                    {'link': link['href'].partition('?')[0],
                    'vacancy': link.text,
                    'city': city,
                    'salary': salary}
                )
    return jobs

def get_jobs_json(jobs):
    with open('jobs.json', 'w', encoding='utf-8') as j:
        json.dump(jobs, j, ensure_ascii=False, indent=4)


if __name__ == '__main__':
    url = "https://spb.hh.ru/search/vacancy"
    jobs= parse_page(url, 2)
    get_jobs_json(jobs)
    