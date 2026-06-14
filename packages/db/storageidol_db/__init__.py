"""
storageidol-db — Shared SQLAlchemy 2 models, session factory, and Alembic helpers.

Usage:
    from storageidol_db.models import Contact, Conversation, Message
    from storageidol_db.session import get_session, engine_for
"""

from .models import (
    Base,
    Contact,
    Conversation,
    DebtCase,
    JudgeScore,
    Lead,
    Message,
)
from .session import DatabaseSettings, engine_for, get_session
from .types import Channel, ConversationStatus, DebtStage, LeadStatus, MessageRole

__all__ = [
    # Models
    "Base",
    "Contact",
    "Conversation",
    "Message",
    "DebtCase",
    "Lead",
    "JudgeScore",
    # Session
    "engine_for",
    "get_session",
    "DatabaseSettings",
    # Enums
    "Channel",
    "ConversationStatus",
    "DebtStage",
    "LeadStatus",
    "MessageRole",
]
