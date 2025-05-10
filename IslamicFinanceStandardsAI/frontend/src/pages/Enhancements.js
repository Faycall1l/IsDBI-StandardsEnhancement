import React, { useState, useEffect } from 'react';
import { Link, useLocation } from 'react-router-dom';

const Enhancements = () => {
  const [enhancements, setEnhancements] = useState([]);
  const [loading, setLoading] = useState(true);
  const location = useLocation();
  const queryParams = new URLSearchParams(location.search);
  const standardId = queryParams.get('standard_id');
  const statusFilter = queryParams.get('status');

  useEffect(() => {
    // In a real implementation, this would fetch data from the API
    // For the hackathon demo, we'll use mock data
    setTimeout(() => {
      const mockEnhancements = [
        {
          id: '1',
          standard_id: '2',
          standard_title: 'Ijarah and Ijarah Muntahia Bittamleek',
          standard_type: 'FAS',
          standard_number: '32',
          enhancement_type: 'DEFINITION',
          target_id: 'd1',
          target_name: 'Ijarah',
          status: 'APPROVED',
          created_at: '2025-05-07T10:30:00Z'
        },
        {
          id: '2',
          standard_id: '2',
          standard_title: 'Ijarah and Ijarah Muntahia Bittamleek',
          standard_type: 'FAS',
          standard_number: '32',
          enhancement_type: 'ACCOUNTING_TREATMENT',
          target_id: 'at1',
          target_name: 'Recognition and Measurement of Ijarah',
          status: 'APPROVED_WITH_MODIFICATIONS',
          created_at: '2025-05-07T11:45:00Z'
        },
        {
          id: '3',
          standard_id: '2',
          standard_title: 'Ijarah and Ijarah Muntahia Bittamleek',
          standard_type: 'FAS',
          standard_number: '32',
          enhancement_type: 'AMBIGUITY_RESOLUTION',
          target_id: 'amb1',
          target_name: 'Variable lease payments',
          status: 'UNDER_REVIEW',
          created_at: '2025-05-08T09:15:00Z'
        },
        {
          id: '4',
          standard_id: '1',
          standard_title: 'Salam and Parallel Salam',
          standard_type: 'FAS',
          standard_number: '10',
          enhancement_type: 'TRANSACTION_STRUCTURE',
          target_id: 'ts1',
          target_name: 'Basic Salam Structure',
          status: 'APPROVED',
          created_at: '2025-05-06T14:20:00Z'
        },
        {
          id: '5',
          standard_id: '3',
          standard_title: 'Murabaha and Other Deferred Payment Sales',
          standard_type: 'FAS',
          standard_number: '28',
          enhancement_type: 'DEFINITION',
          target_id: 'd2',
          target_name: 'Murabaha',
          status: 'APPROVED',
          created_at: '2025-05-05T16:10:00Z'
        },
        {
          id: '6',
          standard_id: '3',
          standard_title: 'Murabaha and Other Deferred Payment Sales',
          standard_type: 'FAS',
          standard_number: '28',
          enhancement_type: 'NEW_GUIDANCE',
          target_id: 'ng1',
          target_name: 'Digital Murabaha Transactions',
          status: 'REJECTED',
          created_at: '2025-05-06T11:30:00Z'
        }
      ];

      // Apply filters if present
      let filteredEnhancements = mockEnhancements;
      
      if (standardId) {
        filteredEnhancements = filteredEnhancements.filter(e => e.standard_id === standardId);
      }
      
      if (statusFilter) {
        filteredEnhancements = filteredEnhancements.filter(e => e.status === statusFilter);
      }

      setEnhancements(filteredEnhancements);
      setLoading(false);
    }, 1000);
  }, [standardId, statusFilter]);

  const getEnhancementTypeLabel = (type) => {
    switch (type) {
      case 'DEFINITION':
        return 'Definition Enhancement';
      case 'ACCOUNTING_TREATMENT':
        return 'Accounting Treatment';
      case 'TRANSACTION_STRUCTURE':
        return 'Transaction Structure';
      case 'AMBIGUITY_RESOLUTION':
        return 'Ambiguity Resolution';
      case 'NEW_GUIDANCE':
        return 'New Guidance';
      default:
        return type;
    }
  };

  const getStatusBadgeClass = (status) => {
    switch (status) {
      case 'APPROVED':
        return 'badge badge-success';
      case 'APPROVED_WITH_MODIFICATIONS':
        return 'badge badge-warning';
      case 'UNDER_REVIEW':
        return 'badge badge-secondary';
      case 'REJECTED':
        return 'badge badge-error';
      default:
        return 'badge badge-secondary';
    }
  };

  return (
    <div>
      <div className="card-header" style={{ marginBottom: '1.5rem' }}>
        <h1 className="card-title">
          {standardId 
            ? `Enhancements for ${enhancements.length > 0 ? `${enhancements[0].standard_type} ${enhancements[0].standard_number}` : 'Standard'}`
            : statusFilter 
              ? `${statusFilter.replace('_', ' ')} Enhancements` 
              : 'All Enhancements'
          }
        </h1>
        {standardId && (
          <Link to={`/standards/${standardId}`} className="btn btn-secondary">
            Back to Standard
          </Link>
        )}
      </div>
      
      {loading ? (
        <div className="card">
          <p>Loading enhancements...</p>
        </div>
      ) : (
        <div>
          {enhancements.length === 0 ? (
            <div className="card">
              <p>No enhancements found matching the current filters.</p>
            </div>
          ) : (
            enhancements.map((enhancement) => (
              <div className="card" key={enhancement.id}>
                <div className="card-header">
                  <div>
                    <h2 className="card-title">
                      {getEnhancementTypeLabel(enhancement.enhancement_type)}: {enhancement.target_name}
                    </h2>
                    <div style={{ display: 'flex', gap: '0.5rem', marginTop: '0.5rem' }}>
                      <span className="badge badge-primary">
                        {enhancement.standard_type} {enhancement.standard_number}
                      </span>
                      <span className={getStatusBadgeClass(enhancement.status)}>
                        {enhancement.status.replace(/_/g, ' ')}
                      </span>
                    </div>
                  </div>
                  <Link to={`/enhancements/${enhancement.id}`} className="btn btn-primary">
                    View Details
                  </Link>
                </div>
                <p style={{ marginBottom: '1rem' }}>
                  Standard: <Link to={`/standards/${enhancement.standard_id}`} style={{ color: 'var(--primary)' }}>
                    {enhancement.standard_title}
                  </Link>
                </p>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <span style={{ color: 'var(--text-secondary)', fontSize: '0.875rem' }}>
                    Created: {new Date(enhancement.created_at).toLocaleString()}
                  </span>
                  {enhancement.status === 'PROPOSED' || enhancement.status === 'UNDER_REVIEW' ? (
                    <Link to={`/validations/new?proposal_id=${enhancement.id}`} className="btn btn-secondary">
                      Validate
                    </Link>
                  ) : (
                    <Link to={`/validations?proposal_id=${enhancement.id}`} className="btn btn-secondary">
                      View Validation
                    </Link>
                  )}
                </div>
              </div>
            ))
          )}
        </div>
      )}
    </div>
  );
};

export default Enhancements;
