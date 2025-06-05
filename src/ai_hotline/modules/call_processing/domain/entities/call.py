"""Call entity for the call processing domain."""

from datetime import datetime
from enum import Enum
from typing import Optional, Dict, Any, List
from uuid import UUID, uuid4

from .....shared.database.models import BaseEntity


class CallStatus(str, Enum):
    """Call status enumeration."""
    INITIATED = "initiated"
    RINGING = "ringing"
    IN_PROGRESS = "in_progress"
    ON_HOLD = "on_hold"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class CallDirection(str, Enum):
    """Call direction enumeration."""
    INBOUND = "inbound"
    OUTBOUND = "outbound"


class CallPriority(str, Enum):
    """Call priority enumeration."""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


class Call(BaseEntity):
    """Call entity representing a phone call interaction."""
    
    def __init__(
        self,
        tenant_id: UUID,
        phone_number: str,
        direction: CallDirection,
        call_id: Optional[UUID] = None,
        caller_name: Optional[str] = None,
        priority: CallPriority = CallPriority.NORMAL,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(call_id)
        self.tenant_id = tenant_id
        self.phone_number = self._validate_phone_number(phone_number)
        self.caller_name = caller_name
        self.direction = direction
        self.status = CallStatus.INITIATED
        self.priority = priority
        self.started_at: Optional[datetime] = None
        self.ended_at: Optional[datetime] = None
        self.duration_seconds: Optional[int] = None
        self.metadata = metadata or {}
        
        # Call session data
        self.session_id: Optional[str] = None
        self.audio_file_paths: List[str] = []
        self.transcript_segments: List[Dict[str, Any]] = []
        self.llm_responses: List[Dict[str, Any]] = []
        self.error_messages: List[str] = []
        
        # Business context
        self.context_data: Dict[str, Any] = {}
        self.automation_triggered: List[str] = []
        self.satisfaction_score: Optional[float] = None
        self.resolution_achieved: Optional[bool] = None
    
    def _validate_phone_number(self, phone_number: str) -> str:
        """Validate phone number format."""
        if not phone_number:
            raise ValueError("Phone number cannot be empty")
        
        # Remove all non-digit characters except +
        cleaned = ''.join(c for c in phone_number if c.isdigit() or c == '+')
        
        if not cleaned:
            raise ValueError("Phone number must contain digits")
        
        if len(cleaned) < 8 or len(cleaned) > 15:
            raise ValueError("Phone number must be between 8 and 15 digits")
        
        return cleaned
    
    def start_call(self, session_id: str) -> None:
        """Start the call."""
        if self.status != CallStatus.INITIATED:
            raise ValueError(f"Cannot start call in status: {self.status}")
        
        self.status = CallStatus.IN_PROGRESS
        self.started_at = datetime.utcnow()
        self.session_id = session_id
    
    def end_call(self, reason: Optional[str] = None) -> None:
        """End the call."""
        if self.status in [CallStatus.COMPLETED, CallStatus.FAILED, CallStatus.CANCELLED]:
            raise ValueError(f"Call already ended with status: {self.status}")
        
        self.ended_at = datetime.utcnow()
        
        if self.started_at:
            duration = self.ended_at - self.started_at
            self.duration_seconds = int(duration.total_seconds())
        
        # Determine final status
        if reason and "error" in reason.lower():
            self.status = CallStatus.FAILED
            self.error_messages.append(reason)
        elif reason and "cancel" in reason.lower():
            self.status = CallStatus.CANCELLED
        else:
            self.status = CallStatus.COMPLETED
    
    def add_audio_file(self, file_path: str) -> None:
        """Add audio file path to the call."""
        if file_path and file_path not in self.audio_file_paths:
            self.audio_file_paths.append(file_path)
    
    def add_transcript_segment(
        self,
        text: str,
        speaker: str,
        timestamp: datetime,
        confidence: Optional[float] = None
    ) -> None:
        """Add a transcript segment to the call."""
        segment = {
            "text": text,
            "speaker": speaker,
            "timestamp": timestamp.isoformat(),
            "confidence": confidence
        }
        self.transcript_segments.append(segment)
    
    def add_llm_response(
        self,
        provider: str,
        prompt: str,
        response: str,
        model: str,
        timestamp: datetime,
        processing_time_ms: Optional[int] = None,
        tokens_used: Optional[int] = None
    ) -> None:
        """Add LLM response to the call."""
        llm_response = {
            "provider": provider,
            "model": model,
            "prompt": prompt,
            "response": response,
            "timestamp": timestamp.isoformat(),
            "processing_time_ms": processing_time_ms,
            "tokens_used": tokens_used
        }
        self.llm_responses.append(llm_response)
    
    def set_context_data(self, key: str, value: Any) -> None:
        """Set context data for the call."""
        self.context_data[key] = value
    
    def get_context_data(self, key: str, default: Any = None) -> Any:
        """Get context data from the call."""
        return self.context_data.get(key, default)
    
    def trigger_automation(self, automation_name: str) -> None:
        """Record automation trigger."""
        if automation_name not in self.automation_triggered:
            self.automation_triggered.append(automation_name)
    
    def set_satisfaction_score(self, score: float) -> None:
        """Set customer satisfaction score (0.0 to 5.0)."""
        if not 0.0 <= score <= 5.0:
            raise ValueError("Satisfaction score must be between 0.0 and 5.0")
        self.satisfaction_score = score
    
    def mark_resolution_achieved(self, achieved: bool) -> None:
        """Mark whether the call achieved its resolution goal."""
        self.resolution_achieved = achieved
    
    def get_full_transcript(self) -> str:
        """Get the full call transcript as a single string."""
        if not self.transcript_segments:
            return ""
        
        transcript_lines = []
        for segment in self.transcript_segments:
            speaker = segment.get("speaker", "Unknown")
            text = segment.get("text", "")
            transcript_lines.append(f"{speaker}: {text}")
        
        return "\n".join(transcript_lines)
    
    def get_call_summary(self) -> Dict[str, Any]:
        """Get a summary of the call."""
        return {
            "call_id": str(self.id),
            "phone_number": self.phone_number,
            "caller_name": self.caller_name,
            "direction": self.direction,
            "status": self.status,
            "priority": self.priority,
            "duration_seconds": self.duration_seconds,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "ended_at": self.ended_at.isoformat() if self.ended_at else None,
            "transcript_segments_count": len(self.transcript_segments),
            "llm_responses_count": len(self.llm_responses),
            "audio_files_count": len(self.audio_file_paths),
            "automations_triggered": self.automation_triggered,
            "satisfaction_score": self.satisfaction_score,
            "resolution_achieved": self.resolution_achieved,
        }
    
    @property
    def is_active(self) -> bool:
        """Check if the call is currently active."""
        return self.status in [CallStatus.RINGING, CallStatus.IN_PROGRESS, CallStatus.ON_HOLD]
    
    @property
    def is_completed(self) -> bool:
        """Check if the call has been completed."""
        return self.status in [CallStatus.COMPLETED, CallStatus.FAILED, CallStatus.CANCELLED]
