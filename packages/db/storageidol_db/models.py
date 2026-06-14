"""
SQLAlchemy 2 async ORM models — shared across all platform services.

Schema rules:
  - All tables have a `client_id` column for explicit multi-tenant partitioning.
    Queries MUST always filter by `client_id`; the application enforces this,
    not the DB (each client has a separate Postgres instance in production).
  - ULIDs are used as primary keys (time-sortable, URL-safe).
  - `created_at` / `updated_at` are always UTC-aware.
"""

from __future__ import annotations

from datetime import datetime

from pgvector.sqlalchemy import Vector
from sqlalchemy import (
    BigInteger,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

from .types import Channel, ConversationStatus, DebtStage, LeadStatus, MessageRole


def _utcnow() -> datetime:
    from datetime import timezone
    return datetime.now(timezone.utc)


class Base(DeclarativeBase):
    """Declarative base for all StorageIdol models."""


class Contact(Base):
    """A person who has interacted with the agent — may be a tenant, lead, or debtor."""

    __tablename__ = "contacts"

    id: Mapped[str] = mapped_column(String(26), primary_key=True)
    client_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)

    # Identifying fields
    phone: Mapped[str | None] = mapped_column(String(32), nullable=True)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    crm_id: Mapped[str | None] = mapped_column(String(128), nullable=True)  # ID in the client's CRM

    # Authentication state
    auth_verified: Mapped[bool] = mapped_column(default=False)
    auth_method: Mapped[str | None] = mapped_column(String(32), nullable=True)  # phone_dni | email_id

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, onupdate=_utcnow
    )

    __table_args__ = (
        UniqueConstraint("client_id", "phone", name="uq_contact_client_phone"),
    )

    conversations: Mapped[list[Conversation]] = relationship(
        back_populates="contact", lazy="select"
    )
    debt_cases: Mapped[list[DebtCase]] = relationship(
        back_populates="contact", lazy="select"
    )
    leads: Mapped[list[Lead]] = relationship(back_populates="contact", lazy="select")


class Conversation(Base):
    """A single thread of interaction with a contact."""

    __tablename__ = "conversations"

    id: Mapped[str] = mapped_column(String(26), primary_key=True)
    client_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    contact_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("contacts.id"), nullable=False
    )

    channel: Mapped[Channel] = mapped_column(Enum(Channel), nullable=False)
    status: Mapped[ConversationStatus] = mapped_column(
        Enum(ConversationStatus), nullable=False, default=ConversationStatus.ACTIVE
    )

    # Intent classified at the start of the conversation
    detected_intent: Mapped[str | None] = mapped_column(String(64), nullable=True)

    # Langfuse trace ID for linking to LLM traces
    langfuse_trace_id: Mapped[str | None] = mapped_column(String(128), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, onupdate=_utcnow
    )
    ended_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    contact: Mapped[Contact] = relationship(back_populates="conversations")
    messages: Mapped[list[Message]] = relationship(
        back_populates="conversation", order_by="Message.created_at", lazy="select"
    )
    judge_scores: Mapped[list[JudgeScore]] = relationship(
        back_populates="conversation", lazy="select"
    )


class Message(Base):
    """A single message within a conversation."""

    __tablename__ = "messages"

    id: Mapped[str] = mapped_column(String(26), primary_key=True)
    conversation_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("conversations.id"), nullable=False, index=True
    )

    role: Mapped[MessageRole] = mapped_column(Enum(MessageRole), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)

    # Channel-specific message ID (e.g. WhatsApp message ID, Twilio call SID)
    channel_message_id: Mapped[str | None] = mapped_column(String(256), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)

    conversation: Mapped[Conversation] = relationship(back_populates="messages")


