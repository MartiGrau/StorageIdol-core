# API

FastAPI application. Handles all inbound traffic and exposes endpoints for dashboards.

**Language:** Python 3.11 | **Framework:** FastAPI + Pydantic v2

## Responsibilities

- Receive and verify WhatsApp Cloud API webhooks
- Receive Twilio voice webhooks (inbound calls, call status)
- Expose `POST /trigger/debt` — client CRM triggers a debt notification sequence
- Expose REST endpoints consumed by `dashboard/` and `backoffice/`
- Route each inbound event to the correct Celery task (agents worker)

## Structure

```
api/
├── main.py
├── requirements.txt
├── .env.example
├── alembic/                  # DB migrations
├── app/
│   ├── routers/
│   │   ├── webhooks/
│   │   │   ├── whatsapp.py   # POST /webhook/whatsapp
│   │   │   ├── voice.py      # POST /webhook/voice + WS /ws/voice/{call_sid}
│   │   │   └── debt.py       # POST /trigger/debt
│   │   └── internal/
│   │       ├── conversations.py
│   │       ├── clients.py
│   │       └── analytics.py
│   ├── models/               # SQLAlchemy ORM models
│   │   ├── contact.py
│   │   ├── conversation.py
│   │   ├── message.py
│   │   └── debt_case.py
│   ├── schemas/              # Pydantic request/response schemas
│   └── services/
│       ├── session.py        # LangGraph session management
│       └── router.py         # Maps inbound event → correct agent graph
└── tests/
```

## Local setup

```bash
cp .env.example .env
pip install -r requirements.txt
alembic upgrade head
uvicorn main:app --reload  # Port 8000
```

## Key design decisions

- Every webhook is verified (WhatsApp signature, Twilio signature) before processing
- Webhook handlers are thin: validate → enqueue Celery task → return 200 immediately
- Long-running agent work happens in `agents/` workers, not in API request handlers
- Client routing: the phone number (or `X-Client-ID` header on internal routes) determines which client config and which agent graph to load
