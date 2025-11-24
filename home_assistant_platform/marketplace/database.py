"""Marketplace database models"""

import logging
from datetime import datetime
from sqlalchemy import create_engine, Column, String, Float, Integer, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from home_assistant_platform.config.settings import settings

logger = logging.getLogger(__name__)

Base = declarative_base()


class PluginListing(Base):
    """Plugin listing in marketplace"""
    __tablename__ = "plugin_listings"
    
    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    version = Column(String, nullable=False)
    description = Column(Text)
    author = Column(String, nullable=False)
    author_id = Column(String, nullable=False)
    
    # Pricing
    price = Column(Float, default=0.0)
    is_free = Column(Boolean, default=True)
    
    # Metadata
    category = Column(String)
    tags = Column(Text)  # JSON array as string
    image_url = Column(String)
    download_url = Column(String)
    
    # Statistics
    downloads = Column(Integer, default=0)
    ratings_count = Column(Integer, default=0)
    average_rating = Column(Float, default=0.0)
    
    # Status
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    purchases = relationship("Purchase", back_populates="plugin")
    reviews = relationship("Review", back_populates="plugin")


class Purchase(Base):
    """Plugin purchase record"""
    __tablename__ = "purchases"
    
    id = Column(String, primary_key=True)
    plugin_id = Column(String, ForeignKey("plugin_listings.id"), nullable=False)
    user_id = Column(String, nullable=False)  # Hardware ID
    transaction_id = Column(String, unique=True)
    
    # Payment
    amount = Column(Float, nullable=False)
    platform_share = Column(Float, nullable=False)
    author_share = Column(Float, nullable=False)
    
    # Status
    status = Column(String, default="pending")  # pending, completed, refunded
    
    # Timestamps
    purchased_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    plugin = relationship("PluginListing", back_populates="purchases")


class Review(Base):
    """Plugin review"""
    __tablename__ = "reviews"
    
    id = Column(String, primary_key=True)
    plugin_id = Column(String, ForeignKey("plugin_listings.id"), nullable=False)
    user_id = Column(String, nullable=False)
    
    rating = Column(Integer, nullable=False)  # 1-5
    comment = Column(Text)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    plugin = relationship("PluginListing", back_populates="reviews")


class Database:
    """Marketplace database manager"""
    
    def __init__(self):
        db_url = (
            f"postgresql://{settings.marketplace_db_user}:{settings.marketplace_db_password}"
            f"@{settings.marketplace_db_host}:{settings.marketplace_db_port}/{settings.marketplace_db_name}"
        )
        self.engine = create_engine(db_url, pool_pre_ping=True)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        self._init_db()
    
    def _init_db(self):
        """Initialize database tables"""
        try:
            Base.metadata.create_all(bind=self.engine)
            logger.info("Marketplace database initialized")
        except Exception as e:
            logger.error(f"Failed to initialize marketplace database: {e}")
    
    def get_session(self):
        """Get database session"""
        return self.SessionLocal()

