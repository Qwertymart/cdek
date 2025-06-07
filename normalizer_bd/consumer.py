#!/usr/bin/env python3
import os
import json
import pika
import sys
from datetime import datetime
import time


class JSONConsumer:
    def __init__(self, host='localhost', queue_name='json_processing_queue'):
        """
        Инициализация consumer для получения JSON файлов из RabbitMQ

        Args:
            host (str): Хост RabbitMQ сервера
            queue_name (str): Имя очереди
        """
        self.host = host
        self.queue_name = queue_name
        self.connection = None
        self.channel = None
        self.processed_count = 0
        self.error_count = 0
        # Глобальный счетчик файлов
        self.file_counter = 0

    def connect(self):
        """Подключение к RabbitMQ"""
        try:
            self.connection = pika.BlockingConnection(
                pika.ConnectionParameters(host=self.host)
            )
            self.channel = self.connection.channel()

            # Создаем очередь (если не существует)
            self.channel.queue_declare(queue=self.queue_name, durable=True)

            # Настраиваем QoS - обрабатываем по одному сообщению за раз
            self.channel.basic_qos(prefetch_count=1)

            print(f"✓ Подключено к RabbitMQ на {self.host}")
            print(f"✓ Очередь '{self.queue_name}' готова")
            return True

        except pika.exceptions.AMQPConnectionError:
            print("❌ Ошибка подключения к RabbitMQ!")
            print("Убедитесь, что RabbitMQ сервер запущен")
            return False
        except Exception as e:
            print(f"❌ Ошибка подключения: {e}")
            return False

    def get_next_file_number(self):
        """
        Возвращает следующий номер файла и увеличивает счетчик

        Returns:
            int: Номер файла
        """
        self.file_counter += 1
        return self.file_counter

    def process_json_file(self, file_path):
        """
        Обрабатывает JSON файл

        Args:
            file_path (str): Путь к JSON файлу

        Returns:
            dict: Результат обработки
        """
        try:
            # Проверяем существование файла
            if not os.path.exists(file_path):
                return {
                    "success": False,
                    "error": f"Файл не найден: {file_path}"
                }

            # Читаем JSON файл
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Здесь вы можете добавить свою логику обработки
            # Например:

            # 1. Подсчет количества вакансий
            if isinstance(data, list):
                vacancy_count = len(data)
            elif isinstance(data, dict):
                vacancy_count = len(data.get('items', []))
            else:
                vacancy_count = 1

            # 2. Анализ данных (пример)
            analysis_result = self.analyze_vacancies(data)

            # 3. Сохранение результата обработки (опционально)
            self.save_processing_result(file_path, analysis_result)

            return {
                "success": True,
                "vacancy_count": vacancy_count,
                "analysis": analysis_result,
                "processed_at": datetime.now().isoformat()
            }

        except json.JSONDecodeError as e:
            return {
                "success": False,
                "error": f"Ошибка парсинга JSON: {e}"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Ошибка обработки файла: {e}"
            }

    def analyze_vacancies(self, data):
        """
        Анализирует данные вакансий

        Args:
            data: JSON данные

        Returns:
            dict: Результат анализа
        """
        try:
            # Пример анализа - адаптируйте под свои данные
            analysis = {
                "total_vacancies": 0,
                "unique_companies": set(),
                "salary_ranges": [],
                "locations": set()
            }

            # Если данные - список вакансий
            if isinstance(data, list):
                vacancies = data
            elif isinstance(data, dict) and 'items' in data:
                vacancies = data['items']
            else:
                vacancies = [data]

            analysis["total_vacancies"] = len(vacancies)

            for vacancy in vacancies:
                if isinstance(vacancy, dict):
                    # Анализ компаний
                    if 'employer' in vacancy and 'name' in vacancy['employer']:
                        analysis["unique_companies"].add(vacancy['employer']['name'])

                    # Анализ зарплат
                    if 'salary' in vacancy and vacancy['salary']:
                        salary_info = vacancy['salary']
                        if 'from' in salary_info or 'to' in salary_info:
                            analysis["salary_ranges"].append({
                                "from": salary_info.get('from'),
                                "to": salary_info.get('to'),
                                "currency": salary_info.get('currency', 'RUR')
                            })

                    # Анализ локаций
                    if 'area' in vacancy and 'name' in vacancy['area']:
                        analysis["locations"].add(vacancy['area']['name'])

            # Конвертируем sets в списки для JSON сериализации
            analysis["unique_companies"] = list(analysis["unique_companies"])
            analysis["locations"] = list(analysis["locations"])
            analysis["unique_companies_count"] = len(analysis["unique_companies"])
            analysis["unique_locations_count"] = len(analysis["locations"])

            return analysis

        except Exception as e:
            return {"error": f"Ошибка анализа: {e}"}

    def save_processing_result(self, file_path, analysis_result):
        """
        Сохраняет результат обработки файла

        Args:
            file_path (str): Путь к исходному файлу
            analysis_result (dict): Результат анализа
        """
        try:
            # Создаем папку для результатов обработки
            processed_dir = "processed_results"
            os.makedirs(processed_dir, exist_ok=True)

            # Создаем имя файла результата
            base_name = os.path.basename(file_path)
            result_name = f"processed_{base_name}"
            result_path = os.path.join(processed_dir, result_name)

            # Сохраняем результат
            result_data = {
                "original_file": file_path,
                "processed_at": datetime.now().isoformat(),
                "analysis": analysis_result
            }

            with open(result_path, 'w', encoding='utf-8') as f:
                json.dump(result_data, f, ensure_ascii=False, indent=2)

            print(f"💾 Результат сохранен: {result_path}")

        except Exception as e:
            print(f"⚠️  Ошибка сохранения результата: {e}")

    def callback(self, ch, method, properties, body):
        """
        Callback функция для сохранения полученных JSON файлов
        """
        try:
            # Создаем папку для сохранения полученных файлов
            received_dir = "received_json_files"
            os.makedirs(received_dir, exist_ok=True)

            # Получаем следующий номер файла
            file_number = self.get_next_file_number()
            file_name = f"received_{file_number:04d}.json"  # Форматирование с ведущими нулями (0001, 0002, и т.д.)
            file_path = os.path.join(received_dir, file_name)

            # Сохраняем полученные данные в файл
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(body.decode('utf-8'))

            print(f"✅ Файл сохранен: {file_path}")

            # Увеличиваем счетчик успешно обработанных файлов
            self.processed_count += 1

            # Подтверждаем обработку сообщения
            ch.basic_ack(delivery_tag=method.delivery_tag)

        except Exception as e:
            print(f"❌ Ошибка сохранения файла: {e}")
            self.error_count += 1
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

    def start_consuming(self):
        """Запускает получение сообщений из очереди"""
        try:
            print("🎯 Запуск JSON Consumer...")
            print("=" * 50)

            if not self.connect():
                return False

            # Настраиваем consumer
            self.channel.basic_consume(
                queue=self.queue_name,
                on_message_callback=self.callback
            )

            print(f"👂 Ожидание сообщений из очереди '{self.queue_name}'...")
            print("⏹️  Для остановки нажмите CTRL+C")
            print("=" * 50)

            # Начинаем получать сообщения
            self.channel.start_consuming()

        except KeyboardInterrupt:
            print(f"\n⏹️  Остановлено пользователем")
            print(f"📊 Итоговая статистика:")
            print(f"   - Обработано успешно: {self.processed_count}")
            print(f"   - Ошибок: {self.error_count}")
            print(f"   - Всего файлов создано: {self.file_counter}")

            # Останавливаем получение сообщений
            self.channel.stop_consuming()
            return True

        except Exception as e:
            print(f"❌ Ошибка consumer: {e}")
            return False

    def close(self):
        """Закрываем соединение"""
        if self.connection and not self.connection.is_closed:
            self.connection.close()
            print("🔌 Соединение с RabbitMQ закрыто")


def main():
    """Главная функция"""
    consumer = JSONConsumer()

    try:
        consumer.start_consuming()
    except Exception as e:
        print(f"💥 Неожиданная ошибка: {e}")
        sys.exit(1)
    finally:
        consumer.close()


if __name__ == "__main__":
    main()