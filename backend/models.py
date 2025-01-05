from sqlalchemy import create_engine, Column, Integer, String, JSON, DateTime, Float, ForeignKey, Table
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

# Association table for document categories
document_categories = Table('document_categories',
    Base.metadata,
    Column('document_id', Integer, ForeignKey('documents.id')),
    Column('category_id', Integer, ForeignKey('categories.id'))
)

class Document(Base):
    __tablename__ = 'documents'
    
    id = Column(Integer, primary_key=True)
    file_path = Column(String)
    file_name = Column(String)
    file_type = Column(String)  # PDF, JPG, etc.
    file_size = Column(Integer)  # in bytes
    
    # Document Classification
    primary_category = Column(String)
    sub_category = Column(String)
    confidence_score = Column(Float)
    
    # Document Content
    processed_text = Column(String)
    summary = Column(String)
    
    # Extracted Information
    extracted_fields = Column(JSON)  # Stores all extracted key-value pairs
    
    # Metadata
    doc_metadata = Column(JSON)  # Renamed from metadata to doc_metadata
    upload_date = Column(DateTime, default=datetime.utcnow)
    last_modified = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    processing_status = Column(String)  # pending, processing, completed, failed
    
    # Relationships
    person_id = Column(Integer, ForeignKey('persons.id'))
    person = relationship("Person", back_populates="documents")
    categories = relationship("Category", secondary=document_categories, back_populates="documents")

class Person(Base):
    __tablename__ = 'persons'
    
    id = Column(Integer, primary_key=True)
    name = Column(String)
    government_id = Column(String, unique=True)
    email = Column(String, unique=True)
    phone = Column(String)
    address = Column(String)
    date_of_birth = Column(DateTime)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    documents = relationship("Document", back_populates="person")

class Category(Base):
    __tablename__ = 'categories'
    
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    parent_id = Column(Integer, ForeignKey('categories.id'))
    description = Column(String)
    
    # Relationships
    documents = relationship("Document", secondary=document_categories, back_populates="categories")
    subcategories = relationship("Category")