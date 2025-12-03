"""Memory system - remembers family events, preferences, and context"""

import logging
from datetime import datetime
from typing import List, Dict, Optional, Any
from sqlalchemy import Column, String, Float, Integer, Boolean, DateTime, Text, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from home_assistant_platform.config.settings import settings

logger = logging.getLogger(__name__)

Base = declarative_base()


class Memory(Base):
    """Stored memory/context"""
    __tablename__ = "memories"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    memory_type = Column(String, nullable=False)  # fact, preference, event, relationship
    key = Column(String, nullable=False, index=True)  # What to remember
    value = Column(JSON)  # The memory content
    context = Column(JSON)  # Additional context
    
    # Metadata
    user_id = Column(String, default="default", index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_accessed = Column(DateTime, default=datetime.utcnow)
    access_count = Column(Integer, default=0)


class ConversationContext(Base):
    """Conversation context for natural flow"""
    __tablename__ = "conversation_contexts"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String, nullable=False, index=True)
    
    # Context
    current_topic = Column(String)
    last_intent = Column(String)
    entities = Column(JSON)
    
    # Conversation state
    is_multi_turn = Column(Boolean, default=False)
    waiting_for = Column(String)  # What we're waiting for
    
    # Timestamp
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


# Database setup
def get_memory_db():
    """Get database session for memory system"""
    db_path = settings.data_dir / "memory.db"
    engine = create_engine(f"sqlite:///{db_path}", echo=False)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    return Session()


class MemorySystem:
    """Manages memories and context"""
    
    def __init__(self):
        self.db = get_memory_db()
    
    def remember(self, key: str, value: Any, memory_type: str = "fact", context: Optional[Dict] = None, user_id: str = "default"):
        """Remember something"""
        # Check if memory exists
        memory = self.db.query(Memory).filter(
            Memory.key == key,
            Memory.user_id == user_id
        ).first()
        
        if memory:
            memory.value = value
            memory.context = context
            memory.last_accessed = datetime.utcnow()
        else:
            memory = Memory(
                key=key,
                value=value,
                memory_type=memory_type,
                context=context,
                user_id=user_id
            )
            self.db.add(memory)
        
        self.db.commit()
        logger.info(f"Remembered: {key} = {value}")
    
    def recall(self, key: str, user_id: str = "default") -> Optional[Any]:
        """Recall a memory"""
        memory = self.db.query(Memory).filter(
            Memory.key == key,
            Memory.user_id == user_id
        ).first()
        
        if memory:
            memory.last_accessed = datetime.utcnow()
            memory.access_count += 1
            self.db.commit()
            return memory.value
        
        return None
    
    def search_memories(self, query: str, memory_type: Optional[str] = None, user_id: str = "default") -> List[Memory]:
        """Search memories"""
        search_query = self.db.query(Memory).filter(
            Memory.user_id == user_id,
            Memory.key.contains(query)
        )
        
        if memory_type:
            search_query = search_query.filter(Memory.memory_type == memory_type)
        
        return search_query.all()
    
    def get_user_preferences(self, user_id: str = "default") -> Dict[str, Any]:
        """Get all user preferences"""
        memories = self.db.query(Memory).filter(
            Memory.user_id == user_id,
            Memory.memory_type == "preference"
        ).all()
        
        return {m.key: m.value for m in memories}
    
    def remember_family_event(self, event: str, date: datetime, user_id: str = "default"):
        """Remember a family event"""
        self.remember(
            f"event_{date.date().isoformat()}",
            {
                "event": event,
                "date": date.isoformat()
            },
            memory_type="event",
            user_id=user_id
        )
    
    def get_recent_memories(self, limit: int = 5, user_id: str = "default") -> List[Memory]:
        """Get recently accessed memories"""
        return self.db.query(Memory).filter(
            Memory.user_id == user_id
        ).order_by(Memory.last_accessed.desc()).limit(limit).all()

