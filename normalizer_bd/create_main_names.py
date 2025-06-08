import json
import uuid
import asyncio
import aiohttp
import time
import logging
import re
from collections import defaultdict

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Конфигурация для Orion LLM API
API_BASE_URL = "https://gpt.orionsoft.ru/api/External"
OPERATING_SYSTEM_CODE = 12
API_KEY = "OrVrQoQ6T43vk0McGmHOsdvvTiX446RJ"
USER_DOMAIN_NAME = "Team32f5nBzYmAAe"
AI_MODEL_CODE = 1

# Пути к входному и выходному файлам
INPUT_JSON_PATH = "hh_job_titles_moscow.json"
OUTPUT_JSON_PATH = "job_title_mappings.json"
FAILED_DATA_PATH = "failed_data.json"

def group_titles(titles):
    """Группирует вакансии по первому слову для сохранения синонимов."""
    groups = defaultdict(list)
    for title in titles:
        # Берем первое слово (игнорируем знаки препинания и пробелы)
        key = title.split()[0].lower().strip("!@#$%^&*()_+-=[]{}|;:,.<>? ")
        groups[key].append(title)
    return list(groups.values())

async def post_llm_request(session, titles, dialog_id):
    """Отправляет список названий вакансий в LLM."""
    prompt = "Вы — эксперт в HR и нормализации названий должностей. Я предоставлю список названий вакансий, некоторые из которых могут быть синонимами или вариациями одной роли. Ваша задача — сгруппировать их в кластеры синонимов и выбрать одно основное название для каждой группы (по возможности на английском). Верните результат ТОЛЬКО в виде валидного JSON-объекта без пояснений, без markdown, без обертки. Ключ — основное название, значение — список всех вариантов. Пример: {\"Frontend Developer\": [\"Frontend Developer\", \"Frontend-разработчик\", \"Front-end Developer\"]}. Вот список: " + json.dumps(titles, ensure_ascii=False)

    request_body = {
        "operatingSystemCode": OPERATING_SYSTEM_CODE,
        "apiKey": API_KEY,
        "userDomainName": USER_DOMAIN_NAME,
        "dialogIdentifier": dialog_id,
        "aiModelCode": AI_MODEL_CODE,
        "Message": prompt
    }

    try:
        async with session.post(f"{API_BASE_URL}/PostNewRequest", json=request_body) as response:
            response_text = await response.text()
            logger.info(f"Post request for dialog {dialog_id}: Status {response.status}, Response: {response_text}")
            if response.status == 200:
                data = await response.json()
                if not data.get("isSuccess"):
                    raise Exception(f"API вернул ошибку: {data.get('description', 'Нет описания')}")
                return data
            else:
                raise Exception(f"Не удалось отправить запрос: {response.status}, Ответ: {response_text}")
    except Exception as e:
        logger.error(f"Ошибка при отправке запроса для диалога {dialog_id}: {e}")
        raise

async def get_llm_response(session, dialog_id):
    """Получает ответ от LLM для указанного dialog_id."""
    request_body = {
        "operatingSystemCode": OPERATING_SYSTEM_CODE,
        "apiKey": API_KEY,
        "dialogIdentifier": dialog_id
    }

    try:
        async with session.post(f"{API_BASE_URL}/GetNewResponse", json=request_body) as response:
            response_text = await response.text()
            logger.info(f"Get response for dialog {dialog_id}: Status {response.status}, Response: {response_text}")
            if response.status == 200:
                data = await response.json()
                if data.get("data") and data["data"].get("lastMessage"):
                    try:
                        # Убираем обертку ```json\n...\n```
                        json_str = re.sub(r'^```json\n|\n```$', '', data["data"]["lastMessage"].strip())
                        return json.loads(json_str)
                    except json.JSONDecodeError as e:
                        logger.error(f"Ошибка декодирования JSON для диалога {dialog_id}: {e}, Ответ: {data['data']['lastMessage']}")
                        return None
                else:
                    logger.warning(f"Ответ пустой для диалога {dialog_id}")
                    return None
            else:
                raise Exception(f"Не удалось получить ответ: {response.status}, Ответ: {response_text}")
    except Exception as e:
        logger.error(f"Ошибка при получении ответа для диалога {dialog_id}: {e}")
        raise

