import React, { useState, useEffect } from 'react';
import DocumentCard from '../components/DocumentCard';
import './Dashboard.css';
const LANGUAGES = {
  'en': 'English',
  'ta': 'Tamil',
  'te': 'Telugu',
  'hi': 'Hindi',
  'ur': 'Urdu',
  'ar': 'Arabic',
  'fr': 'French',
  'es': 'Spanish'
};

const Dashboard = () => {
  const [documentData, setDocumentData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [filters, setFilters] = useState({
    person: 'all',
    documentType: 'all'
  });
  const [selectedLanguage, setSelectedLanguage] = useState('en');
  const [translations, setTranslations] = useState({});
  const [translating, setTranslating] = useState(false);

  const handleFilterChange = (filterName, value) => {
    setFilters(prev => ({
      ...prev,
      [filterName]: value
    }));
  };

  const translateText = async (text, language) => {
    if (!text || language === 'en') return text;
    
    const cacheKey = `${text}-${language}`;
    if (translations[cacheKey]) return translations[cacheKey];

    try {
      const response = await fetch('http://localhost:5000/api/translate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text, target_language: language })
      });
      const data = await response.json();
      
      if (data.error) throw new Error(data.error);
      
      setTranslations(prev => ({
        ...prev,
        [cacheKey]: data.translatedText
      }));
      
      return data.translatedText;
    } catch (error) {
      console.error('Translation error:', error);
      return text;
    }
  };

  useEffect(() => {
    const fetchDocuments = async () => {
      try {
        const response = await fetch('http://localhost:5000/api/documents');
        if (!response.ok) throw new Error('Failed to fetch documents');
        const data = await response.json();
        setDocumentData(data.documents);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchDocuments();
  }, []); // Empty dependency array to run only once on mount

  const getUniquePersons = () => {
    const persons = new Set(documentData?.map(doc => doc.person?.name).filter(Boolean));
    return ['all', ...Array.from(persons)];
  };

  const getUniqueDocumentTypes = () => {
    const types = new Set(documentData?.map(doc => doc.primary_category).filter(Boolean));
    return ['all', ...Array.from(types)];
  };

  const filteredDocuments = documentData?.filter(doc => {
    return (filters.person === 'all' || doc.person?.name === filters.person) &&
           (filters.documentType === 'all' || doc.primary_category === filters.documentType);
  });

  return (
    <div className="dashboard-container">
      <div className="dashboard-header">
        <div className="header-content">
          <h1>Document Analysis Dashboard</h1>
        
        </div>
        
      </div>
      <div className="language-section">
            <span className="language-label">Choose Language:</span>
            <select 
              value={selectedLanguage}
              onChange={(e) => setSelectedLanguage(e.target.value)}
              className="language-selector"
            >
              {Object.entries(LANGUAGES).map(([code, name]) => (
                <option key={code} value={code}>{name}</option>
              ))}
            </select>
          </div>

      <div className="filters-section">
        <select 
          value={filters.person} 
          onChange={(e) => handleFilterChange('person', e.target.value)}
        >
          {getUniquePersons().map(person => (
            <option key={person} value={person}>{person}</option>
          ))}
        </select>

        <select 
          value={filters.documentType} 
          onChange={(e) => handleFilterChange('documentType', e.target.value)}
        >
          {getUniqueDocumentTypes().map(type => (
            <option key={type} value={type}>{type}</option>
          ))}
        </select>
      </div>

      {loading ? (
        <div className="loading">Loading...</div>
      ) : error ? (
        <div className="error">Error: {error}</div>
      ) : (
        <div className="documents-grid">
          {filteredDocuments?.map(doc => (
            <DocumentCard 
              key={doc.id}
              doc={doc}
              selectedLanguage={selectedLanguage}
              translateText={translateText}
            />
          ))}
        </div>
      )}
    </div>
  );
};

export default Dashboard;