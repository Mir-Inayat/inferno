import requests
import os
import json

def test_upload():
    url = 'http://localhost:5000/upload'
    test_file = r"C:\Users\inayat\Downloads\Mir Inayat Ahmed-outlier_cv.pdf"  # Your file path
    
    # Check if file exists
    if not os.path.exists(test_file):
        print(f"Error: File not found at {test_file}")
        return

    try:
        with open(test_file, 'rb') as f:
            files = {'file': ('test_document.pdf', f, 'application/pdf')}
            print("Uploading file...")
            response = requests.post(url, files=files)
            
        if response.status_code == 200:
            result = response.json()
            print("\nSuccess! Analysis Results:")
            print("------------------------")
            print(json.dumps(result, indent=2))
        else:
            print(f"Error {response.status_code}:", response.text)
            
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to server. Make sure Flask is running on http://localhost:5000")
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == '__main__':
    test_upload()
