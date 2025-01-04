import { useState, useRef } from 'react';
import '../styles/FileUpload.css';

const FileUpload = () => {
  const [isDragging, setIsDragging] = useState(false);
  const [files, setFiles] = useState([]);
  const [uploadStatus, setUploadStatus] = useState({});
  const fileInputRef = useRef(null);

  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    setIsDragging(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragging(false);
    
    const droppedFiles = Array.from(e.dataTransfer.files);
    handleFiles(droppedFiles);
  };

  const handleFileInput = (e) => {
    const selectedFiles = Array.from(e.target.files);
    handleFiles(selectedFiles);
  };

  const handleFiles = async (newFiles) => {
    // Update files state immediately for UI feedback
    setFiles((prevFiles) => [...prevFiles, ...newFiles]);
    
    // Initialize upload status for new files
    newFiles.forEach(file => {
      setUploadStatus(prev => ({
        ...prev,
        [file.name]: { status: 'uploading' }
      }));
    });

    // Create FormData and append files
    const formData = new FormData();
    newFiles.forEach((file) => {
      formData.append('files[]', file);
    });

    try {
      const response = await fetch('http://localhost:5000/upload', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error('Upload failed');
      }

      const data = await response.json();
      
      // Update status for each file based on response
      data.results.forEach(result => {
        setUploadStatus(prev => ({
          ...prev,
          [result.filename]: {
            status: result.status,
            message: result.status === 'error' ? result.error : null,
            analysis: result.analysis
          }
        }));
      });
    } catch (error) {
      // Update status for all files in this batch as failed
      newFiles.forEach(file => {
        setUploadStatus(prev => ({
          ...prev,
          [file.name]: {
            status: 'error',
            message: error.message
          }
        }));
      });
    }
  };

  const removeFile = (index) => {
    const fileToRemove = files[index];
    setFiles((prevFiles) => prevFiles.filter((_, i) => i !== index));
    setUploadStatus((prev) => {
      const newStatus = { ...prev };
      delete newStatus[fileToRemove.name];
      return newStatus;
    });
  };

  const getStatusIcon = (fileName) => {
    const status = uploadStatus[fileName]?.status;
    switch (status) {
      case 'uploading':
        return <i className="fas fa-spinner fa-spin" />;
      case 'success':
        return <i className="fas fa-check text-green-500" />;
      case 'error':
        return <i className="fas fa-exclamation-circle text-red-500" />;
      default:
        return null;
    }
  };

  const allFilesUploaded = files.length > 0 && files.every(file => uploadStatus[file.name]?.status === 'success');

  const handleSubmit = () => {
    // Handle the submit action here
    console.log('All files uploaded successfully. Submitting...');
  };

  return (
    <div className="file-upload-container">
      <div
        className={`drop-zone ${isDragging ? 'dragging' : ''}`}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        onClick={() => fileInputRef.current?.click()}
      >
        <div className="drop-zone-content">
          <i className="fas fa-cloud-upload-alt"></i>
          <p>Drag and drop files here or click to select</p>
          <span className="supported-files">Supports PDF, Images, and Text files</span>
        </div>
        <input
          type="file"
          ref={fileInputRef}
          onChange={handleFileInput}
          multiple
          accept=".pdf,.jpg,.jpeg,.png,.tiff,.txt"
          hidden
        />
      </div>

      {files.length > 0 && (
        <div className="file-list">
          {files.map((file, index) => (
            <div key={index} className="file-item">
              <div className="file-info">
                <span className="file-name">{file.name}</span>
                {uploadStatus[file.name]?.message && (
                  <span className="file-error">{uploadStatus[file.name].message}</span>
                )}
              </div>
              <div className="file-actions">
                {getStatusIcon(file.name)}
                <button
                  className="remove-file"
                  onClick={() => removeFile(index)}
                >
                  ×
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      {allFilesUploaded && (
        <button className="submit-button" onClick={handleSubmit}>
          Submit
        </button>
      )}
    </div>
  );
};

export default FileUpload; 