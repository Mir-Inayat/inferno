import React, { useState } from 'react'

const Home = () => {
  const [files, setFiles] = useState([]);

  const handleFileChange = (e) => {
    const selectedFiles = Array.from(e.target.files);
    setFiles(selectedFiles);
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    // Handle multiple file submission logic here
    console.log('Files to upload:', files);
  }

  return (
    <div className="upload-container">
      <h1>Welcome</h1>
      <p>Please upload your documents here</p>
      
      <form onSubmit={handleSubmit}>
        <input 
          type="file" 
          accept=".pdf"
          multiple
          className="file-input"
          onChange={handleFileChange}
        />
        <div className="selected-files">
          {files.length > 0 && (
            <p className="file-count">
              {files.length} file{files.length !== 1 ? 's' : ''} selected
            </p>
          )}
          {files.map((file, index) => (
            <div key={index} className="file-name">
              {file.name}
            </div>
          ))}
        </div>
        <button type="submit" disabled={files.length === 0}>
          Submit
        </button>
      </form>
    </div>
  )
}

export default Home