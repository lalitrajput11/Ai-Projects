"""Memory and state persistence layer."""
import json
import os
from typing import Dict, Any, List, Optional
from datetime import datetime
from sqlalchemy import create_engine, Column, String, Integer, JSON, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import logging

logger = logging.getLogger(__name__)

Base = declarative_base()


class ConversationHistory(Base):
    """SQLAlchemy model for conversation history."""
    __tablename__ = "conversation_history"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    trigger_id = Column(String, index=True)
    timestamp = Column(DateTime, default=datetime.now)
    action = Column(String)
    parameters = Column(JSON)
    result = Column(JSON)
    status = Column(String)


class MemoryStore:
    """Persistent memory storage for the agent."""
    
    def __init__(self, db_path: str, json_path: str):
        self.db_path = db_path
        self.json_path = json_path
        
        # Ensure data directory exists
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        os.makedirs(os.path.dirname(json_path), exist_ok=True)
        
        # Initialize SQLite database
        self.engine = create_engine(f"sqlite:///{db_path}")
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
        
        # Load or initialize JSON memory
        self.memory = self._load_json_memory()
        
        logger.info(f"Memory store initialized: DB={db_path}, JSON={json_path}")
    
    def _load_json_memory(self) -> Dict[str, Any]:
        """Load memory from JSON file."""
        if os.path.exists(self.json_path):
            try:
                with open(self.json_path, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading JSON memory: {e}")
                return {"facts": [], "preferences": {}, "context": {}}
        return {"facts": [], "preferences": {}, "context": {}}
    
    def _save_json_memory(self):
        """Save memory to JSON file."""
        try:
            with open(self.json_path, 'w') as f:
                json.dump(self.memory, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Error saving JSON memory: {e}")
    
    def add_conversation(self, trigger_id: str, action: str, parameters: Dict, result: Any, status: str):
        """Add conversation to history."""
        session = self.Session()
        try:
            conversation = ConversationHistory(
                trigger_id=trigger_id,
                action=action,
                parameters=parameters,
                result=result,
                status=status
            )
            session.add(conversation)
            session.commit()
            logger.info(f"Conversation saved: {trigger_id}")
        except Exception as e:
            logger.error(f"Error saving conversation: {e}")
            session.rollback()
        finally:
            session.close()
    
    def get_recent_conversations(self, limit: int = 10) -> List[Dict]:
        """Get recent conversations."""
        session = self.Session()
        try:
            conversations = session.query(ConversationHistory)\
                .order_by(ConversationHistory.timestamp.desc())\
                .limit(limit)\
                .all()
            return [
                {
                    "trigger_id": c.trigger_id,
                    "timestamp": c.timestamp.isoformat(),
                    "action": c.action,
                    "parameters": c.parameters,
                    "result": c.result,
                    "status": c.status
                }
                for c in conversations
            ]
        finally:
            session.close()
    
    def add_fact(self, fact: str):
        """Add a fact to long-term memory."""
        if fact not in self.memory.get("facts", []):
            self.memory.setdefault("facts", []).append({
                "content": fact,
                "timestamp": datetime.now().isoformat()
            })
            self._save_json_memory()
    
    def update_context(self, key: str, value: Any):
        """Update context memory."""
        self.memory.setdefault("context", {})[key] = value
        self._save_json_memory()
    
    def get_context(self) -> Dict[str, Any]:
        """Get current context."""
        return self.memory.get("context", {})
    
    def get_facts(self) -> List[str]:
        """Get all stored facts."""
        return [f["content"] for f in self.memory.get("facts", [])]
