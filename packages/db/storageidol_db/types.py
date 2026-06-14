"""Shared enumerations used across models."""

import enum


class Channel(str, enum.Enum):
    """Communication channel for a conversation or message."""
    WHATSAPP = "whatsapp"
    VOICE = "voice"
    SMS = "sms"


class MessageRole(str, enum.Enum):
    """Sender of a message within a conversation."""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class ConversationStatus(str, enum.Enum):
    """Lifecycle state of a conversation."""
    ACTIVE = "active"
    ESCALATED = "escalated"   # Handed off to human
    RESOLVED = "resolved"     # Successfully closed by agent
    ABANDONED = "abandoned"   # No response from user


class DebtStage(str, enum.Enum):
    """D+N collection stage a debt case is currently in."""
    D3 = "d3"
    D10 = "d10"
    D20 = "d20"
    D30 = "d30"
    HUMAN = "human"      # Escalated to human recovery team
    RESOLVED = "resolved"
    WRITTEN_OFF = "written_off"


class LeadStatus(str, enum.Enum):
    """Status of a lead through the qualification funnel."""
    NEW = "new"
    CONTACTED = "contacted"
    QUALIFIED = "qualified"
    SCHEDULED = "scheduled"   # Visit / demo booked
    CONVERTED = "converted"
    LOST = "lost"
