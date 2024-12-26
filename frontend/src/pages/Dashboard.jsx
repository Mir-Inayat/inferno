import React from 'react'

const Dashboard = () => {
  // Example data - replace with your actual data fetching logic
  const documentData = {
    document_id: "DOC123",
    classification: {
      person: {
        name: "John Doe",
        government_id: "XXX-XX-1234",
        email: "john.doe@email.com",
        confidence_score: 0.95
      },
      document_type: {
        primary_category: "Financial Document",
        sub_category: "Bank Account Application",
        confidence_score: 0.88
      }
    },
    metadata: {
      date_received: "2024-03-15",
      processing_timestamp: "2024-03-15T10:30:00Z",
      file_type: "pdf",
      page_count: 2
    },
    summary: "Credit card application for John Doe, including personal information and financial history. Application dated March 15, 2024.",
    extracted_fields: {
      account_type: "Credit Card",
      requested_credit_limit: "$5000",
      employment_status: "Employed",
      annual_income: "$75,000"
    }
  };

  return (
    <div className="dashboard-container">
      <h1>Document Analysis Dashboard</h1>
      
      {/* Document ID and Summary Card */}
      <div className="dashboard-card main-card">
        <h2>Document ID: {documentData.document_id}</h2>
        <p className="summary">{documentData.summary}</p>
      </div>

      <div className="cards-grid">
        {/* Person Information Card */}
        <div className="dashboard-card">
          <h3>Personal Information</h3>
          <div className="card-content">
            <p><strong>Name:</strong> {documentData.classification.person.name}</p>
            <p><strong>ID:</strong> {documentData.classification.person.government_id}</p>
            <p><strong>Email:</strong> {documentData.classification.person.email}</p>
            <div className="confidence-score">
              Confidence Score: {(documentData.classification.person.confidence_score * 100).toFixed(1)}%
            </div>
          </div>
        </div>

        {/* Document Type Card */}
        <div className="dashboard-card">
          <h3>Document Classification</h3>
          <div className="card-content">
            <p><strong>Category:</strong> {documentData.classification.document_type.primary_category}</p>
            <p><strong>Sub-category:</strong> {documentData.classification.document_type.sub_category}</p>
            <div className="confidence-score">
              Confidence Score: {(documentData.classification.document_type.confidence_score * 100).toFixed(1)}%
            </div>
          </div>
        </div>

        {/* Metadata Card */}
        <div className="dashboard-card">
          <h3>Document Metadata</h3>
          <div className="card-content">
            <p><strong>Date Received:</strong> {documentData.metadata.date_received}</p>
            <p><strong>Processing Time:</strong> {new Date(documentData.metadata.processing_timestamp).toLocaleString()}</p>
            <p><strong>File Type:</strong> {documentData.metadata.file_type.toUpperCase()}</p>
            <p><strong>Pages:</strong> {documentData.metadata.page_count}</p>
          </div>
        </div>

        {/* Extracted Fields Card */}
        <div className="dashboard-card">
          <h3>Extracted Information</h3>
          <div className="card-content">
            <p><strong>Account Type:</strong> {documentData.extracted_fields.account_type}</p>
            <p><strong>Credit Limit:</strong> {documentData.extracted_fields.requested_credit_limit}</p>
            <p><strong>Employment:</strong> {documentData.extracted_fields.employment_status}</p>
            <p><strong>Annual Income:</strong> {documentData.extracted_fields.annual_income}</p>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Dashboard 