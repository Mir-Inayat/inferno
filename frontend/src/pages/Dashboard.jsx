import React, { useState, useEffect } from 'react'

const Dashboard = () => {
  const [documentData, setDocumentData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [filters, setFilters] = useState({
    documentType: 'all',
    dateRange: 'all',
    confidenceScore: 'all'
  });

  const handleFilterChange = (filterName, value) => {
    setFilters(prev => ({
      ...prev,
      [filterName]: value
    }));
  };

  useEffect(() => {
    const fetchDocumentData = async () => {
      try {
        const response = await fetch('/api/document-analysis'); // Adjust the endpoint as needed
        if (!response.ok) {
          throw new Error('Failed to fetch document data');
        }
        const data = await response.json();
        setDocumentData(data);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchDocumentData();
  }, []);

  if (loading) {
    return <div className="dashboard-container">Loading...</div>;
  }

  if (error) {
    return <div className="dashboard-container">Error: {error}</div>;
  }

  if (!documentData) {
    return <div className="dashboard-container">No document data available</div>;
  }

  const filterDocumentData = (data) => {
    if (!data) return null;
    
    let filteredData = { ...data };

    if (filters.documentType !== 'all') {
      if (filteredData.classification.document_type.primary_category !== filters.documentType) {
        return null;
      }
    }

    if (filters.confidenceScore !== 'all') {
      const minScore = parseFloat(filters.confidenceScore);
      if (filteredData.classification.document_type.confidence_score < minScore) {
        return null;
      }
    }

    if (filters.dateRange !== 'all') {
      const date = new Date(filteredData.metadata.date_received);
      const today = new Date();
      const daysDiff = (today - date) / (1000 * 60 * 60 * 24);

      switch (filters.dateRange) {
        case 'week':
          if (daysDiff > 7) return null;
          break;
        case 'month':
          if (daysDiff > 30) return null;
          break;
        case 'quarter':
          if (daysDiff > 90) return null;
          break;
      }
    }

    return filteredData;
  };

  const filteredDocumentData = filterDocumentData(documentData);

  return (
    <div className="dashboard-container">
      <h1>Document Analysis Dashboard</h1>
      
      <div className="filters-container">
        <div className="filter-group">
          <label>Document Type:</label>
          <select 
            value={filters.documentType}
            onChange={(e) => handleFilterChange('documentType', e.target.value)}
          >
            <option value="all">All Types</option>
            <option value="invoice">Invoice</option>
            <option value="contract">Contract</option>
            <option value="application">Application</option>
          </select>
        </div>

        <div className="filter-group">
          <label>Date Range:</label>
          <select 
            value={filters.dateRange}
            onChange={(e) => handleFilterChange('dateRange', e.target.value)}
          >
            <option value="all">All Time</option>
            <option value="week">Last Week</option>
            <option value="month">Last Month</option>
            <option value="quarter">Last Quarter</option>
          </select>
        </div>

        <div className="filter-group">
          <label>Minimum Confidence Score:</label>
          <select 
            value={filters.confidenceScore}
            onChange={(e) => handleFilterChange('confidenceScore', e.target.value)}
          >
            <option value="all">All Scores</option>
            <option value="0.7">70%+</option>
            <option value="0.8">80%+</option>
            <option value="0.9">90%+</option>
          </select>
        </div>
      </div>

      {!filteredDocumentData ? (
        <div className="no-results">No documents match the selected filters</div>
      ) : (
        <>
          <div className="dashboard-card main-card">
            <h2>Document ID: {filteredDocumentData.document_id}</h2>
            <p className="summary">{filteredDocumentData.summary}</p>
          </div>

          <div className="cards-grid">
            <div className="dashboard-card">
              <h3>Personal Information</h3>
              <div className="card-content">
                <p><strong>Name:</strong> {filteredDocumentData.classification.person.name}</p>
                <p><strong>ID:</strong> {filteredDocumentData.classification.person.government_id}</p>
                <p><strong>Email:</strong> {filteredDocumentData.classification.person.email}</p>
                <div className="confidence-score">
                  Confidence Score: {(filteredDocumentData.classification.person.confidence_score * 100).toFixed(1)}%
                </div>
              </div>
            </div>

            <div className="dashboard-card">
              <h3>Document Classification</h3>
              <div className="card-content">
                <p><strong>Category:</strong> {filteredDocumentData.classification.document_type.primary_category}</p>
                <p><strong>Sub-category:</strong> {filteredDocumentData.classification.document_type.sub_category}</p>
                <div className="confidence-score">
                  Confidence Score: {(filteredDocumentData.classification.document_type.confidence_score * 100).toFixed(1)}%
                </div>
              </div>
            </div>

            <div className="dashboard-card">
              <h3>Document Metadata</h3>
              <div className="card-content">
                <p><strong>Date Received:</strong> {filteredDocumentData.metadata.date_received}</p>
                <p><strong>Processing Time:</strong> {new Date(filteredDocumentData.metadata.processing_timestamp).toLocaleString()}</p>
                <p><strong>File Type:</strong> {filteredDocumentData.metadata.file_type.toUpperCase()}</p>
                <p><strong>Pages:</strong> {filteredDocumentData.metadata.page_count}</p>
              </div>
            </div>

            <div className="dashboard-card">
              <h3>Extracted Information</h3>
              <div className="card-content">
                <p><strong>Account Type:</strong> {filteredDocumentData.extracted_fields.account_type}</p>
                <p><strong>Credit Limit:</strong> {filteredDocumentData.extracted_fields.requested_credit_limit}</p>
                <p><strong>Employment:</strong> {filteredDocumentData.extracted_fields.employment_status}</p>
                <p><strong>Annual Income:</strong> {filteredDocumentData.extracted_fields.annual_income}</p>
              </div>
            </div>
          </div>
        </>
      )}
    </div>
  )
}

export default Dashboard 