async def complete_session(session, dialog_id):
    """Очищает контекст для указанного dialog_id."""
    request_body = {
        "operatingSystemCode": OPERATING_SYSTEM_CODE,
        "apiKey": API_KEY,
        "dialogIdentifier": dialog_id
    }

    try:
        async with session.post(f"{API_BASE_URL}/CompleteSession", json=request_body) as response:
            if response.status != 200:
                logger.warning(f"Не удалось завершить сессию для диалога {dialog_id}: {response.status}")
    except Exception as e:
        logger.error(f"Ошибка при завершении сессии для диалога {dialog_id}: {e}")

async def process_group(titles):
    """Обрабатывает группу названий вакансий с помощью LLM."""
    dialog_id = f"{USER_DOMAIN_NAME}_{str(uuid.uuid4())}"

    async with aiohttp.ClientSession() as session:
        # Отправляем запрос
        try:
            await post_llm_request(session, titles, dialog_id)
        except Exception as e:
            logger.error(f"Не удалось отправить запрос для диалога {dialog_id}: {e}")
            return None

        # Опрашиваем ответ
        max_attempts = 10
        for attempt in range(max_attempts):
            await asyncio.sleep(3)
            try:
                response = await get_llm_response(session, dialog_id)
                if response:
                    await complete_session(session, dialog_id)
                    return response
                logger.info(f"Попытка {attempt + 1}/{max_attempts} для диалога {dialog_id}: ответа нет")
            except Exception as e:
                logger.error(f"Ошибка при опросе ответа для диалога {dialog_id}: {e}")

        await complete_session(session, dialog_id)
        logger.error(f"Ответ не получен после {max_attempts} попыток для диалога {dialog_id}")
        return None

async def main():
    # Читаем входной JSON
    try:
        with open(INPUT_JSON_PATH, 'r', encoding='utf-8') as f:
            job_titles = json.load(f)
    except Exception as e:
        logger.error(f"Ошибка чтения файла {INPUT_JSON_PATH}: {e}")
        return

    # Группируем вакансии
    title_groups = group_titles(job_titles)
    logger.info(f"Создано {len(title_groups)} групп вакансий")
    # Обрабатываем группы
    mappings = {}
    failed_groups = []

    for group in title_groups:
        try:
            group_mappings = await process_group(group)
            if group_mappings:
                #mappings.update(group_mappings)
                for key, variants in group_mappings.items():
                    if key in mappings:
                        # Добавляем только новые элементы, чтобы избежать дубликатов
                        existing_set = set(mappings[key])
                        for v in variants:
                            if v not in existing_set:
                                mappings[key].append(v)
                    else:
                        mappings[key] = variants
                logger.info(f"Успешно обработана группа из {len(group)} названий")
            else:
                logger.warning(f"Группа не обработана, добавляем в список для повторной обработки: {group}")
                failed_groups.append(group)
        except Exception as e:
            logger.error(f"Ошибка при обработке группы: {e}")
            failed_groups.append(group)

    # Сохраняем сопоставления
    try:
        with open(OUTPUT_JSON_PATH, 'w', encoding='utf-8') as f:
            json.dump(mappings, f, ensure_ascii=False, indent=4)
        logger.info(f"Сопоставления названий вакансий сохранены в {OUTPUT_JSON_PATH}")
    except Exception as e:
        logger.error(f"Ошибка записи в файл {OUTPUT_JSON_PATH}: {e}")

    # Сохраняем необработанные группы
    if failed_groups:
        try:
            with open(FAILED_DATA_PATH, 'w', encoding='utf-8') as f:
                json.dump(failed_groups, f, ensure_ascii=False, indent=4)
            logger.info(f"Необработанные группы сохранены в {FAILED_DATA_PATH}")
        except Exception as e:
            logger.error(f"Ошибка записи в файл {FAILED_DATA_PATH}: {e}")

if __name__ == "__main__":
    asyncio.run(main())
