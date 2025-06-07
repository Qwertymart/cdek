#!/usr/bin/env python3
"""
Главный модуль для запуска парсинга вакансий HH.ru
"""
import os
import sys
from pathlib import Path

# Добавляем корневую директорию проекта в путь
project_root = Path(__file__).parent.parent  # ~/PycharmProjects/cdek/vacancy_parser
sys.path.append(str(project_root))

from src.parsers.hh_parser import HHVacancyParser

def main():
    """Основная функция запуска парсинга"""
    print("Запуск парсера вакансий HH.ru")

    # Инициализируем парсер
    parser = HHVacancyParser()

    # Указываем входной файл относительно корня проекта
    input_file = project_root / "data" / "input" / "golang_vacancies_moscow.json"

    # Проверяем существование входного файла
    if not input_file.exists():
        print(f"Входной файл не найден: {input_file}")
        print("Убедитесь, что файл golang_vacancies_moscow.json существует в папке data/input/")
        return False

    try:
        # Запускаем парсинг, передавая относительный путь от корня проекта
        success = parser.run_parsing(str(Path("data") / "input" / "golang_vacancies_moscow.json"))
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