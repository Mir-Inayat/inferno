from celery import shared_task
from document_processor import DocumentProcessor
from models import Base, Document, Person
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os

# Database setup
DATABASE_URL = "sqlite:///./documents.db"
engine = create_engine(DATABASE_URL)
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)

processor = DocumentProcessor()

@shared_task
def process_document_async(file_path, filename):
    session = Session()
    try:
        doc_info = processor.process_document(file_path)
        if doc_info.get('status') == 'error':
            raise Exception(doc_info.get('error', 'Unknown processing error'))

        person_data = doc_info['classification']['person']
        person = session.query(Person).filter_by(
            government_id=person_data['government_id']
        ).first()

        if not person:
            person = Person(
                name=person_data['name'],
                government_id=person_data['government_id'],
                email=person_data['email']
            )
            session.add(person)

        document = Document(
            file_path=file_path,
            file_name=filename,
            primary_category=doc_info['classification']['document_type']['primary_category'],
            sub_category=doc_info['classification']['document_type']['sub_category'],
            confidence_score=doc_info['classification']['document_type']['confidence_score'],
            extracted_fields=doc_info['classification']['extracted_fields'],
            person=person,
            processing_status='completed'
        )
        session.add(document)
        session.commit()
        return {"status": "success", "file_name": filename}

    except Exception as e:
        session.rollback()
        return {"status": "error", "error": str(e)}

    finally:
        session.close()
