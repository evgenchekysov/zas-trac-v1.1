
# ADR-002: Backend Project Structure

## Статус
Accepted (production baseline)

## Контекст

В рамках development ZAS-TRAC backend сформировалась многослойная структура,
отражающая архитектурные принципы разделения ответственности
(API / Workflow / Domain / Infrastructure).

Необходимо зафиксировать структуру проекта как архитектурный контракт,
чтобы предотвратить её случайную деградацию при дальнейшем развитии.

## Решение

Backend проекта ZAS-TRAC имеет следующую логическую структуру:

- `core/` — инфраструктурный и кросс-срезовый слой
  - auth, deps, config, errors, transitions
- `routers/` — API слой (FastAPI routers)
  - исключительно HTTP + dependency injection
- `services/` — application / domain services
  - бизнес-правила и orchestration
- `domain/` — доменные модели и enum’ы
- `db/` — репозитории доступа к данным
- `static/` — frontend статика (временное решение для beta)
- `tg_bot/` — внешний интерфейс (Telegram bot), изолирован от backend ядра

## Инварианты

- Router-слой не содержит бизнес-логики
- Workflow и Services не зависят от FastAPI
- Domain не знает о базе данных и HTTP
- DB слой не реализует бизнес-правила
- Любое новое добавление обязано соответствовать существующему слою

## Последствия

- Архитектура становится проверяемой
- Упрощается code review
- Снижается риск скрытого beta-технического долга
- Структура backend считается частью production-контракта
.
├── README.md
├── backend
│   ├── README.md
│   ├── __pycache__
│   │   └── main.cpython-312.pyc
│   ├── core
│   │   ├── __pycache__
│   │   │   ├── config.cpython-312.pyc
│   │   │   ├── deps.cpython-312.pyc
│   │   │   └── errors.cpython-312.pyc
│   │   ├── auth.py
│   │   ├── auth_models.py
│   │   ├── config.py
│   │   ├── deps.py
│   │   ├── errors.py
│   │   └── transitions.py
│   ├── db
│   │   ├── __pycache__
│   │   │   ├── session_repo.cpython-312.pyc
│   │   │   └── ticket_repo.cpython-312.pyc
│   │   ├── asset_repo.py
│   │   ├── participant_repo.py
│   │   ├── pool.py
│   │   ├── session_repo.py
│   │   ├── ticket_repo.py
│   │   └── user_repo.py
│   ├── domain
│   │   ├── __pycache__
│   │   │   └── ticket.cpython-312.pyc
│   │   └── ticket.py
│   ├── main.py
│   ├── routers
│   │   ├── __pycache__
│   │   │   ├── assets.cpython-312.pyc
│   │   │   ├── diag.cpython-312.pyc
│   │   │   ├── sessions.cpython-312.pyc
│   │   │   └── tickets.cpython-312.pyc
│   │   ├── assets.py
│   │   ├── diag.py
│   │   ├── sessions.py
│   │   ├── tickets.py
│   │   └── users.py
│   ├── services
│   │   ├── __init__.py
│   │   ├── __pycache__
│   │   │   ├── __init__.cpython-312.pyc
│   │   │   ├── audit_service.cpython-312.pyc
│   │   │   ├── session_service.cpython-312.pyc
│   │   │   ├── session_workflow.cpython-312.pyc
│   │   │   ├── ticket_service.cpython-312.pyc
│   │   │   └── ticket_workflow.cpython-312.pyc
│   │   ├── asset_service.py
│   │   ├── audit_service.py
│   │   ├── notification_service.py
│   │   ├── session_service.py
│   │   ├── session_workflow.py
│   │   ├── ticket_service.py
│   │   ├── ticket_workflow.py
│   │   └── user_service.py
│   └── static
│       ├── add-asset.html
│       ├── add-user.html
│       ├── admin.html
│       ├── assets
│       │   └── blank
│       ├── assets-registry.html
│       ├── css
│       │   └── style.css
│       ├── index.html
│       ├── js
│       │   └── html5-qrcode.min.js
│       ├── login.html
│       ├── my-tickets.html
│       ├── reports.html
│       ├── scanner.html
│       ├── ticket-view.html
│       ├── tickets-dispatcher.html
│       ├── user-home.html
│       └── users-registry.html
├── docs
│   └── adr
│       ├── ADR-001-creator-owner-separation.md
│       └── architecture
│           └── 01_auth_and_roles.md
├── run.txt
└── tg_bot
    └── bot.py