# API

FastAPI application. Central backend for all inbound webhooks and dashboard/backoffice endpoints.

See `context/components/api/README.md` for full component documentation.

## Local setup

```bash
cp .env.example .env
# Fill in required vars (see context/operations/env-vars.md)
pip install -r requirements.txt
alembic upgrade head
uvicorn main:app --reload
```

## Structure (to be defined as development starts)

```
apps/api/
├── main.py
├── requirements.txt
├── .env.example
├── alembic/
├── app/
│   ├── routers/
│   ├── models/
│   ├── schemas/
│   └── services/
└── tests/
```
