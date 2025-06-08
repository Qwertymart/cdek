# Руководство по развертыванию платформы HR-аналитики для СДЭК (без Docker)

## Введение
Это руководство описывает процесс развертывания платформы HR-аналитики и управления компенсациями для СДЭК без использования Docker. Платформа включает микросервисы на Go, фронтенд на Next.js, парсеры данных и нормализатор на Python, а также использует PostgreSQL для хранения данных и RabbitMQ для обмена сообщениями.


### Программные требования
- **Git**: для клонирования репозитория.
- **Go**: версии 1.20 или выше (для бэкенда).
- **Node.js**: версии 18 или выше (для фронтенда).
- **Python**: версии 3.10 или выше (для парсеров и нормализатора).
- **PostgreSQL**: версии 15 или выше.
- **RabbitMQ**: версии 3.9 или выше.

## Установка зависимостей
1. **Установите Git**:
   ```bash
   sudo apt update
   sudo apt install git
   ```

2. **Установите Go**:
   ```bash
   wget https://golang.org/dl/go1.20.5.linux-amd64.tar.gz
   sudo tar -C /usr/local -xzf go1.20.5.linux-amd64.tar.gz
   export PATH=$PATH:/usr/local/go/bin
   echo "export PATH=$PATH:/usr/local/go/bin" >> ~/.bashrc
   source ~/.bashrc
   ```

3. **Установите Node.js**:
   ```bash
   curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
   sudo apt install -y nodejs
   ```

4. **Установите Python**:
   ```bash
   sudo apt install python3.10 python3-pip python3-venv
   ```

5. **Установите PostgreSQL**:
   ```bash
   sudo apt install postgresql postgresql-contrib
   sudo systemctl enable postgresql
   sudo systemctl start postgresql
   ```

6. **Установите RabbitMQ**:
   ```bash
   sudo apt install rabbitmq-server
   sudo systemctl enable rabbitmq-server
   sudo systemctl start rabbitmq-server
   ```

## Подготовка окружения
1. **Клонируйте репозиторий**:
   ```bash
   git clone <repository_url>
   cd cdek
   ```

2. **Создайте файл окружения**:
   Создайте файл `.env` в корне проекта со следующими переменными:
   ```env
   # PostgreSQL
   POSTGRES_HOST=localhost
   POSTGRES_PORT=5432
   POSTGRES_USER=admin
   POSTGRES_PASSWORD=secure_password
   POSTGRES_DB=cdek_hr

   # RabbitMQ
   RABBITMQ_HOST=localhost
   RABBITMQ_PORT=5672
   RABBITMQ_USER=guest
   RABBITMQ_PASSWORD=guest

   # gRPC сервисы
   AUTH_SERVICE_PORT=50051
   DASHBOARD_SERVICE_PORT=50052
   USER_SERVICE_PORT=50053

   # Фронтенд
   NEXT_PUBLIC_API_URL=http://localhost:3000/api
   ```

3. **Настройте PostgreSQL**:
   Создайте базу данных и пользователя:
   ```bash
   sudo -u postgres psql -c "CREATE DATABASE cdek_hr;"
   sudo -u postgres psql -c "CREATE USER admin WITH PASSWORD 'secure_password';"
   sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE cdek_hr TO admin;"
   ```

4. **Проверьте RabbitMQ**:
   Убедитесь, что RabbitMQ работает:
   ```bash
   sudo rabbitmqctl status
   ```
   Панель управления доступна по адресу `http://localhost:15672` (логин/пароль: guest/guest).

## Развертывание vacancy_parser
1. **Инициализируйте Python-зависимости**:
   ```bash
   cd vacancy_parser
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Запустите парсинг**:
   Убедитесь, что RabbitMQ работает, и запустите основной скрипт для отправки JSON-файлов в брокер сообщений:
   ```bash
   python src/main.py
   ```

3. **Мониторинг**:
   Логи парсинга записываются в `vacancy_parser/logs/hh_parser.log` и `logs/sj_parser.log`. Проверьте их:
   ```bash
   tail -f logs/hh_parser.log
   ```

## Развертывание norm_consumer.py
1. **Инициализируйте Python-зависимости**:
   ```bash
   cd normalizer_bd
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Инициализируйте базу данных**:
   Убедитесь, что PostgreSQL настроен, и выполните скрипт для создания таблиц:
   ```bash
   python Create_db_resumes.py
   ```

