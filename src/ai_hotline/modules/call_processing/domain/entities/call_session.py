"""Call session entity for managing real-time call state."""

from datetime import datetime
from enum import Enum
from typing import Optional, Dict, Any, List
from uuid import UUID, uuid4


class SessionState(str, Enum):
    """Call session state enumeration."""
    INITIALIZING = "initializing"
    WAITING_FOR_CALLER = "waiting_for_caller"
    LISTENING = "listening"
    PROCESSING = "processing"
    SPEAKING = "speaking"
    WAITING_FOR_RESPONSE = "waiting_for_response"
    ENDING = "ending"
    ENDED = "ended"
    ERROR = "error"


class ConversationTurn(str, Enum):
    """Who should speak next in the conversation."""
    CALLER = "caller"
    AI = "ai"
    SYSTEM = "system"


class CallSession:
    """Call session entity for managing real-time call interactions."""
    
    def __init__(
        self,
        call_id: UUID,
        tenant_id: UUID,
        session_id: Optional[str] = None,
    ):
        self.session_id = session_id or str(uuid4())
        self.call_id = call_id
        self.tenant_id = tenant_id
        self.state = SessionState.INITIALIZING
        self.current_turn = ConversationTurn.AI  # AI speaks first typically
        
        # Session timing
        self.created_at = datetime.utcnow()
        self.last_activity_at = datetime.utcnow()
        self.state_changed_at = datetime.utcnow()
        
        # Audio processing state
        self.current_audio_stream_id: Optional[str] = None
        self.is_recording: bool = False
        self.is_playing: bool = False
        
        # Conversation context
        self.conversation_history: List[Dict[str, Any]] = []
        self.current_prompt: Optional[str] = None
        self.last_user_input: Optional[str] = None
        self.last_ai_response: Optional[str] = None
        
        # Processing state
        self.pending_stt_requests: List[str] = []
        self.pending_llm_requests: List[str] = []
        self.pending_tts_requests: List[str] = []
        
        # Session configuration
        self.max_silence_duration_seconds: int = 10
        self.max_session_duration_seconds: int = 1800  # 30 minutes
        self.language_code: str = "ar-EG"  # Egyptian Arabic
        
        # Error handling
        self.error_count: int = 0
        self.last_error: Optional[str] = None
        self.retry_count: int = 0
        
        # Session metadata
        self.metadata: Dict[str, Any] = {}
    
    def change_state(self, new_state: SessionState, reason: Optional[str] = None) -> None:
        """Change the session state."""
        if self.state == new_state:
            return
        
        old_state = self.state
        self.state = new_state
        self.state_changed_at = datetime.utcnow()
        self.last_activity_at = datetime.utcnow()
        
        # Log state change in conversation history
        self.conversation_history.append({
            "type": "state_change",
            "from_state": old_state,
            "to_state": new_state,
            "reason": reason,
            "timestamp": self.state_changed_at.isoformat()
        })
    
    def set_turn(self, turn: ConversationTurn) -> None:
        """Set whose turn it is to speak."""
        self.current_turn = turn
        self.last_activity_at = datetime.utcnow()
    
    def start_recording(self, stream_id: str) -> None:
        """Start recording audio."""
        self.current_audio_stream_id = stream_id
        self.is_recording = True
        self.change_state(SessionState.LISTENING, "Started recording audio")
    
    def stop_recording(self) -> None:
        """Stop recording audio."""
        self.is_recording = False
        if self.state == SessionState.LISTENING:
            self.change_state(SessionState.PROCESSING, "Stopped recording audio")
    
    def start_playing(self) -> None:
        """Start playing audio to caller."""
        self.is_playing = True
        self.change_state(SessionState.SPEAKING, "Started playing audio")
    
    def stop_playing(self) -> None:
        """Stop playing audio to caller."""
        self.is_playing = False
        if self.state == SessionState.SPEAKING:
            self.change_state(SessionState.WAITING_FOR_RESPONSE, "Finished playing audio")
            self.set_turn(ConversationTurn.CALLER)
    
    def add_user_input(self, text: str, confidence: Optional[float] = None) -> None:
        """Add user input from STT."""
        self.last_user_input = text
        self.last_activity_at = datetime.utcnow()
        
        self.conversation_history.append({
            "type": "user_input",
            "text": text,
            "confidence": confidence,
            "timestamp": self.last_activity_at.isoformat()
        })
        
        # Move to processing state
        if self.state == SessionState.LISTENING:
            self.change_state(SessionState.PROCESSING, "Received user input")
    
    def add_ai_response(
        self,
        text: str,
        provider: str,
        model: str,
        processing_time_ms: Optional[int] = None
    ) -> None:
        """Add AI response from LLM."""
        self.last_ai_response = text
        self.last_activity_at = datetime.utcnow()
        
        self.conversation_history.append({
            "type": "ai_response",
            "text": text,
            "provider": provider,
            "model": model,
            "processing_time_ms": processing_time_ms,
            "timestamp": self.last_activity_at.isoformat()
        })
    
    def add_system_message(self, message: str, level: str = "info") -> None:
        """Add system message to conversation history."""
        self.conversation_history.append({
            "type": "system_message",
            "message": message,
            "level": level,
            "timestamp": datetime.utcnow().isoformat()
        })
    
    def add_error(self, error_message: str) -> None:
        """Add error to session."""
        self.error_count += 1
        self.last_error = error_message
        
        self.conversation_history.append({
            "type": "error",
            "message": error_message,
            "error_count": self.error_count,
            "timestamp": datetime.utcnow().isoformat()
        })
        
        # Change to error state if too many errors
        if self.error_count >= 3:
            self.change_state(SessionState.ERROR, f"Too many errors: {error_message}")
    
    def add_pending_request(self, request_type: str, request_id: str) -> None:
        """Add pending request to track async operations."""
        if request_type == "stt":
            self.pending_stt_requests.append(request_id)
        elif request_type == "llm":
            self.pending_llm_requests.append(request_id)
        elif request_type == "tts":
            self.pending_tts_requests.append(request_id)
    
    def remove_pending_request(self, request_type: str, request_id: str) -> None:
        """Remove completed request from pending list."""
        try:
            if request_type == "stt" and request_id in self.pending_stt_requests:
                self.pending_stt_requests.remove(request_id)
            elif request_type == "llm" and request_id in self.pending_llm_requests:
                self.pending_llm_requests.remove(request_id)
            elif request_type == "tts" and request_id in self.pending_tts_requests:
                self.pending_tts_requests.remove(request_id)
        except ValueError:
            pass  # Request not in list
    
    def set_metadata(self, key: str, value: Any) -> None:
        """Set session metadata."""
        self.metadata[key] = value
    
    def get_metadata(self, key: str, default: Any = None) -> Any:
        """Get session metadata."""
        return self.metadata.get(key, default)
    
    def is_expired(self) -> bool:
        """Check if session has expired."""
        now = datetime.utcnow()
        session_age = (now - self.created_at).total_seconds()
        return session_age > self.max_session_duration_seconds
    
    def is_idle(self) -> bool:
        """Check if session has been idle too long."""
        now = datetime.utcnow()
        idle_time = (now - self.last_activity_at).total_seconds()
        return idle_time > self.max_silence_duration_seconds
    
    def has_pending_requests(self) -> bool:
        """Check if there are any pending async requests."""
        return bool(
            self.pending_stt_requests or 
            self.pending_llm_requests or 
            self.pending_tts_requests
        )
    
    def get_conversation_context(self, max_turns: int = 10) -> List[Dict[str, Any]]:
        """Get recent conversation context for LLM prompts."""
        # Filter only user inputs and AI responses
        relevant_turns = [
            turn for turn in self.conversation_history
            if turn["type"] in ["user_input", "ai_response"]
        ]
        
        # Return last N turns
        return relevant_turns[-max_turns:] if relevant_turns else []
    
    def end_session(self, reason: str = "Session ended") -> None:
        """End the session."""
        self.change_state(SessionState.ENDED, reason)
        self.is_recording = False
        self.is_playing = False
        
        # Clear pending requests
        self.pending_stt_requests.clear()
        self.pending_llm_requests.clear()
        self.pending_tts_requests.clear()
    
    def get_session_summary(self) -> Dict[str, Any]:
        """Get session summary."""
        now = datetime.utcnow()
        duration = (now - self.created_at).total_seconds()
        
        return {
            "session_id": self.session_id,
            "call_id": str(self.call_id),
            "state": self.state,
            "current_turn": self.current_turn,
            "duration_seconds": int(duration),
            "conversation_turns": len([
                t for t in self.conversation_history 
                if t["type"] in ["user_input", "ai_response"]
            ]),
            "error_count": self.error_count,
            "last_error": self.last_error,
            "is_recording": self.is_recording,
            "is_playing": self.is_playing,
            "pending_requests": {
                "stt": len(self.pending_stt_requests),
                "llm": len(self.pending_llm_requests),
                "tts": len(self.pending_tts_requests),
            }
        }
