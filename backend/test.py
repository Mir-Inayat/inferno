from document_processor import DocumentProcessor

def test_document_processing():
    # Initialize the processor
    processor = DocumentProcessor()
    
    # Provide a valid file path to a PDF or image
    file_path = r"C:\Users\dihsa\OneDrive\Desktop\1% CLUB\saksham driving license.jpg"  # Replace with actual file path
    
    # Process the document
    result = processor.process_document(file_path)
    
    # Print the result
    print(result)

if __name__ == "__main__":
    test_document_processing()