3. **Запустите слушателя RabbitMQ**:
   Запустите `norm_consumer.py` для обработки сообщений из RabbitMQ и записи нормализованных данных в PostgreSQL:
   ```bash
   python norm_consumer.py
   ```

4. **Мониторинг**:
   Логи нормализации можно найти в `normalizer_bd/json_results` или настроить дополнительные логи в скрипте.

## Развертывание бэкенда (Go-микросервисы)
1. **Соберите и запустите auth_service**:
   ```bash
   cd auth_service
   go mod tidy
   go build -o auth_service cmd/main.go
   ./auth_service
   ```

2. **Соберите и запустите dashboard_service**:
   ```bash
   cd ../dashboard_service
   go mod tidy
   go build -o dashboard_service cmd/main.go
   ./dashboard_service
   ```

3. **Соберите и запустите user_service**:
   ```bash
   cd ../user_service
   go mod tidy
   go build -o user_service cmd/main.go
   ./user_service
   ```

4. **Мониторинг**:
   Каждый сервис слушает на портах, указанных в `.env` (50051, 50052, 50053). Логи выводятся в консоль или могут быть настроены для записи в файлы.

## Развертывание фронтенда (Next.js)
1. **Установите зависимости**:
   ```bash
   cd cdek_front
   npm install
   ```

2. **Запустите фронтенд**:
   ```bash
   npm run dev
   ```

3. **Доступ**:
   Фронтенд доступен по адресу `http://localhost:3000`. Убедитесь, что бэкенд-сервисы (auth_service, dashboard_service, user_service) запущены, так как фронтенд взаимодействует с ними через API.

## Проверка работоспособности
1. **Проверьте парсинг**:
   Убедитесь, что `vacancy_parser` отправляет JSON-файлы в RabbitMQ:
   ```bash
   sudo rabbitmqctl list_queues
   ```
   Должны быть очереди с сообщениями.

2. **Проверьте нормализацию**:
   Проверьте, что `norm_consumer.py` обрабатывает сообщения и записывает данные в PostgreSQL:
   ```bash
   psql -U admin -d cdek_hr -c "\dt"
   psql -U admin -d cdek_hr -c "SELECT * FROM resumes LIMIT 5;"
   ```

3. **Проверьте бэкенд**:
   Используйте gRPC-клиент (например, `grpcurl`) для проверки сервисов:
   ```bash
   grpcurl -plaintext localhost:50051 list
   ```

4. **Проверьте фронтенд**:
   Откройте `http://localhost:3000` в браузере и протестируйте функционал (логин, дашборд, аналитика).

## Устранение неисправностей
- **vacancy_parser не отправляет данные**:
  - Проверьте, работает ли RabbitMQ: `sudo rabbitmqctl status`.
  - Убедитесь, что `.env` содержит правильные настройки RabbitMQ.
  - Проверьте логи: `tail -f vacancy_parser/logs/hh_parser.log`.
- **norm_consumer.py не записывает в PostgreSQL**:
  - Проверьте настройки PostgreSQL в `.env`.
  - Убедитесь, что таблицы созданы: `python Create_db_resumes.py`.
  - Проверьте логи в консоли или настройте их в скрипте.
- **Go-сервисы не запускаются**:
  - Проверьте зависимости: `go mod tidy`.
  - Убедитесь, что порты (50051, 50052, 50053) свободны: `netstat -tuln`.
- **Фронтенд не подключается к бэкенду**:
  - Проверьте, что `NEXT_PUBLIC_API_URL` в `.env` корректен.
  - Убедитесь, что все Go-сервисы запущены.

## Обновление
1. Обновите репозиторий:
   ```bash
   git pull origin main
   ```
2. Переустановите зависимости:
   - Для Python: `pip install -r requirements.txt` в `vacancy_parser` и `normalizer_bd`.
   - Для Go: `go mod tidy` в каждом сервисе.
   - Для фронтенда: `npm install` в `cdek_front`.
3. Перезапустите все компоненты.

## Дополнительные замечания
- **Безопасность**:
  - Замените значения по умолчанию в `.env` (пароли, пользователи) на защищенные.
  - Ограничьте доступ к портам (5432, 5672, 50051–50053) через фаервол.
- **Бэкапы PostgreSQL**:
   ```bash
   pg_dump -U admin cdek_hr > backup.sql
   ```
- **Логи**:
  Настройте ротацию логов в `logs`, `vacancy_parser/logs` и для Go-сервисов, чтобы избежать переполнения диска.
