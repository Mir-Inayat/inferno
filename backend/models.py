from sqlalchemy import create_engine, Column, Integer, String, JSON, DateTime, Float
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class Document(Base):
    __tablename__ = 'documents'
    
    id = Column(Integer, primary_key=True)
    file_path = Column(String)
    person_id = Column(Integer)  # Link to Person table
    document_type = Column(String)
    sub_type = Column(String)
    confidence_score = Column(Float)
    processed_text = Column(String)
    summary = Column(String)
    metadata = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    
class Person(Base):
    __tablename__ = 'persons'
    
    id = Column(Integer, primary_key=True)
    name = Column(String)
    government_id = Column(String)
    email = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow) 