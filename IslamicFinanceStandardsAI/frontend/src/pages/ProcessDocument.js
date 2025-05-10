import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';

const ProcessDocument = () => {
  const [selectedFile, setSelectedFile] = useState(null);
  const [filePath, setFilePath] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [processingStep, setProcessingStep] = useState(0);
  const navigate = useNavigate();

  const handleFileChange = (e) => {
    if (e.target.files.length > 0) {
      setSelectedFile(e.target.files[0]);
      // In a real implementation, this would handle file upload
      // For the demo, we'll just set a mock file path
      setFilePath(`/Users/faycalamrouche/Desktop/IsDBI/Resources/${e.target.files[0].name}`);
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!filePath) {
      setError('Please select a file or enter a file path');
      return;
    }

    setLoading(true);
    setError('');
    setProcessingStep(1);

    // Simulate document processing steps with timeouts
    setTimeout(() => {
      setProcessingStep(2);
      setTimeout(() => {
        setProcessingStep(3);
        setTimeout(() => {
          setProcessingStep(4);
          setTimeout(() => {
            setProcessingStep(5);
            setTimeout(() => {
              setLoading(false);
              // Redirect to the newly processed standard (mock ID for demo)
              navigate('/standards/6');
            }, 1500);
          }, 2000);
        }, 2000);
      }, 2000);
    }, 2000);
  };

  const renderProcessingStatus = () => {
    const steps = [
      { id: 1, label: 'Extracting text from document' },
      { id: 2, label: 'Identifying key definitions and concepts' },
      { id: 3, label: 'Extracting accounting treatments and transaction structures' },
      { id: 4, label: 'Identifying potential ambiguities' },
      { id: 5, label: 'Storing in knowledge graph' }
    ];

    return (
      <div style={{ marginTop: '1.5rem' }}>
        <h3 style={{ marginBottom: '1rem', fontWeight: '600' }}>Processing Status</h3>
        <div style={{ 
          display: 'flex',
          flexDirection: 'column',
          gap: '0.75rem'
        }}>
          {steps.map(step => (
            <div 
              key={step.id} 
              style={{ 
                display: 'flex',
                alignItems: 'center',
                padding: '0.75rem',
                backgroundColor: processingStep >= step.id ? 'rgba(16, 185, 129, 0.1)' : 'var(--background)',
                borderRadius: '0.375rem',
                border: `1px solid ${processingStep >= step.id ? 'var(--primary)' : 'var(--border)'}`,
              }}
            >
              {processingStep > step.id ? (
                <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="var(--success)" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{ marginRight: '0.75rem' }}>
                  <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path>
                  <polyline points="22 4 12 14.01 9 11.01"></polyline>
                </svg>
              ) : processingStep === step.id ? (
                <div style={{ 
                  width: '20px', 
                  height: '20px', 
                  borderRadius: '50%', 
                  border: '2px solid var(--primary)',
                  borderTopColor: 'transparent',
                  animation: 'spin 1s linear infinite',
                  marginRight: '0.75rem'
                }}></div>
              ) : (
                <div style={{ 
                  width: '20px', 
                  height: '20px', 
                  borderRadius: '50%', 
                  border: '2px solid var(--border)',
                  marginRight: '0.75rem'
                }}></div>
              )}
              <span style={{ 
                color: processingStep >= step.id ? 'var(--text-primary)' : 'var(--text-secondary)',
                fontWeight: processingStep === step.id ? '500' : 'normal'
              }}>
                {step.label}
              </span>
            </div>
          ))}
        </div>
        <style jsx>{`
          @keyframes spin {
            to { transform: rotate(360deg); }
          }
        `}</style>
      </div>
    );
  };

  return (
    <div>
      <h1 className="card-title" style={{ marginBottom: '1.5rem' }}>Process AAOIFI Standard Document</h1>
      
      <div className="card">
        <p style={{ marginBottom: '1.5rem' }}>
          Upload or specify the path to an AAOIFI standard document (FAS or SS) to process.
          The Document Agent will extract key elements and store them in the knowledge graph.
        </p>

        {error && (
          <div className="alert alert-error" style={{ marginBottom: '1.5rem' }}>
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label className="form-label">Upload Document</label>
            <input 
              type="file" 
              accept=".pdf,.docx,.txt" 
              onChange={handleFileChange}
              disabled={loading}
              className="form-input"
              style={{ padding: '0.5rem' }}
            />
            <p style={{ fontSize: '0.875rem', color: 'var(--text-secondary)', marginTop: '0.5rem' }}>
              Supported formats: PDF, DOCX, TXT
            </p>
          </div>

          <div className="form-group">
            <label className="form-label">Or Enter File Path</label>
            <input 
              type="text" 
              value={filePath}
              onChange={(e) => setFilePath(e.target.value)}
              disabled={loading}
              placeholder="/path/to/document.pdf"
              className="form-input"
            />
          </div>

          <div style={{ display: 'flex', gap: '1rem', marginTop: '1.5rem' }}>
            <button 
              type="submit" 
              className="btn btn-primary"
              disabled={loading}
            >
              {loading ? 'Processing...' : 'Process Document'}
            </button>
            <Link to="/standards" className="btn btn-secondary">
              Cancel
            </Link>
          </div>
        </form>

        {loading && renderProcessingStatus()}
      </div>

      <div className="card" style={{ marginTop: '1.5rem' }}>
        <h2 className="card-title" style={{ marginBottom: '1rem' }}>Available Documents</h2>
        <p style={{ marginBottom: '1rem' }}>
          The following AAOIFI standard documents are available in the Resources directory:
        </p>
        <ul style={{ paddingLeft: '1.5rem' }}>
          <li style={{ marginBottom: '0.5rem' }}>FAS 10 - Salam and Parallel Salam</li>
          <li style={{ marginBottom: '0.5rem' }}>FAS 28 - Murabaha and Other Deferred Payment Sales</li>
          <li style={{ marginBottom: '0.5rem' }}>FAS 32 - Ijarah and Ijarah Muntahia Bittamleek</li>
          <li style={{ marginBottom: '0.5rem' }}>SS 9 - Ijarah and Ijarah Muntahia Bittamleek</li>
          <li style={{ marginBottom: '0.5rem' }}>SS 10 - Salam and Parallel Salam</li>
        </ul>
      </div>
    </div>
  );
};

export default ProcessDocument;
