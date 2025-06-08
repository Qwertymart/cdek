#!/usr/bin/env python3
import json
import pika
import psycopg2
import sys
from typing import Dict, Any


class VacancyConsumer:
    def __init__(self):
        # Настройки RabbitMQ
        self.rabbitmq_host = 'localhost'
        self.queue_name = 'json_processing_queue'


        # Настройки PostgreSQL
        self.db_config = {
            'dbname': 'postgres',
            'user': 'vladimirbugrenkov',
            'password': '387n3',
            'host': 'localhost',
            'port': '5432'
        }

        # Счетчики
        self.processed_count = 0
        self.error_count = 0

        # Подключения
        self.rabbit_conn = None
        self.rabbit_channel = None
        self.pg_conn = None
        self.pg_cur = None

        # Загрузка маппинга должностей
        self.title_mapping = self._load_title_mapping()

    def _load_title_mapping(self) -> Dict[str, str]:
        """Загружает маппинг названий вакансий из файла"""
        try:
            with open('job_title_mappings.json', 'r', encoding='utf-8') as f:
                mapping = json.load(f)
            return {synonym: main for main, synonyms in mapping.items() for synonym in synonyms}
        except Exception as e:
            print(f"⚠️ Ошибка загрузки маппинга должностей: {e}")
            return {}

    def _connect_databases(self) -> bool:
        """Устанавливает соединения с RabbitMQ и PostgreSQL"""
        try:
            # Подключение к RabbitMQ
            self.rabbit_conn = pika.BlockingConnection(
                pika.ConnectionParameters(host=self.rabbitmq_host))
            self.rabbit_channel = self.rabbit_conn.channel()
            self.rabbit_channel.queue_declare(queue=self.queue_name, durable=True)
            self.rabbit_channel.basic_qos(prefetch_count=1)

            # Подключение к PostgreSQL
            self.pg_conn = psycopg2.connect(**self.db_config)
            self.pg_cur = self.pg_conn.cursor()
            self._create_tables()

            print("✓ Подключено к RabbitMQ и PostgreSQL")
            return True
        except Exception as e:
            print(f"❌ Ошибка подключения к базам данных: {e}")
            return False

    def _create_tables(self) -> None:
        """Создает таблицы в PostgreSQL если они не существуют"""
        queries = [
            """CREATE TABLE IF NOT EXISTS companies
               (
                   id
                   TEXT
                   PRIMARY
                   KEY,
                   name
                   TEXT,
                   name_variations
                   JSONB,
                   industry
                   TEXT,
                   size
                   TEXT,
                   is_foreign
                   BOOLEAN,
                   location_city
                   TEXT,
                   location_radius_km
                   INTEGER
               );""",
            """CREATE TABLE IF NOT EXISTS benefits
               (
                   id
                   TEXT
                   PRIMARY
                   KEY,
                   health_insurance
                   BOOLEAN,
                   fuel_compensation
                   BOOLEAN,
                   mobile_compensation
                   BOOLEAN,
                   free_meals
                   BOOLEAN,
                   other_benefits
                   JSONB,
                   new_column
                   BOOLEAN
               );""",
            """CREATE TABLE IF NOT EXISTS compensations
               (
                   id
                   TEXT
                   PRIMARY
                   KEY,
                   salary_min
                   NUMERIC,
                   salary_max
                   NUMERIC,
                   salary_median
                   NUMERIC,
                   salary_avg
                   NUMERIC,
                   salary_net
                   BOOLEAN,
                   currency
                   TEXT,
                   bonuses
                   TEXT,
                   payment_frequency
                   TEXT,
                   payment_type
                   TEXT
               );""",
            """CREATE TABLE IF NOT EXISTS vacancies
            (
                external_id
                TEXT
                PRIMARY
                KEY,
                title
                TEXT,
                description
                TEXT,
                requirements
                TEXT,
                work_format
                TEXT,
                employment_type
                TEXT,
                schedule
                TEXT,
                experience_required
                TEXT,
                source_url
                TEXT,
                source_name
                TEXT,
                publication_date
                DATE,
                is_relevant
                BOOLEAN,
                company_id
                TEXT
                REFERENCES
                companies
               (
                id
               ),
                compensation_id TEXT,
                benefits_id TEXT REFERENCES benefits
               (
                   id
               ),
                created_at TIMESTAMP,
                similar_titles JSONB,
                exclude_keywords JSONB,
                experience_years INTEGER []
                );"""
        ]

        for query in queries:
            self.pg_cur.execute(query)
        self.pg_conn.commit()

    def _normalize_experience(self, exp: str) -> list[int]:
        """Преобразует текст опыта работы в числовой диапазон"""
        if not exp:
            return [0, 1]

        exp = exp.lower()
        if "нет опыта" in exp:
            return [0, 1]
        if "более" in exp:
            num = int(''.join(filter(str.isdigit, exp)))
            return [num, 10]
        if "от" in exp and "до" in exp:
            parts = exp.replace("лет", "").split("до")
            return [int(''.join(filter(str.isdigit, parts[0]))),
                    int(''.join(filter(str.isdigit, parts[1])))]
        return [0, 10]

    def _process_vacancy(self, data: Dict[str, Any]) -> bool:
        """Обрабатывает и сохраняет одну вакансию"""
        try:
            # Компания
            company = data['companies']
            self.pg_cur.execute(
                """INSERT INTO companies
                   (id, name, industry, size, is_foreign, location_city, location_radius_km)
                   VALUES (%s, %s, %s, %s, %s, %s, %s) ON CONFLICT (id) DO NOTHING""",
                (company['id'], company['name'], company['industry'],
                 company['size'], company['is_foreign'],
                 company['location_city'], company['location_radius_km'])
            )

            # Бенефиты
            benefits = data['benefits']
            self.pg_cur.execute(
                """INSERT INTO benefits
                   (id, health_insurance, fuel_compensation, mobile_compensation,
                    free_meals, other_benefits, new_column)
                   VALUES (%s, %s, %s, %s, %s, %s, %s) ON CONFLICT (id) DO NOTHING""",
                (benefits['id'], benefits['health_insurance'],
                 benefits['fuel_compensation'], benefits['mobile_compensation'],
                 benefits['free_meals'], benefits['other_benefits'],
                 benefits['new_column'])
            )

            # Компенсация (если есть)
            compensation = data['compensations']
            if compensation['id']:
                self.pg_cur.execute(
                    """INSERT INTO compensations
                       (id, salary_min, salary_max, salary_median, salary_avg,
                        salary_net, currency, bonuses, payment_frequency, payment_type)
                       VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s) ON CONFLICT (id) DO NOTHING""",
                    (compensation['id'], compensation['salary_min'],
                     compensation['salary_max'], compensation['salary_median'],
                     compensation['salary_avg'], compensation['salary_net'],
                     compensation['currency'], compensation['bonuses'],
                     compensation['payment_frequency'], compensation['payment_type'])
                )

            # Вакансия
            vacancy = data['vacancies']
            title = self.title_mapping.get(vacancy['title'].strip(), vacancy['title'])
            exp_years = self._normalize_experience(vacancy['experience_required'])

            self.pg_cur.execute(
                """INSERT INTO vacancies
                   (external_id, title, description, requirements, work_format,
                    employment_type, schedule, experience_required, source_url,
                    source_name, publication_date, is_relevant, company_id,
                    compensation_id, benefits_id, created_at, similar_titles,
                    exclude_keywords, experience_years)
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                           %s) ON CONFLICT (external_id) DO
                UPDATE SET
                    title = EXCLUDED.title,
                    similar_titles = EXCLUDED.similar_titles,
                    exclude_keywords = EXCLUDED.exclude_keywords,
                    experience_years = EXCLUDED.experience_years""",
                (vacancy['external_id'], title, vacancy['description'],
                 vacancy['requirements'], vacancy['work_format'],
                 vacancy['employment_type'], vacancy['schedule'],
                 vacancy['experience_required'], vacancy['source_url'],
                 vacancy['source_name'], vacancy['publication_date'],
                 vacancy['is_relevant'], vacancy['company_id'],
                 vacancy['compensation_id'], vacancy['benefits_id'],
                 vacancy['created_at'], vacancy['similar_titles'],
                 vacancy['exclude_keywords'], exp_years)
            )

            return True

        except Exception as e:
            print(f"❌ Ошибка обработки вакансии: {e}")
            self.pg_conn.rollback()
            return False

    def _process_message(self, body: bytes) -> bool:
        """Обрабатывает одно сообщение из очереди"""
        try:
            data = json.loads(body.decode('utf-8'))

            # Поддерживаем как отдельные вакансии, так и списки
            vacancies = data if isinstance(data, list) else [data]

            for vacancy in vacancies:
                if not self._process_vacancy(vacancy):
                    return False

            self.pg_conn.commit()
            self.processed_count += 1
            print(f"Успешно обработано вакансий: {len(vacancies)} (всего: {self.processed_count})")
            return True

        except json.JSONDecodeError as e:
            print(f"Ошибка декодирования JSON: {e}")
            self.error_count += 1
            return False
        except Exception as e:
            print(f"Ошибка обработки сообщения: {e}")
            self.pg_conn.rollback()
            self.error_count += 1
            return False

    def _callback(self, ch, method, properties, body):
        """Callback для обработки сообщений RabbitMQ"""
        if self._process_message(body):
            ch.basic_ack(delivery_tag=method.delivery_tag)
        else:
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

    def start(self):
        """Запускает потребитель"""
        if not self._connect_databases():
            sys.exit(1)

        print(f"Потребитель запущен. Ожидание сообщений в очереди '{self.queue_name}'...")
        print("Для остановки нажмите CTRL+C")

        try:
            self.rabbit_channel.basic_consume(
                queue=self.queue_name,
                on_message_callback=self._callback
            )
            self.rabbit_channel.start_consuming()
        except KeyboardInterrupt:
            print("\nОстановлено пользователем")
        except Exception as e:
            print(f"❌ Критическая ошибка: {e}")
        finally:
            self._close_connections()
            print("\nСтатистика:")
            print(f"   Успешно обработано: {self.processed_count}")
            print(f"   Ошибок: {self.error_count}")

    def _close_connections(self):
        """Закрывает все соединения"""
        if self.pg_cur:
            self.pg_cur.close()
        if self.pg_conn:
            self.pg_conn.close()
        if self.rabbit_channel and self.rabbit_channel.is_open:
            self.rabbit_channel.close()
        if self.rabbit_conn and self.rabbit_conn.is_open:
            self.rabbit_conn.close()
        print("Все соединения закрыты")

if __name__ == "__main__":
    consumer = VacancyConsumer()
    consumer.start()