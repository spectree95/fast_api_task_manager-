# Task Manager / Flow

Менеджер личных задач: FastAPI, SQLAlchemy и PostgreSQL на сервере, Vue и Vite в интерфейсе. Есть регистрация, JWT-авторизация, профиль, создание и редактирование задач, фильтры, сортировка и необязательный кэш Redis. Интерфейс доступен на русском языке и поддерживает деморежим без сервера.

## Локальный запуск

Команды ниже рассчитаны на PowerShell. Для API нужен Python 3.10+ и доступная база PostgreSQL; для интерфейса — Node.js `^22.18.0` или `>=24.12.0`.

### API

Из корня проекта:

```powershell
cd backend
python -m venv venv
.\venv\Scripts\python.exe -m pip install -r requirements.txt
if (!(Test-Path .env)) { Copy-Item .env.example .env }
```

Создайте базу PostgreSQL и заполните `backend/.env`:

```dotenv
DATABASE_URL=postgresql+psycopg2://taskuser:local_password@localhost:5432/task_manager
SECRET_KEY=replace_with_a_random_secret
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REDIS_URL=
CACHE_TTL_SECONDS=60
CACHE_TASKS_KEY=tasks
```

Замените данные подключения своими. Сгенерировать `SECRET_KEY` можно командой:

```powershell
.\venv\Scripts\python.exe -c "import secrets; print(secrets.token_urlsafe(48))"
```

Примените миграции и запустите API из каталога `backend`:

```powershell
.\venv\Scripts\python.exe -m alembic upgrade head
.\venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

Документация API: <http://127.0.0.1:8000/docs>. `REDIS_URL` можно оставить пустым. Для подключения Redis укажите, например, `redis://localhost:6379/0`. `TEST_DATABASE_URL` необязателен и не используется тестами.

### Интерфейс

В другом терминале из корня проекта:

```powershell
cd frontend
npm install
npm run dev
```

Откройте адрес, который напечатает Vite. Запросы `/api` автоматически перенаправляются на `http://127.0.0.1:8000`. Для другого адреса сервера создайте `frontend/.env` по примеру `.env.example` и измените `API_PROXY_TARGET`.

## API задач

Создайте пользователя через `POST /users/`, затем получите токен через `POST /users/login`, передав `username` и `password` как форму. В запросах к задачам используйте заголовок `Authorization: Bearer <access_token>`.

| Метод | Путь | Действие |
| --- | --- | --- |
| `POST` | `/tasks/create` | Создать задачу |
| `GET` | `/tasks` | Найти задачи с фильтрами и пагинацией |
| `GET` | `/tasks/{id}` | Получить задачу |
| `PATCH` | `/tasks/{id}` | Изменить переданные поля |
| `DELETE` | `/tasks/{id}` | Удалить задачу |

Параметры `GET /tasks`:

| Параметр | Значение по умолчанию | Описание |
| --- | --- | --- |
| `q` | пустая строка | Поиск подстроки в названии или описании без учёта регистра; до 255 символов |
| `completed` | не задан | `true` — завершённые, `false` — активные; без параметра — все |
| `sort` | `created_at` | `created_at`, `updated_at` или `title` |
| `order` | `desc` | `asc` или `desc` |
| `skip` | `0` | Число пропускаемых результатов, не меньше 0 |
| `limit` | `10` | Размер страницы, от 1 до 100 |

Пример поиска активных задач:

```powershell
curl.exe -H "Authorization: Bearer <access_token>" "http://127.0.0.1:8000/tasks?q=api&completed=false&sort=title&order=asc&skip=0&limit=10"
```

Пробелы по краям `q` удаляются. Пустой поиск не ограничивает результаты. Символы `%` и `_` ищутся буквально. Поиск и счётчик `total` учитывают все фильтры и только задачи текущего пользователя. Кэш разделён по пользователю и параметрам запроса; создание, изменение и удаление задач сбрасывают его для этого пользователя.

### Проверка данных

Создание задачи принимает `title` и необязательное `description`:

```json
{"title": "Подготовить релиз", "description": "Проверить список изменений"}
```

- Название: от 1 до 255 символов после удаления пробелов по краям.
- Описание: до 1000 символов; при создании по умолчанию `""`.
- `PATCH` принимает только `title`, `description` и `completed`. Пропущенные поля сохраняют свои значения; пустой объект оставляет задачу без изменений.
- Для очистки описания передайте `"description": ""`. Явный `null` в обновлениях отклоняется.
- `completed` принимает JSON-значения `true` и `false`, без преобразования строк и чисел.
- Неизвестные поля и некорректные значения возвращают `422` до записи в базу.

## Проверки

Из каталога `backend`:

```powershell
.\venv\Scripts\python.exe -m pytest -q
```

Pytest запускает тесты из `tests` и `checks`. До импорта приложения настройки заменяются тестовыми; каждый тест получает отдельную базу SQLite в памяти. Настроенные в `.env` базы PostgreSQL и Redis не используются и не изменяются. Проверки кэша используют замену Redis в памяти.

Покрыты авторизация, владение задачами, CRUD, ограничения входных данных, поиск, экранирование спецсимволов, фильтры, пагинация, изоляция кэша и его сброс. Эти проверки не заменяют интеграционный прогон с настоящими PostgreSQL и Redis.

Из каталога `frontend`:

```powershell
npm test
npm run build
```
