import React, { useState, useEffect } from 'react';
import { Link, useLocation } from 'react-router-dom';

const Validations = () => {
  const [validations, setValidations] = useState([]);
  const [loading, setLoading] = useState(true);
  const location = useLocation();
  const queryParams = new URLSearchParams(location.search);
  const proposalId = queryParams.get('proposal_id');
  const statusFilter = queryParams.get('status');

  useEffect(() => {
    // In a real implementation, this would fetch data from the API
    // For the hackathon demo, we'll use mock data
    setTimeout(() => {
      const mockValidations = [
        {
          id: 'v1',
          proposal_id: '1',
          proposal_title: 'Definition Enhancement: Ijarah',
          standard_id: '2',
          standard_title: 'Ijarah and Ijarah Muntahia Bittamleek',
          standard_type: 'FAS',
          standard_number: '32',
          validation_date: '2025-05-07T14:45:00Z',
          overall_score: 0.92,
          status: 'APPROVED'
        },
        {
          id: 'v2',
          proposal_id: '2',
          proposal_title: 'Accounting Treatment: Recognition and Measurement of Ijarah',
          standard_id: '2',
          standard_title: 'Ijarah and Ijarah Muntahia Bittamleek',
          standard_type: 'FAS',
          standard_number: '32',
          validation_date: '2025-05-07T16:20:00Z',
          overall_score: 0.78,
          status: 'APPROVED_WITH_MODIFICATIONS'
        },
        {
          id: 'v3',
          proposal_id: '4',
          proposal_title: 'Transaction Structure: Basic Salam Structure',
          standard_id: '1',
          standard_title: 'Salam and Parallel Salam',
          standard_type: 'FAS',
          standard_number: '10',
          validation_date: '2025-05-06T15:10:00Z',
          overall_score: 0.88,
          status: 'APPROVED'
        },
        {
          id: 'v4',
          proposal_id: '5',
          proposal_title: 'Definition Enhancement: Murabaha',
          standard_id: '3',
          standard_title: 'Murabaha and Other Deferred Payment Sales',
          standard_type: 'FAS',
          standard_number: '28',
          validation_date: '2025-05-05T17:30:00Z',
          overall_score: 0.85,
          status: 'APPROVED'
        },
        {
          id: 'v5',
          proposal_id: '6',
          proposal_title: 'New Guidance: Digital Murabaha Transactions',
          standard_id: '3',
          standard_title: 'Murabaha and Other Deferred Payment Sales',
          standard_type: 'FAS',
          standard_number: '28',
          validation_date: '2025-05-06T12:45:00Z',
          overall_score: 0.52,
          status: 'REJECTED'
        }
      ];

      // Apply filters if present
      let filteredValidations = mockValidations;
      
      if (proposalId) {
        filteredValidations = filteredValidations.filter(v => v.proposal_id === proposalId);
      }
      
      if (statusFilter) {
        filteredValidations = filteredValidations.filter(v => v.status === statusFilter);
      }

      setValidations(filteredValidations);
      setLoading(false);
    }, 1000);
  }, [proposalId, statusFilter]);

  const getStatusBadgeClass = (status) => {
    switch (status) {
      case 'APPROVED':
        return 'badge badge-success';
      case 'APPROVED_WITH_MODIFICATIONS':
        return 'badge badge-warning';
      case 'REJECTED':
        return 'badge badge-error';
      default:
        return 'badge badge-secondary';
    }
  };

  const getScoreColor = (score) => {
    if (score >= 0.8) return 'var(--success)';
    if (score >= 0.6) return 'var(--warning)';
    return 'var(--error)';
  };

  return (
    <div>
      <div className="card-header" style={{ marginBottom: '1.5rem' }}>
        <h1 className="card-title">
          {proposalId 
            ? `Validations for Enhancement #${proposalId}`
            : statusFilter 
              ? `${statusFilter.replace('_', ' ')} Validations` 
              : 'All Validations'
          }
        </h1>
        {proposalId && (
          <Link to={`/enhancements/${proposalId}`} className="btn btn-secondary">
            Back to Enhancement
          </Link>
        )}
      </div>
      
      {loading ? (
        <div className="card">
          <p>Loading validations...</p>
        </div>
      ) : (
        <div>
          {validations.length === 0 ? (
            <div className="card">
              <p>No validations found matching the current filters.</p>
            </div>
          ) : (
            validations.map((validation) => (
              <div className="card" key={validation.id}>
                <div className="card-header">
                  <div>
                    <h2 className="card-title">
                      {validation.proposal_title}
                    </h2>
                    <div style={{ display: 'flex', gap: '0.5rem', marginTop: '0.5rem' }}>
                      <span className="badge badge-primary">
                        {validation.standard_type} {validation.standard_number}
                      </span>
                      <span className={getStatusBadgeClass(validation.status)}>
                        {validation.status.replace(/_/g, ' ')}
                      </span>
                    </div>
                  </div>
                  <Link to={`/validations/${validation.id}`} className="btn btn-primary">
                    View Details
                  </Link>
                </div>
                
                <p style={{ marginBottom: '1rem' }}>
                  Standard: <Link to={`/standards/${validation.standard_id}`} style={{ color: 'var(--primary)' }}>
                    {validation.standard_title}
                  </Link>
                </p>
                
                <div style={{ 
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                  padding: '0.75rem',
                  backgroundColor: 'var(--background)',
                  borderRadius: '0.375rem',
                  marginBottom: '1rem'
                }}>
                  <div>
                    <strong>Overall Score:</strong>
                  </div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                    <div style={{ 
                      width: '150px', 
                      height: '8px', 
                      backgroundColor: 'var(--border)',
                      borderRadius: '4px'
                    }}>
                      <div style={{ 
                        width: `${validation.overall_score * 100}%`, 
                        height: '100%', 
                        backgroundColor: getScoreColor(validation.overall_score),
                        borderRadius: '4px'
                      }}></div>
                    </div>
                    <div style={{ 
                      fontWeight: 'bold',
                      color: getScoreColor(validation.overall_score)
                    }}>
                      {(validation.overall_score * 100).toFixed(0)}%
                    </div>
                  </div>
                </div>
                
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <span style={{ color: 'var(--text-secondary)', fontSize: '0.875rem' }}>
                    Validated on: {new Date(validation.validation_date).toLocaleString()}
                  </span>
                  <Link to={`/enhancements/${validation.proposal_id}`} className="btn btn-secondary">
                    View Enhancement
                  </Link>
                </div>
              </div>
            ))
          )}
        </div>
      )}
    </div>
  );
};

export default Validations;
