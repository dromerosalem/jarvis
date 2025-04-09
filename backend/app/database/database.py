from sqlalchemy import Column, Integer, String, Boolean, DateTime, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
import os
from datetime import datetime
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Define the database path
DATABASE_URL = "sqlite:///./leads.db"

# Create SQLAlchemy engine
engine = create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}
)

# Create sessionmaker
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create Base class
Base = declarative_base()

# Define Lead model
class Lead(Base):
    """
    SQLAlchemy model for the leads table
    """
    __tablename__ = "leads"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    category = Column(String, nullable=True)
    address = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    website = Column(String, nullable=True)
    has_website = Column(Boolean, default=False)
    source = Column(String)  # e.g., "google_maps"
    query = Column(String)   # e.g., "plumbers in Manchester"
    created_at = Column(DateTime, default=datetime.now)
    
    def __repr__(self):
        return f"<Lead {self.name}, has_website={self.has_website}>"

# Create database tables
def create_tables():
    """
    Create all database tables if they don't exist
    """
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Error creating database tables: {str(e)}")
        raise

# Dependency to get the database session
def get_db():
    """
    Get database session for dependency injection in FastAPI routes
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() 