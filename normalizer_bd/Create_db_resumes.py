import psycopg2
import json
import os
from typing import Dict, List
from psycopg2.extras import RealDictCursor

# Конфигурация подключения к PostgreSQL
DB_CONFIG = {
    "dbname": "resumes",  # Замените на имя вашей базы данных
    "user": "postgres",  # Замените на имя пользователя
    "password": "42264",  # Замените на пароль
    "host": "localhost",  # Хост, обычно localhost
    "port": "5432"  # Порт PostgreSQL, по умолчанию 5432
}

# Конфигурация путей
INPUT_DIR = "resumes"  # Папка с JSON-файлами резюме

# Загрузка маппинга профессий
with open("job_title_mappings.json", encoding='utf-8') as f:
    title_mapping_raw = json.load(f)

# Построим "обратный" словарь: синоним -> основной тайтл
title_mapping = {}
for main_title, synonyms in title_mapping_raw.items():
    for synonym in synonyms:
        title_mapping[synonym.strip()] = main_title


def create_database():
    """Создание таблиц в базе данных PostgreSQL."""
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()

    # Создание таблицы resumes
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS resumes (
            id BIGINT PRIMARY KEY,
            age INTEGER,
            city TEXT,
            position TEXT,
            salary INTEGER,
            education TEXT,
            resume_url TEXT,
            keyword TEXT,
            skills TEXT,
            last_updated TEXT,
            search_status TEXT,
            employment_type TEXT,
            schedule TEXT
        )
    """)

    # Создание таблицы work_experience
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS work_experience (
            id SERIAL PRIMARY KEY,
            resume_id BIGINT,
            company TEXT,
            position TEXT,
            start_date TEXT,
            end_date TEXT,
            responsibilities TEXT,
            FOREIGN KEY (resume_id) REFERENCES resumes(id)
        )
    """)

    # Создание таблицы languages
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS languages (
            id SERIAL PRIMARY KEY,
            resume_id BIGINT,
            language TEXT,
            level TEXT,
            FOREIGN KEY (resume_id) REFERENCES resumes(id)
        )
    """)

    # Создание таблицы contacts
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS contacts (
            id SERIAL PRIMARY KEY,
            resume_id BIGINT,
            phone TEXT,
            email TEXT,
            FOREIGN KEY (resume_id) REFERENCES resumes(id)
        )
    """)

    conn.commit()
    cursor.close()
    conn.close()


def insert_resume(resume: Dict, conn):
    """Вставка резюме в базу данных с заменой position на основное название."""
    cursor = conn.cursor()

    # Проверка, существует ли резюме с таким id
    cursor.execute("SELECT id FROM resumes WHERE id = %s", (resume["id"],))
    if cursor.fetchone():
        print(f"Резюме с id {resume['id']} уже существует, пропускаем.")
        return

    # Замена position на основное название из title_mapping
    position = resume.get("position", "")
    normalized_position = title_mapping.get(position.strip(), position)  # Если нет в маппинге, оставляем как есть

    # Вставка в таблицу resumes
    cursor.execute("""
        INSERT INTO resumes (
            id, age, city, position, salary, education, resume_url,
            keyword, skills, last_updated, search_status, employment_type, schedule
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, (
        resume["id"],
        resume["age"],
        resume["city"],
        normalized_position,  # Используем нормализованное название
        resume["salary"],
        resume["education"],
        resume["resume_url"],
        resume["keyword"],
        resume["skills"],
        resume["last_updated"],
        resume["search_status"],
        resume["employment_type"],
        resume["schedule"]
    ))

    # Вставка опыта работы
    for exp in resume.get("work_experience", []):
        cursor.execute("""
            INSERT INTO work_experience (
                resume_id, company, position, start_date, end_date, responsibilities
            ) VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            resume["id"],
            exp.get("company", ""),
            exp.get("position", ""),
            exp.get("start_date", ""),
            exp.get("end_date", ""),
            exp.get("responsibilities", "")
        ))

    # Вставка языков
    for lang in resume.get("languages", []):
        cursor.execute("""
            INSERT INTO languages (resume_id, language, level)
            VALUES (%s, %s, %s)
        """, (
            resume["id"],
            lang.get("language", ""),
            lang.get("level", "")
        ))

    # Вставка контактов
    contacts = resume.get("contacts", {})
    cursor.execute("""
        INSERT INTO contacts (resume_id, phone, email)
        VALUES (%s, %s, %s)
    """, (
        resume["id"],
        contacts.get("phone", ""),
        contacts.get("email", "")
    ))


def main():
    # Создание таблиц
    create_database()

    # Подключение к базе данных
    conn = psycopg2.connect(**DB_CONFIG, cursor_factory=RealDictCursor)

    try:
        # Чтение всех JSON-файлов из папки resumes
        if not os.path.exists(INPUT_DIR):
            print(f"Папка {INPUT_DIR} не найдена.")
            return

        for filename in os.listdir(INPUT_DIR):
            if filename.endswith(".json"):
                filepath = os.path.join(INPUT_DIR, filename)
                try:
                    with open(filepath, "r", encoding="utf-8") as f:
                        resumes = json.load(f)
                        for resume in resumes:
                            insert_resume(resume, conn)
                            print(f"Добавлено резюме с id {resume['id']} из {filename}")
                except json.JSONDecodeError:
                    print(f"Ошибка чтения JSON из {filepath}")
                except Exception as e:
                    print(f"Ошибка при обработке {filepath}: {e}")

        # Подтверждение изменений
        conn.commit()
        print("Все резюме успешно добавлены в базу данных.")

    except Exception as e:
        print(f"Ошибка: {e}")
    finally:
        conn.close()


if __name__ == "__main__":
    main()