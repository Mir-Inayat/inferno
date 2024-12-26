Automated Document Categorization & Summarization

Overview

This repository contains the implementation of an AI-powered tool designed for the Appian AI Application Challenge. The project aims to automate the categorization and summarization of unstructured financial documents, streamlining document management for financial institutions.

Key Features

Hierarchical Document Categorization:

Associates documents with the correct individual using identifiers like name, government ID, and email.

Categorizes by document type (e.g., applications, identity documents, receipts).

Support for Multiple Formats:

Processes PDFs, images, and text files seamlessly.

AI-Powered Automation:

Utilizes Hugging Face's LayoutLMv3 model for document classification and summarization.

Multilingual Support:

Handles documents in multiple languages.

Batch Processing Capability:

Integrates Redis and Celery for handling large batches of documents efficiently.

Drag-and-Drop Functionality:

Simplifies document upload through an intuitive drag-and-drop interface.

Voice-Enabled AI Assistant:

Communicates key document details interactively using voice-based AI.

Deployment:

Backend deployed on Streamlit Community Cloud for free and scalable hosting.

Frontend built with React for a dynamic and responsive user interface.

Technology Stack

Frontend: React for a dynamic and interactive user interface.

Backend: Hugging Face Transformers for text classification and summarization.

OCR: Tesseract for text extraction from PDFs.

Batch Processing: Redis and Celery.

Deployment:

Frontend: Deployed on platforms like Vercel or Netlify.

Backend: Deployed on Streamlit Community Cloud.

Installation

Prerequisites

Node.js

Python 3.8+

npm or yarn

Steps

Clone the repository:

git clone <repository-url>
cd <repository-folder>

Install backend dependencies:

cd backend
pip install -r requirements.txt

Install frontend dependencies:

cd ../frontend
npm install

Run the application:

Start the backend:

cd ../backend
streamlit run app.py

Start the frontend:

cd ../frontend
npm start

Usage

Drag and drop documents into the upload area on the React frontend.

View categorized results with confidence scores.

Interact with the AI assistant for voice-based document insights.

Demo

Live App URL: [Insert URL]

Demo Video: [Insert link]

File Structure

.
├── backend/              # Backend application
│   ├── app.py           # Main application script
│   ├── requirements.txt # Dependencies
│   ├── models/          # Pretrained models
│   └── templates/       # HTML templates
├── frontend/             # React frontend
│   ├── src/             # Source code
│   ├── public/          # Public assets
│   ├── package.json     # Frontend dependencies
│   └── README.md        # Frontend documentation
└── README.md             # Project documentation

Future Enhancements

Add user correction feedback.

Integrate cloud storage for document management.

Advanced compliance checks for financial regulations.

Contributors

[Your Name(s)]
