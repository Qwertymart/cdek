import requests
import json
from typing import Set, Dict, List
from tqdm import tqdm  # Для прогресс-бара


def fetch_all_job_titles(
        search_query: str = "",
        max_results: int = 2000,  # Лимит API hh.ru
        area: int = 1,  # 1 - Москва
        period: int = 30  # За последние 30 дней
) -> Set[str]:
    """
    Собирает уникальные названия вакансий с hh.ru

    :param search_query: Поисковый запрос (пусто - все вакансии)
    :param max_results: Максимальное количество результатов
    :param area: ID региона
    :param period: Период в днях
    :return: Множество уникальных названий
    """
    base_url = "https://api.hh.ru/vacancies"
    job_titles = set()
    per_page = 100  # Максимум на страницу
    pages = min((max_results // per_page) + 1, 20)  # Не более 20 страниц

    try:
        for page in tqdm(range(pages), desc="Получение вакансий"):
            params = {
                "text": search_query,
                "area": area,
                "period": period,
                "per_page": per_page,
                "page": page
            }

            response = requests.get(base_url, params=params)
            response.raise_for_status()

            data = response.json()
            for item in data.get("items", []):
                job_titles.add(item["name"].strip())

            if len(data.get("items", [])) < per_page:
                break  # Последняя страница

    except requests.exceptions.RequestException as e:
        print(f"\nОшибка при запросе: {e}")

    return job_titles


def save_to_json(data: Set[str], filename: str = "hh_job_titles_moscow.json") -> None:
    """Сохраняет названия в JSON-файл"""
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(sorted(list(data)), f, ensure_ascii=False, indent=2)
    print(f"\nСохранено {len(data)} уникальных названий в {filename}")


if __name__ == "__main__":
    search = input("Введите поисковый запрос (или Enter для всех вакансий): ")

    print("\nСбор названий вакансий...")
    titles = fetch_all_job_titles(
        search_query=search,
        max_results=2000,  # Можно уменьшить
        area=1,  # 1 - Москва, 2 - СПб
        period=30  # За последний месяц
    )

    if titles:
        save_to_json(titles)
    else:
        print("Не удалось получить названия вакансий")
