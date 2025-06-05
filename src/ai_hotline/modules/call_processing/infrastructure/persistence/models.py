"""SQLAlchemy models for call processing module."""

from datetime import datetime
from sqlalchemy import Column, String, DateTime, Integer, Float, Boolean, Text, JSON, ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID, ARRAY
from sqlalchemy.orm import relationship

from src.ai_hotline.shared.database.models import TenantBaseModel


class CallModel(TenantBaseModel):
    """SQLAlchemy model for Call entity."""
    
    __tablename__ = "calls"
    
    # Call identification
    phone_number = Column(String(20), nullable=False, index=True)
    caller_name = Column(String(200), nullable=True)
    direction = Column(String(20), nullable=False)  # inbound/outbound
    status = Column(String(50), nullable=False, default="initiated")
    priority = Column(String(20), nullable=False, default="normal")
    
    # Timing
    started_at = Column(DateTime, nullable=True)
    ended_at = Column(DateTime, nullable=True)
    duration_seconds = Column(Integer, nullable=True)
    
    # Session data
    session_id = Column(String(100), nullable=True, index=True)
    audio_file_paths = Column(ARRAY(String), nullable=False, default=[])
    
    # Content
    transcript_segments = Column(JSON, nullable=False, default=[])
    llm_responses = Column(JSON, nullable=False, default=[])
    error_messages = Column(ARRAY(String), nullable=False, default=[])
    
    # Business context
    context_data = Column(JSON, nullable=False, default={})
    automation_triggered = Column(ARRAY(String), nullable=False, default=[])
      # Quality metrics
    satisfaction_score = Column(Float, nullable=True)
    resolution_achieved = Column(Boolean, nullable=True)
    
    # Additional metadata
    call_metadata = Column(JSON, nullable=False, default={})
    
    # Relationships
    sessions = relationship("CallSessionModel", back_populates="call", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<CallModel(id={self.id}, phone_number={self.phone_number}, status={self.status})>"


class CallSessionModel(TenantBaseModel):
    """SQLAlchemy model for CallSession entity."""
    
    __tablename__ = "call_sessions"
    
    # Session identification
    session_id = Column(String(100), nullable=False, unique=True, index=True)
    call_id = Column(PostgresUUID(as_uuid=True), ForeignKey("calls.id"), nullable=False)
    
    # Session state
    state = Column(String(50), nullable=False, default="initializing")
    current_turn = Column(String(20), nullable=False, default="ai")
    
    # Timing
    last_activity_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    state_changed_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    
    # Audio state
    current_audio_stream_id = Column(String(100), nullable=True)
    is_recording = Column(Boolean, nullable=False, default=False)
    is_playing = Column(Boolean, nullable=False, default=False)
    
    # Conversation context
    conversation_history = Column(JSON, nullable=False, default=[])
    current_prompt = Column(Text, nullable=True)
    last_user_input = Column(Text, nullable=True)
    last_ai_response = Column(Text, nullable=True)
    
    # Processing state
    pending_stt_requests = Column(ARRAY(String), nullable=False, default=[])
    pending_llm_requests = Column(ARRAY(String), nullable=False, default=[])
    pending_tts_requests = Column(ARRAY(String), nullable=False, default=[])
    
    # Configuration
    max_silence_duration_seconds = Column(Integer, nullable=False, default=10)
    max_session_duration_seconds = Column(Integer, nullable=False, default=1800)
    language_code = Column(String(10), nullable=False, default="ar-EG")
    
    # Error handling
    error_count = Column(Integer, nullable=False, default=0)
    last_error = Column(Text, nullable=True)
    retry_count = Column(Integer, nullable=False, default=0)
      # Session metadata
    session_metadata = Column(JSON, nullable=False, default={})
    
    # Relationships
    call = relationship("CallModel", back_populates="sessions")
    
    def __repr__(self):
        return f"<CallSessionModel(session_id={self.session_id}, state={self.state})>"
