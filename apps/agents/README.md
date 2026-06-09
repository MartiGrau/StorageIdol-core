# Agents

LangGraph multi-agent system. The intelligence layer of the platform.

See `context/components/agents/README.md` for full component documentation.

## Local setup

```bash
cp .env.example .env
pip install -r requirements.txt
# Run as a Celery worker (triggered by API)
celery -A tasks worker --loglevel=info
```

## Structure (to be defined as development starts)

```
apps/agents/
├── requirements.txt
├── .env.example
├── tasks.py          # Celery task definitions
├── graphs/           # LangGraph graph definitions
│   ├── orchestrator.py
│   ├── conversation.py
│   ├── lead_nurture.py
│   ├── debt_collection.py
│   └── escalation.py
├── prompts/          # System prompts (Core layer)
├── scheduler/        # Debt D+N scheduler engine
└── tests/
```
