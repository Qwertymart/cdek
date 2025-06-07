import requests
import json
import hashlib
import logging
import logging.handlers
from datetime import datetime
from typing import Dict, Any, List, Optional
from pathlib import Path
import time
import re
import pika


class HHVacancyParser:
    def __init__(self, log_dir: str = "../logs", rabbitmq_host: str = 'localhost',
                 queue_name: str = 'json_processing_queue'):
        self.base_url = "https://api.hh.ru/vacancies"
        self.headers = {"User-Agent": "CDEK HR Analytics/1.0"}
        self.output_dir = None
        self.chunk_size = 10
        self.saved_files = []
        self.parsed_data = []

        # RabbitMQ настройки
        self.rabbitmq_host = rabbitmq_host
        self.queue_name = queue_name
        self.connection = None
        self.channel = None
        self.rabbitmq_connected = False

        self.logger = logging.getLogger("HHVacancyParser")
        self.logger.setLevel(logging.DEBUG)

        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )

        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)

        # Создаем папку для логов
        log_path = Path(__file__).parent.parent.parent / log_dir
        log_path.mkdir(exist_ok=True)

        file_handler = logging.handlers.RotatingFileHandler(
            filename=str(log_path / "hh_parser.log"),
            maxBytes=1_000_000,
            backupCount=5
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)

    def connect_rabbitmq(self):
        """Подключение к RabbitMQ"""
        try:
            self.connection = pika.BlockingConnection(
                pika.ConnectionParameters(host=self.rabbitmq_host)
            )
            self.channel = self.connection.channel()
            self.channel.queue_declare(queue=self.queue_name, durable=True)
            self.rabbitmq_connected = True
            self.logger.info(f"Подключено к RabbitMQ на {self.rabbitmq_host}")
            return True
        except Exception as e:
            self.logger.error(f"Ошибка подключения к RabbitMQ: {e}")
            return False

    def send_to_rabbitmq(self, data: List[Dict]):
        """Отправляет данные в RabbitMQ"""
        if not self.rabbitmq_connected:
            self.logger.warning("RabbitMQ не подключен, пропускаем отправку")
            return False

        try:
            json_data = json.dumps(data, ensure_ascii=False, indent=2)
            self.channel.basic_publish(
                exchange='',
                routing_key=self.queue_name,
                body=json_data,
                properties=pika.BasicProperties(
                    delivery_mode=2,
                    content_type='application/json'
                )
            )
            self.logger.info(f"📤 Отправлено в RabbitMQ: {len(data)} вакансий")
            return True
        except Exception as e:
            self.logger.error(f"❌ Ошибка отправки в RabbitMQ: {e}")
            return False

    def close_rabbitmq(self):
        """Закрывает соединение с RabbitMQ"""
        if self.connection and not self.connection.is_closed:
            self.connection.close()
            self.logger.info("🔌 Соединение с RabbitMQ закрыто")

    def init_output_dir(self, time_str: str):
        """Инициализирует папку для сохранения результатов"""
        output_path = Path(__file__).parent.parent.parent / "data" / "output" / f"result_{time_str}"
        output_path.mkdir(parents=True, exist_ok=True)
        self.output_dir = output_path
        self.logger.info(f"Создана папка для результатов: {self.output_dir}")

    def fetch_vacancies(self, params: Dict, retries: int = 3, delay: float = 1.0) -> List[Dict]:
        """Получает список вакансий с повторными попытками"""
        for attempt in range(retries):
            try:
                response = requests.get(self.base_url, params=params, headers=self.headers)
                response.raise_for_status()
                data = response.json()
                self.logger.info(f"Получено {len(data.get('items', []))} вакансий для параметров {params}")
                return data.get("items", [])
            except requests.exceptions.HTTPError as e:
                if response.status_code == 403:
                    self.logger.error(f"403 Forbidden для параметров {params}: {e}")
                    return []
                elif response.status_code == 429:
                    self.logger.warning(f"429 Rate Limit, попытка {attempt + 1}/{retries}, жду {delay}s")
                    time.sleep(delay * (2 ** attempt))
                else:
                    self.logger.error(f"HTTP ошибка для параметров {params}: {e}")
            except requests.exceptions.RequestException as e:
                self.logger.error(f"Сетевая ошибка для параметров {params}: {e}")
                time.sleep(delay)
        self.logger.error(f"Не удалось получить вакансии для параметров {params} после {retries} попыток")
        return []

    def get_vacancy_details(self, vacancy_id: str, retries: int = 3, delay: float = 1.0) -> Optional[Dict[str, Any]]:
        """Получает полные данные по вакансии с повторными попытками"""
        self.logger.debug(f"Запрос данных для вакансии {vacancy_id}")
        for attempt in range(retries):
            try:
                response = requests.get(f"{self.base_url}/{vacancy_id}", headers=self.headers)
                response.raise_for_status()
                self.logger.info(f"Успешно получены данные для вакансии {vacancy_id}")
                return response.json()
            except requests.exceptions.HTTPError as e:
                if response.status_code == 403:
                    self.logger.error(f"403 Forbidden для вакансии {vacancy_id}: {e}")
                    return None
                elif response.status_code == 429:
                    self.logger.warning(
                        f"429 Rate Limit для вакансии {vacancy_id}, попытка {attempt + 1}/{retries}, жду {delay}s")
                    time.sleep(delay * (2 ** attempt))
                else:
                    self.logger.error(f"HTTP ошибка для вакансии {vacancy_id}: {e}")
            except requests.exceptions.RequestException as e:
                self.logger.error(f"Сетевая ошибка для вакансии {vacancy_id}: {e}")
                time.sleep(delay)
        self.logger.error(f"Не удалось получить данные для вакансии {vacancy_id} после {retries} попыток")
        return None

    def normalize_salary(self, salary_data: Optional[Dict]) -> Dict:
        """Нормализует данные о зарплате, округляя медианную зарплату до целого"""
        if not salary_data:
            self.logger.warning("Данные о зарплате отсутствуют, создается компенсация с пустыми значениями")
            compensation_str = "no_salary:default"
            compensation_id = hashlib.md5(compensation_str.encode("utf-8")).hexdigest()
            return {
                "id": compensation_id,
                "salary_min": None,
                "salary_max": None,
                "salary_median": None,
                "salary_avg": None,
                "salary_net": None,
                "currency": None,
                "bonuses": "",
                "payment_frequency": "",
                "payment_type": ""
            }

        gross = salary_data.get("gross", False)
        salary_from = salary_data.get("from")
        salary_to = salary_data.get("to")
        currency = salary_data.get("currency", "RUR")

        avg_salary = None
        if salary_from and salary_to:
            avg_salary = round((salary_from + salary_to) / 2)
        elif salary_from:
            avg_salary = round(salary_from * 1.15)
        elif salary_to:
            avg_salary = round(salary_to * 0.85)  # Assume median is 85% of max if only max is provided

        # Handle None values in compensation_str to ensure consistent hashing
        salary_from_str = str(salary_from) if salary_from is not None else "none"
        salary_to_str = str(salary_to) if salary_to is not None else "none"
        currency_str = str(currency) if currency is not None else "none"
        compensation_str = f"{salary_from_str}:{salary_to_str}:{currency_str}"
        compensation_id = hashlib.md5(compensation_str.encode("utf-8")).hexdigest()

        self.logger.debug(
            f"Нормализована зарплата: min={salary_from}, max={salary_to}, median={avg_salary}, currency={currency}, id={compensation_id}")
        return {
            "id": compensation_id,
            "salary_min": salary_from,
            "salary_max": salary_to,
            "salary_median": avg_salary,
            "salary_avg": avg_salary,
            "salary_net": not gross,
            "currency": currency,
            "bonuses": "",
            "payment_frequency": "monthly",
            "payment_type": "fixed"
        }


    def parse_benefits(self, description: str) -> Dict:
        """Анализирует описание и извлекает бенефиты"""
        benefits = {
            "health_insurance": False,
            "fuel_compensation": False,
            "mobile_compensation": False,
            "free_meals": False,
            "other_benefits": [],
            "new_column": False
        }

        desc_lower = description.lower()
        if "дмс" in desc_lower or "медицинская страховка" in desc_lower:
            benefits["health_insurance"] = True
        if "гсм" in desc_lower or "топливо" in desc_lower:
            benefits["fuel_compensation"] = True
        if "связь" in desc_lower and ("оплата" in desc_lower or "компенсация" in desc_lower):
            benefits["mobile_compensation"] = True
        if "питание" in desc_lower and ("оплата" in desc_lower or "бесплатное" in desc_lower):
            benefits["free_meals"] = True

        benefits_str = f"{benefits['health_insurance']}:{benefits['fuel_compensation']}:{benefits['mobile_compensation']}:{benefits['free_meals']}"
        benefits["id"] = hashlib.md5(benefits_str.encode("utf-8")).hexdigest()

        self.logger.debug(f"Извлечены бенефиты: {benefits}")
        return benefits

    def normalize_company_name(self, name: str) -> str:
        """Нормализует название компании"""
        name = name.lower().replace("ооо", "").replace("зао", "").replace("ао", "").strip()
        self.logger.debug(f"Нормализовано название компании: {name}")
        return name

    def generate_company_id(self, name: str) -> str:
        """Генерирует уникальный ID компании"""
        normalized_name = self.normalize_company_name(name)
        company_id = hashlib.md5(normalized_name.encode("utf-8")).hexdigest()
        self.logger.debug(f"Сгенерирован company_id: {company_id} для {name}")
        return company_id

    def extract_experience_from_description(self, description: str, experience: Optional[Dict]) -> str:
        """Извлекает требования к опыту из описания и данных API"""
        if experience and experience.get("name"):
            return experience["name"]

        desc_lower = description.lower()
        experience_patterns = [
            r'опыт[а-я\s]*(\d+)[\s-]*лет',
            r'от\s*(\d+)\s*лет',
            r'(\d+)[\s+-]*года?\s*опыт',
            r'experience[:\s]*(\d+)[\s-]*years?'
        ]

        for pattern in experience_patterns:
            match = re.search(pattern, desc_lower)
            if match:
                years = match.group(1)
                return f"От {years} лет"

        return "Не указан"

    def determine_company_size(self, employer_data: Dict) -> str:
        """Определяет размер компании на основе доступных данных"""
        return "Не указан"

    def parse_vacancy(self, vacancy_data: Dict, require_salary: bool = True) -> Optional[Dict[str, Any]]:
        """Парсит данные вакансии в формат для БД"""
        self.logger.info(f"Парсинг вакансии {vacancy_data.get('id')}")

        description = vacancy_data.get("description", "").strip()
        if not description:
            self.logger.warning(f"Вакансия {vacancy_data.get('id')} пропущена: пустое описание")
            return None

        salary_info = self.normalize_salary(vacancy_data.get("salary"))

        # Пропускаем вакансии без данных о зарплате
        if salary_info["salary_min"] is None and salary_info["salary_max"] is None:
            self.logger.warning(f"Вакансия {vacancy_data.get('id')} пропущена: отсутствуют данные о зарплате")
            return None

        benefits = self.parse_benefits(description)
        publication_date = vacancy_data.get("published_at")
        if publication_date:
            try:
                publication_date = datetime.strptime(publication_date, "%Y-%m-%dT%H:%M:%S%z").date().isoformat()
            except ValueError as e:
                self.logger.error(f"Ошибка формата даты публикации для вакансии {vacancy_data.get('id')}: {e}")
                publication_date = None

        employer_data = vacancy_data.get("employer", {})
        company_name = employer_data.get("name") or "Не указан"
        company_id = self.generate_company_id(company_name)

        name_variations = [self.normalize_company_name(company_name)]

        return {
            "vacancies": {
                "external_id": vacancy_data.get("id"),
                "similar_titles": [],
                "title": vacancy_data.get("name"),
                "exclude_keywords": [],
                "description": description,
                "requirements": vacancy_data.get("snippet", {}).get("requirement") or "",
                "work_format": self.detect_work_format(vacancy_data),
                "employment_type": vacancy_data.get("employment", {}).get("name") or "Не указан",
                "schedule": vacancy_data.get("schedule", {}).get("name") or "Не указан",
                "experience_required": self.extract_experience_from_description(description,
                                                                                vacancy_data.get("experience")),
                "source_url": vacancy_data.get("alternate_url"),
                "source_name": "hh.ru",
                "publication_date": publication_date,
                "is_relevant": True,
                "company_id": company_id,
                "compensation_id": salary_info["id"],
                "benefits_id": benefits["id"],
                "created_at": datetime.now().isoformat()
            },
            "companies": {
                "id": company_id,
                "name": company_name,
                "name_variations": name_variations,
                "industry": "Не указан",
                "size": self.determine_company_size(employer_data),
                "is_foreign": False,
                "location_city": vacancy_data.get("area", {}).get("name") or "Не указан",
                "location_radius_km": 50
            },
            "compensations": salary_info,
            "benefits": benefits,
        }

    def detect_work_format(self, vacancy_data: Dict) -> str:
        """Определяет формат работы"""
        schedule = vacancy_data.get("schedule", {}).get("name", "").lower()
        description = vacancy_data.get("description", "").lower()
        if "удален" in schedule or "remote" in schedule or "удаленная работа" in description:
            work_format = "remote"
        elif "гибрид" in schedule or "гибридный" in description:
            work_format = "hybrid"
        else:
            work_format = "office"
        self.logger.debug(f"Определен формат работы: {work_format}")
        return work_format

    def save_chunk(self, chunk_data: List[Dict], chunk_number: int) -> bool:
        """Сохраняет чанк данных в JSON файл"""
        if not self.output_dir:
            self.logger.warning("Папка для сохранения не инициализирована")
            return False

        filename = self.output_dir / f"hh_vacancies_part{chunk_number}.json"
        try:
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(chunk_data, f, ensure_ascii=False, indent=2)
            self.saved_files.append(str(filename))
            self.logger.info(f"Сохранен файл {filename} с {len(chunk_data)} вакансиями")
            return True
        except Exception as e:
            self.logger.error(f"Ошибка при сохранении файла {filename}: {e}")
            return False

    def process_and_send(self, vacancy: Dict):
        """Обрабатывает вакансию и отправляет в RabbitMQ при накоплении достаточного количества"""
        parsed = self.parse_vacancy(vacancy, require_salary=True)  # Добавлен параметр require_salary
        if parsed:
            self.parsed_data.append(parsed)

            if len(self.parsed_data) >= self.chunk_size:
                self.send_to_rabbitmq(self.parsed_data)
                self.save_chunk(self.parsed_data, len(self.saved_files) + 1)
                self.parsed_data = []

    def final_send(self):
        """Отправляет оставшиеся данные"""
        if self.parsed_data:
            self.send_to_rabbitmq(self.parsed_data)
            self.save_chunk(self.parsed_data, len(self.saved_files) + 1)
            self.parsed_data = []

    def load_job_titles(self, file_path: str) -> List[str]:
        """Загружает список названий вакансий из JSON файла"""
        try:
            full_path = Path(__file__).parent.parent.parent / file_path
            with open(full_path, "r", encoding="utf-8") as f:
                titles = json.load(f)
            self.logger.info(f"Загружено {len(titles)} названий вакансий из {file_path}")
            return titles
        except Exception as e:
            self.logger.error(f"Ошибка при загрузке файла {file_path}: {e}")
            return []

    def run_parsing(self, input_file: str) -> bool:
        """Основной метод запуска парсинга"""
        if not self.connect_rabbitmq():
            self.logger.error("Не удалось подключиться к RabbitMQ")
            return False

        job_titles = self.load_job_titles(input_file)
        if not job_titles:
            self.logger.error("Не загружены названия вакансий")
            return False

        time_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.init_output_dir(time_str)

        try:
            for title in job_titles:
                self.logger.info(f"Поиск вакансий для: {title}")
                params = {"text": title, "area": 1, "per_page": 5}

                vacancies = self.fetch_vacancies(params)
                for vacancy in vacancies:
                    time.sleep(0.5)
                    full_data = self.get_vacancy_details(vacancy["id"])
                    if full_data:
                        self.process_and_send(full_data)

            self.final_send()
            return True
        except KeyboardInterrupt:
            self.logger.info("Парсинг остановлен пользователем")
            self.final_send()
            return False
        except Exception as e:
            self.logger.error(f"Ошибка парсинга: {e}")
            return False
        finally:
            self.close_rabbitmq()