#!/usr/bin/env python3
"""
Главный модуль для запуска парсинга вакансий с HH.ru или SuperJob
"""
import os
import sys
from pathlib import Path

# Добавляем корневую директорию проекта в путь
project_root = Path(__file__).parent.parent  # ~/PycharmProjects/cdek/vacancy_parser
sys.path.append(str(project_root))

from src.parsers.hh_parser import HHVacancyParser
from src.parsers.superjob_parse import SuperJobVacancyParser  # Исправлен импорт

def main():
    """Основная функция запуска парсинга"""

    # Укажите источник: 'hh' для HH.ru, 'sj' для SuperJob
    SOURCE = 'hh'

    print(f"Запуск парсера вакансий для {SOURCE.upper()}")

    # Указываем входной файл относительно корня проекта
    input_file = project_root / "data" / "input" / "all_vacancies_moscow.json"

    # Проверяем существование входного файла
    if not input_file.exists():
        print(f"Входной файл не найден: {input_file}")
        print("Убедитесь, что файл all_vacancies_moscow.json существует в папке data/input/")
        return False

    try:
        if SOURCE == 'hh':
            # Инициализируем парсер HH
            parser = HHVacancyParser()
        elif SOURCE == 'sj':
            # Получаем секретный ключ SuperJob из переменной окружения
            sj_secret_key = os.getenv("SUPERJOB_SECRET_KEY")
            if not sj_secret_key:
                print("Ошибка: Не указан секретный ключ SuperJob. Установите переменную окружения SUPERJOB_SECRET_KEY.")
                return False
            # Инициализируем парсер SuperJob
            parser = SuperJobVacancyParser(secret_key=sj_secret_key)
        else:
            print(f"Ошибка: Неверный источник '{SOURCE}'. Используйте 'hh' или 'sj'.")
            return False

        # Запускаем парсинг
        success = parser.run_parsing(str(Path("data") / "input" / "all_vacancies_moscow.json"))
        if success:
            print("\nПарсинг завершен успешно!")
            print("Результаты сохранены в папке data/output/")
            print("JSON файлы отправлены в RabbitMQ")
        else:
            print("\nПарсинг завершился с ошибками")
            return False

    except KeyboardInterrupt:
        print("\nОстановлено пользователем")
        return False
    except Exception as e:
        print(f"\nНеожиданная ошибка: {e}")
        return False

    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)