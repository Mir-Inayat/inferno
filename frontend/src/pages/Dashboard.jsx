import React, { useState, useEffect } from 'react'

const Dashboard = () => {
  const [documentData, setDocumentData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [filters, setFilters] = useState({
    person: 'all',
    documentType: 'all'
  });

  const handleFilterChange = (filterName, value) => {
    setFilters(prev => ({
      ...prev,
      [filterName]: value
    }));
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
  }, []);

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

  const renderDocumentCard = (doc) => {
    if (!doc) return null;
    
    return (
      <div key={doc.id} className="dashboard-card">
        <div className="card-header">
          <h2>{doc.file_name}</h2>
          <span className="document-type">{doc.primary_category}</span>
        </div>
        
        <div className="card-section">
          <h3>Personal Information</h3>
          <p><strong>Name:</strong> {doc.person?.name || 'N/A'}</p>
          <p><strong>Email:</strong> {doc.person?.email || 'N/A'}</p>
          <p><strong>ID:</strong> {doc.person?.government_id || 'N/A'}</p>
        </div>

        <div className="card-section">
          <h3>Document Details</h3>
          <p><strong>Category:</strong> {doc.primary_category}</p>
          <p><strong>Sub-category:</strong> {doc.sub_category}</p>
          <p><strong>Confidence:</strong> {(doc.confidence_score * 100).toFixed(1)}%</p>
        </div>

        {doc.summary && (
          <div className="card-section">
            <h3>Summary</h3>
            <p>{doc.summary}</p>
          </div>
        )}

        <div className="card-actions">
          <button onClick={() => window.open(`http://localhost:5000/download/${doc.id}`)}>
            View Document
          </button>
        </div>
      </div>
    );
  };

  return (
    <div className="dashboard-container">
      <h1>Document Analysis Dashboard</h1>
      
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
          {filteredDocuments?.map(doc => renderDocumentCard(doc))}
        </div>
      )}
    </div>
  );
};

export default Dashboard;