class DebtCase(Base):
    """A debt collection case for a specific contact and invoice."""

    __tablename__ = "debt_cases"

    id: Mapped[str] = mapped_column(String(26), primary_key=True)
    client_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    contact_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("contacts.id"), nullable=False
    )

    # Invoice details (read from client CRM via MCP — stored here for scheduler)
    invoice_id: Mapped[str] = mapped_column(String(128), nullable=False)
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    currency: Mapped[str] = mapped_column(String(3), default="EUR")

    stage: Mapped[DebtStage] = mapped_column(
        Enum(DebtStage), nullable=False, default=DebtStage.D3
    )
    next_action_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    payment_promise_amount: Mapped[float | None] = mapped_column(Float, nullable=True)
    payment_promise_date: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, onupdate=_utcnow
    )

    contact: Mapped[Contact] = relationship(back_populates="debt_cases")


class Lead(Base):
    """A prospective client moving through the qualification funnel."""

    __tablename__ = "leads"

    id: Mapped[str] = mapped_column(String(26), primary_key=True)
    client_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    contact_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("contacts.id"), nullable=False
    )

    status: Mapped[LeadStatus] = mapped_column(
        Enum(LeadStatus), nullable=False, default=LeadStatus.NEW
    )
    source: Mapped[str | None] = mapped_column(String(128), nullable=True)  # e.g. "whatsapp_inbound"

    # Storage unit preferences (self-storage specific — generalise when needed)
    unit_size_m2: Mapped[float | None] = mapped_column(Float, nullable=True)
    unit_duration_months: Mapped[int | None] = mapped_column(Integer, nullable=True)
    budget_eur: Mapped[float | None] = mapped_column(Float, nullable=True)

    qualified_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    handoff_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, onupdate=_utcnow
    )

    contact: Mapped[Contact] = relationship(back_populates="leads")


class JudgeScore(Base):
    """
    LLM-as-a-judge evaluation of a completed conversation.

    Written by the post-conversation Celery task (core/agents/judge.py).
    Also pushed to Langfuse as an evaluation score for that trace.
    """

    __tablename__ = "judge_scores"

    id: Mapped[str] = mapped_column(String(26), primary_key=True)
    conversation_id: Mapped[str] = mapped_column(
        String(26), ForeignKey("conversations.id"), nullable=False, index=True
    )

    # Score: 0.0 = complete failure, 1.0 = perfect resolution
    score: Mapped[float] = mapped_column(Float, nullable=False)
    # success: True if score >= 0.7 (threshold configurable per client)
    success: Mapped[bool] = mapped_column(default=False)

    reason: Mapped[str] = mapped_column(Text, nullable=False)
    model: Mapped[str] = mapped_column(String(64), nullable=False)

    evaluated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)

    conversation: Mapped[Conversation] = relationship(back_populates="judge_scores")


class KnowledgeChunk(Base):
    """
    A chunk of the client's knowledge base, embedded for FAQ RAG retrieval.

    pgvector stores the embedding; `faq_rag` module queries via cosine similarity.
    Text-embedding-3-small produces 1536-dim vectors.
    """

    __tablename__ = "knowledge_chunks"

    id: Mapped[str] = mapped_column(String(26), primary_key=True)
    client_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)

    source_file: Mapped[str] = mapped_column(String(512), nullable=False)
    chunk_index: Mapped[int] = mapped_column(Integer, nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)

    # 1536 dims for text-embedding-3-small; adjust if model changes
    embedding: Mapped[list[float]] = mapped_column(Vector(1536), nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)

    __table_args__ = (
        UniqueConstraint("client_id", "source_file", "chunk_index"),
    )


class FeedbackRow(Base):
    """
    A row from clients/<id>/feedback/feedback.csv, ingested by the scheduler.

    After ingestion the row is stored here; flagged rows become test scenarios
    for the simulate harness.
    """

    __tablename__ = "feedback_rows"

    id: Mapped[str] = mapped_column(String(26), primary_key=True)
    client_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    conversation_id: Mapped[str | None] = mapped_column(String(26), nullable=True)

    environment: Mapped[str] = mapped_column(String(16), nullable=False)  # dev | prod
    category: Mapped[str] = mapped_column(String(64), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    expected_behavior: Mapped[str | None] = mapped_column(Text, nullable=True)
    actual_behavior: Mapped[str | None] = mapped_column(Text, nullable=True)
    priority: Mapped[str] = mapped_column(String(16), default="medium")
    resolved: Mapped[bool] = mapped_column(default=False)

    ingested_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)
    csv_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
