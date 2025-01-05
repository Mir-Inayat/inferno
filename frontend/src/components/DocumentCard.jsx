import React, { useState, useEffect } from 'react';

const DocumentCard = ({ doc, selectedLanguage, translateText }) => {
  const [translatedContent, setTranslatedContent] = useState(doc);
  const [translating, setTranslating] = useState(false);

  useEffect(() => {
    const translateContent = async () => {
      if (selectedLanguage === 'en') {
        setTranslatedContent(doc);
        return;
      }
      
      setTranslating(true);
      const translated = {
        ...doc,
        file_name: await translateText(doc.file_name, selectedLanguage),
        primary_category: await translateText(doc.primary_category, selectedLanguage),
        sub_category: await translateText(doc.sub_category, selectedLanguage),
        summary: await translateText(doc.summary, selectedLanguage)
      };
      setTranslatedContent(translated);
      setTranslating(false);
    };
    
    translateContent();
  }, [selectedLanguage, doc, translateText]);

  return (
    <div className="dashboard-card">
      {translating ? (
        <div className="translating-overlay">
          <p>Translating...</p>
        </div>
      ) : (
        <>
          <div className="card-header">
            <h2>{translatedContent.file_name}</h2>
            <span className="document-type">{translatedContent.primary_category}</span>
          </div>
          
          <div className="card-section">
            <h3>Personal Information</h3>
            <p><strong>Name:</strong> {doc.person?.name || 'N/A'}</p>
            <p><strong>Email:</strong> {doc.person?.email || 'N/A'}</p>
            <p><strong>ID:</strong> {doc.person?.government_id || 'N/A'}</p>
          </div>

          <div className="card-section">
            <h3>Document Details</h3>
            <p><strong>Category:</strong> {translatedContent.primary_category}</p>
            <p><strong>Sub-category:</strong> {translatedContent.sub_category}</p>
            <p><strong>Confidence:</strong> {(doc.confidence_score * 100).toFixed(1)}%</p>
          </div>

          {translatedContent.summary && (
            <div className="card-section">
              <h3>Summary</h3>
              <p>{translatedContent.summary}</p>
            </div>
          )}

          <div className="card-actions">
            <button onClick={() => window.open(`http://localhost:5000/download/${doc.id}`)}>
              View Document
            </button>
          </div>
        </>
      )}
    </div>
  );
};

export default DocumentCard;