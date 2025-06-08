#!/usr/bin/env python3
"""
Главный модуль для запуска парсинга вакансий с HH.ru или SuperJob
"""
import os
import sys
from pathlib import Path
from multiprocessing import Process, Value
from ctypes import c_bool

# Добавляем корневую директорию проекта в путь
project_root = Path(__file__).parent.parent  # ~/PycharmProjects/cdek/vacancy_parser
sys.path.append(str(project_root))

from src.parsers.hh_parser import HHVacancyParser
from src.parsers.superjob_parse import SuperJobVacancyParser

def run_parser(parser_class, input_file: str, success_flag: Value):
    """Запускает парсер в отдельном процессе и обновляет флаг успеха"""
    try:
        parser = parser_class()
        success = parser.run_parsing(str(input_file))
        with success_flag.get_lock():
            success_flag.value = success
        if success:
            print(f"\nПарсинг {parser_class.__name__} завершен успешно!")
        else:
            print(f"\nПарсинг {parser_class.__name__} завершился с ошибками")
    except Exception as e:
        print(f"\nОшибка в {parser_class.__name__}: {e}")
        with success_flag.get_lock():
            success_flag.value = False

def main():
    """Основная функция запуска парсинга"""

    # Укажите источник: 'hh' для HH.ru, 'sj' для SuperJob, 'both' для параллельного запуска
    SOURCE = 'both'

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
            # Инициализируем и запускаем парсер HH
            parser = HHVacancyParser()
            success = parser.run_parsing(str(Path("data") / "input" / "all_vacancies_moscow.json"))
            if success:
                print("\nПарсинг HH.ru завершен успешно!")
                print("Результаты сохранены в папке data/output/")
                print("JSON файлы отправлены в RabbitMQ")
            else:
                print("\nПарсинг HH.ru завершился с ошибками")
                return False

        elif SOURCE == 'sj':
            # Инициализируем и запускаем парсер SuperJob
            parser = SuperJobVacancyParser()
            success = parser.run_parsing(str(Path("data") / "input" / "all_vacancies_moscow.json"))
            if success:
                print("\nПарсинг SuperJob завершен успешно!")
                print("Результаты сохранены в папке data/output/")
                print("JSON файлы отправлены в RabbitMQ")
            else:
                print("\nПарсинг SuperJob завершился с ошибками")
                return False

        elif SOURCE == 'both':
            # Запускаем оба парсера параллельно
            hh_success = Value(c_bool, True)
            sj_success = Value(c_bool, True)

            hh_process = Process(
                target=run_parser,
                args=(HHVacancyParser, Path("data") / "input" / "all_vacancies_moscow.json", hh_success)
            )
            sj_process = Process(
                target=run_parser,
                args=(SuperJobVacancyParser, Path("data") / "input" / "all_vacancies_moscow.json", sj_success)
            )

            print("\nЗапускаем парсеры HH.ru и SuperJob параллельно...")
            hh_process.start()
            sj_process.start()

            hh_process.join()
            sj_process.join()

            if hh_success.value and sj_success.value:
                print("\nОба парсера завершили работу успешно!")
                print("Результаты сохранены в папке data/output/")
                print("JSON файлы отправлены в RabbitMQ")
                return True
            else:
                print("\nОдин или оба парсера завершились с ошибками")
                return False

        else:
            print(f"Ошибка: Неверный источник '{SOURCE}'. Используйте 'hh', 'sj' или 'both'.")
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