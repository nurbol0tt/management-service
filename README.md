# Сервис управления конфигурациями

Сервис для управления конфигурациями распределённых сервисов с REST API, построенный на **Twisted** и **PostgreSQL**.

## Функциональность

- ✅ REST API для загрузки, получения и ведения истории конфигураций  
- ✅ Валидация YAML конфигураций  
- ✅ Автоматическое версионирование  
- ✅ Шаблонизация с помощью Jinja2  
- ✅ Асинхронная обработка запросов с Twisted  
- ✅ Хранение в PostgreSQL  
- ✅ Докеризация с docker-compose  
- ✅ Полное покрытие тестами  

---

## Быстрый старт

### 1. Запуск с Docker Compose

```bash
# Клонируйте проект
git clone <repository>
cd config_service

# Запустите сервисы
docker-compose up --build

# Сервис будет доступен на http://localhost:8081


# Установите зависимости
pip install -r requirements.txt

# Настройте переменные окружения
export DB_HOST=localhost
export DB_PORT=5432
export DB_NAME=config_service
export DB_USER=config_user
export DB_PASSWORD=config_password

# Запустите PostgreSQL и создайте таблицы из init.sql

# Запустите приложение
python -m main


curl http://localhost:8081/

# Загрузить конфигурацию
curl -X POST http://localhost:8081/config/my_service \
  -H "Content-Type: application/x-yaml" \
  -d '
version: 1
database:
  host: "localhost"
  port: 5432
features:
  enable_auth: true
  enable_cache: false
'
# Ответ
{
  "service": "my_service",
  "version": 1,
  "status": "saved"
}

curl http://localhost:8081/config/my_service
curl http://localhost:8081/config/my_service?version=1

# Загрузите конфигурацию с шаблоном
curl -X POST http://localhost:8081/config/template_service \
  -d '
version: 1
database:
  host: "{{ db_host }}"
  port: 5432
welcome_message: "Hello {{ user }}!"
'


# Получите обработанную конфигурацию
curl -X GET http://localhost:8081/config/template_service?template=1 \
  -H "Content-Type: application/json" \
  -d '{"user": "Alice", "db_host": "production.db"}'

Ответ:
{
  "version": 1,
  "database": {
    "host": "production.db",
    "port": 5432
  },
  "welcome_message": "Hello Alice!"
}


curl http://localhost:8080/config/my_service/history

Ответ:
[
  {"version": 3, "created_at": "2025-08-19T13:00:00"},
  {"version": 2, "created_at": "2025-08-19T12:15:00"},
  {"version": 1, "created_at": "2025-08-19T12:00:00"}
]
