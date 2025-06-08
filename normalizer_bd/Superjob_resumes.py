import requests
import json
import time
import os
from typing import Dict, List

# Конфигурация
API_KEY = "v3.h.4905791.f72938d0c57d8956a4524c02a06d50409fcb4198.0e4294e23cc795178fe05e210746a2aa21881acc"  # Замените на ваш секретный ключ API
BASE_URL = "https://api.superjob.ru/2.0/resumes/"
OUTPUT_DIR = "resumes"  # Папка для сохранения JSON-файлов
RESUMES_PER_FILE = 20  # Количество резюме в одном JSON-файле
REQUESTS_PER_MINUTE = 120  # Ограничение API
PAGE_SIZE = 100  # Максимум 100 резюме на страницу
MAX_PAGES = 5  # Максимум 500 резюме (5 страниц по 100)
VACANCIES_FILE = "all_vacancies_moscow.json"  # Файл с профессиями


def load_vacancies() -> List[str]:
    """Чтение профессий из JSON-файла."""
    try:
        with open(VACANCIES_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Файл {VACANCIES_FILE} не найден.")
        return []
    except json.JSONDecodeError:
        print(f"Ошибка чтения JSON из {VACANCIES_FILE}.")
        return []


def fetch_resumes(keyword: str, page: int = 0) -> Dict:
    """Получение резюме с SuperJob API по ключевому слову."""
    headers = {"X-Api-App-Id": API_KEY}
    params = {
        "page": page,
        "count": PAGE_SIZE,
        "keyword": keyword,
    }

    try:
        response = requests.get(BASE_URL, headers=headers, params=params)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Ошибка при запросе к API для '{keyword}' (страница {page + 1}): {e}")
        return {}


def parse_resume(resume: Dict) -> Dict:
    """Извлечение расширенных полей из резюме."""
    # Проверка зарплаты
    salary = resume.get("payment", 0)
    if not salary:
        return None  # Пропускаем резюме без зарплаты

    # Обработка profession
    profession = resume.get("profession", "")
    position = profession.get("title", "") if isinstance(profession, dict) else profession

    # Обработка town
    town = resume.get("town", "")
    city = town.get("title", "") if isinstance(town, dict) else town

    # Обработка education
    education = resume.get("education", "")
    education_title = education.get("title", "") if isinstance(education, dict) else education

    # Обработка опыта работы
    work_experience = []
    for exp in resume.get("work_experience", []):
        work_experience.append({
            "company": exp.get("company", ""),
            "position": exp.get("position", ""),
            "start_date": f"{exp.get('start_year', '')}-{exp.get('start_month', '').zfill(2)}",
            "end_date": f"{exp.get('end_year', '')}-{exp.get('end_month', '').zfill(2)}" if exp.get(
                "end_year") else "по настоящее время",
            "responsibilities": exp.get("responsibilities", "")
        })

    # Обработка типа занятости и графика
    employment_type = resume.get("employment", {}).get("title", "") if isinstance(resume.get("employment"),
                                                                                  dict) else resume.get("employment",
                                                                                                        "")
    schedule = resume.get("place_of_work", {}).get("title", "") if isinstance(resume.get("place_of_work"),
                                                                              dict) else resume.get("place_of_work", "")

    return {
        "id": resume.get("id", ""),
        "age": resume.get("age", 0),
        "city": city,
        "position": position,
        "salary": salary,
        "education": education_title,
        "resume_url": resume.get("link", ""),
        "keyword": resume.get("keyword", ""),
        "work_experience": work_experience,
        "skills": resume.get("key_skills", ""),
        "last_updated": resume.get("update_date", ""),
        "search_status": resume.get("search_status", {}).get("title", ""),
        "employment_type": employment_type,
        "schedule": schedule
    }


def save_to_json(resumes: List[Dict], file_index: int):
    """Сохранение резюме в JSON-файл."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    filename = os.path.join(OUTPUT_DIR, f"resumes_{file_index}.json")
    try:
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(resumes, f, ensure_ascii=False, indent=4)
        print(f"Сохранено {len(resumes)} резюме в {filename}")
    except Exception as e:
        print(f"Ошибка при сохранении в {filename}: {e}")


def main():
    all_resumes = []
    file_index = 1

    # Чтение профессий
    keywords = load_vacancies()
    if not keywords:
        print("Не удалось загрузить профессии. Завершение работы.")
        return

    # Создание папки для JSON-файлов
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Проходим по всем ключевым словам
    for keyword in keywords:
        print(f"Получение резюме для '{keyword}'...")
        for page in range(MAX_PAGES):
            print(f"Страница {page + 1} для '{keyword}'...")
            data = fetch_resumes(keyword, page)

            if not data.get("objects"):
                print(f"Резюме не найдены для '{keyword}' или достигнут конец данных.")
                break

            # Парсинг резюме
            for resume in data["objects"]:
                parsed_resume = parse_resume(resume)
                if parsed_resume:  # Пропускаем резюме без зарплаты
                    parsed_resume["keyword"] = keyword
                    all_resumes.append(parsed_resume)

                    # Сохранение каждые RESUMES_PER_FILE резюме
                    if len(all_resumes) >= RESUMES_PER_FILE:
                        save_to_json(all_resumes[:RESUMES_PER_FILE], file_index)
                        all_resumes = all_resumes[RESUMES_PER_FILE:]
                        file_index += 1

            # Соблюдение лимита запросов
            time.sleep(60 / REQUESTS_PER_MINUTE)

    # Сохранение оставшихся резюме, если они есть
    if all_resumes:
        save_to_json(all_resumes, file_index)

    if file_index == 1:
        print("Не удалось собрать резюме.")


if __name__ == "__main__":
    main()