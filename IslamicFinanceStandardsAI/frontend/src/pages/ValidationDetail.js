import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';

const ValidationDetail = () => {
  const { id } = useParams();
  const [validation, setValidation] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // In a real implementation, this would fetch data from the API
    // For the hackathon demo, we'll use mock data
    setTimeout(() => {
      // Mock data for a validation
      const mockValidation = {
        id,
        proposal_id: '1',
        proposal_title: 'Definition Enhancement: Ijarah',
        standard_id: '2',
        standard_title: 'Ijarah and Ijarah Muntahia Bittamleek',
        standard_type: 'FAS',
        standard_number: '32',
        validation_date: '2025-05-07T14:45:00Z',
        overall_score: 0.92,
        status: 'APPROVED',
        feedback: 'The proposed enhancement to the definition of Ijarah significantly improves clarity and Shariah compliance. The addition of "Shariah-compliant" emphasizes the Islamic nature of the contract. Specifying that the asset must be "specified" aligns with the Shariah requirement that the subject matter of a contract must be known and determined. Clarifying that consideration is specifically "rental" distinguishes Ijarah from other contracts. The explicit mention that ownership and associated liabilities remain with the lessor is crucial for differentiating Ijarah from conventional leases and sales. The references provided are authoritative and relevant. Overall, this enhancement maintains the essence of the original definition while adding precision and Shariah alignment.',
        modified_content: '',
        scores: {
          'SHARIAH_COMPLIANCE': {
            score: 0.95,
            description: 'Compliance with Islamic principles and Shariah requirements',
            evaluation: 'The enhanced definition strongly aligns with Shariah principles by explicitly mentioning that the contract is Shariah-compliant and clarifying that ownership and associated liabilities remain with the lessor, which is a key Shariah requirement for Ijarah. The definition correctly emphasizes the transfer of usufruct rather than ownership, which is fundamental to the Shariah concept of Ijarah. The references to authoritative Shariah sources further strengthen its compliance.'
          },
          'TECHNICAL_ACCURACY': {
            score: 0.90,
            description: 'Accuracy of accounting treatments and financial concepts',
            evaluation: 'The enhanced definition accurately reflects the financial and accounting nature of Ijarah by specifying that the consideration is rental and that the asset must be specified. It correctly distinguishes between ownership and usufruct rights, which has important accounting implications. The definition aligns with the accounting treatment prescribed in FAS 32.'
          },
          'CLARITY_AND_PRECISION': {
            score: 0.94,
            description: 'Clarity, precision, and lack of ambiguity in language',
            evaluation: 'The enhanced definition is significantly clearer and more precise than the original. It eliminates potential ambiguities by specifying that the asset must be identified, clarifying that the consideration is specifically rental, and explicitly stating that ownership and its associated liabilities remain with the lessor. The language is concise yet comprehensive.'
          },
          'PRACTICAL_IMPLEMENTATION': {
            score: 0.88,
            description: 'Feasibility of implementation in real-world scenarios',
            evaluation: 'The enhanced definition provides clearer guidance for practical implementation by financial institutions. By specifying that the asset must be identified and that ownership liabilities remain with the lessor, it helps practitioners structure compliant Ijarah contracts. However, it could potentially provide more guidance on variable rental arrangements which are common in practice.'
          },
          'CONSISTENCY': {
            score: 0.90,
            description: 'Consistency with other standards and established practices',
            evaluation: 'The enhanced definition maintains consistency with other AAOIFI standards, particularly Shariah Standard No. 9 on Ijarah. It also aligns with established Islamic finance practices across the industry. The definition is compatible with international accounting standards while maintaining its Shariah-specific elements.'
          }
        },
        enhancement: {
          original_content: 'A lease contract whereby the lessor (owner) transfers the usufruct of an asset to another person (lessee) for an agreed period against an agreed consideration.',
          enhanced_content: 'A Shariah-compliant lease contract whereby the lessor (owner) transfers the usufruct (right to use) of a specified asset to another person (lessee) for an agreed period against an agreed consideration (rental), with the ownership of the asset remaining with the lessor along with all the liabilities arising from ownership.',
          reasoning: 'The enhanced definition provides greater clarity by explicitly mentioning that the contract is Shariah-compliant, specifying that the asset must be identified, clarifying that the consideration is specifically rental, and emphasizing that ownership and its associated liabilities remain with the lessor. These additions address potential ambiguities in the original definition and align more closely with Shariah requirements for valid Ijarah contracts.'
        }
      };

      setValidation(mockValidation);
      setLoading(false);
    }, 1000);
  }, [id]);

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

  if (loading) {
    return (
      <div className="card">
        <p>Loading validation details...</p>
      </div>
    );
  }

  if (!validation) {
    return (
      <div className="card">
        <p>Validation not found.</p>
        <Link to="/validations" className="btn btn-primary">Back to Validations</Link>
      </div>
    );
  }

  return (
    <div>
      <div className="card-header" style={{ marginBottom: '1.5rem' }}>
        <div>
          <h1 className="card-title">
            Validation: {validation.proposal_title}
          </h1>
          <div style={{ display: 'flex', gap: '0.5rem', marginTop: '0.5rem' }}>
            <span className="badge badge-primary">
              {validation.standard_type} {validation.standard_number}
            </span>
            <span className={getStatusBadgeClass(validation.status)}>
              {validation.status.replace(/_/g, ' ')}
            </span>
          </div>
        </div>
        <div>
          <Link to={`/enhancements/${validation.proposal_id}`} className="btn btn-secondary" style={{ marginRight: '0.5rem' }}>
            View Enhancement
          </Link>
          <Link to={`/standards/${validation.standard_id}`} className="btn btn-secondary">
            View Standard
          </Link>
        </div>
      </div>

      <div className="card">
        <h2 className="card-title" style={{ marginBottom: '1rem' }}>Validation Summary</h2>
        <p style={{ marginBottom: '1rem' }}>
          <strong>Standard:</strong> <Link to={`/standards/${validation.standard_id}`} style={{ color: 'var(--primary)' }}>
            {validation.standard_title}
          </Link>
        </p>
        <p style={{ marginBottom: '1rem' }}>
          <strong>Validated on:</strong> {new Date(validation.validation_date).toLocaleString()}
        </p>

        <div style={{ 
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          padding: '1rem',
          backgroundColor: 'var(--background)',
          borderRadius: '0.375rem',
          marginBottom: '1.5rem'
        }}>
          <div>
            <strong>Overall Score:</strong>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
            <div style={{ 
              width: '200px', 
              height: '10px', 
              backgroundColor: 'var(--border)',
              borderRadius: '5px'
            }}>
              <div style={{ 
                width: `${validation.overall_score * 100}%`, 
                height: '100%', 
                backgroundColor: getScoreColor(validation.overall_score),
                borderRadius: '5px'
              }}></div>
            </div>
            <div style={{ 
              fontWeight: 'bold',
              fontSize: '1.25rem',
              color: getScoreColor(validation.overall_score)
            }}>
              {(validation.overall_score * 100).toFixed(0)}%
            </div>
          </div>
        </div>

        <h3 style={{ marginBottom: '1rem', fontWeight: '600' }}>Validation Criteria Scores</h3>
        <div style={{ marginBottom: '1.5rem' }}>
          {Object.entries(validation.scores).map(([criterion, details]) => (
            <div key={criterion} style={{ 
              marginBottom: '1rem',
              padding: '1rem',
              backgroundColor: 'var(--background)',
              borderRadius: '0.375rem',
              border: '1px solid var(--border)'
            }}>
              <div style={{ 
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
                marginBottom: '0.5rem'
              }}>
                <h4 style={{ fontWeight: '600' }}>{criterion.replace(/_/g, ' ')}</h4>
                <div style={{ 
                  fontWeight: 'bold',
                  color: getScoreColor(details.score)
                }}>
                  {(details.score * 100).toFixed(0)}%
                </div>
              </div>
              <p style={{ fontSize: '0.875rem', color: 'var(--text-secondary)', marginBottom: '0.5rem' }}>
                {details.description}
              </p>
              <div style={{ 
                width: '100%', 
                height: '6px', 
                backgroundColor: 'var(--border)',
                borderRadius: '3px',
                marginBottom: '0.75rem'
              }}>
                <div style={{ 
                  width: `${details.score * 100}%`, 
                  height: '100%', 
                  backgroundColor: getScoreColor(details.score),
                  borderRadius: '3px'
                }}></div>
              </div>
              <p>{details.evaluation}</p>
            </div>
          ))}
        </div>

        <h3 style={{ marginBottom: '1rem', fontWeight: '600' }}>Validation Feedback</h3>
        <div style={{ 
          padding: '1rem',
          backgroundColor: 'var(--background)',
          borderRadius: '0.375rem',
          border: '1px solid var(--border)',
          marginBottom: '1.5rem'
        }}>
          <p>{validation.feedback}</p>
        </div>

        {validation.status === 'APPROVED_WITH_MODIFICATIONS' && validation.modified_content && (
          <div>
            <h3 style={{ marginBottom: '1rem', fontWeight: '600' }}>Modified Content</h3>
            <div style={{ 
              padding: '1rem',
              backgroundColor: 'rgba(16, 185, 129, 0.1)',
              borderRadius: '0.375rem',
              border: '1px solid var(--primary)',
              marginBottom: '1.5rem'
            }}>
              <p>{validation.modified_content}</p>
            </div>
          </div>
        )}
      </div>

      <div className="card" style={{ marginTop: '1.5rem' }}>
        <h2 className="card-title" style={{ marginBottom: '1rem' }}>Enhancement Details</h2>
        
        <div style={{ 
          backgroundColor: 'var(--background)', 
          padding: '1rem', 
          borderRadius: '0.375rem',
          border: '1px solid var(--border)',
          marginBottom: '1rem'
        }}>
          <h3 style={{ marginBottom: '0.5rem', fontWeight: '600' }}>Original Content</h3>
          <p>{validation.enhancement.original_content}</p>
        </div>
        
        <div style={{ 
          backgroundColor: validation.status === 'APPROVED' ? 'rgba(16, 185, 129, 0.1)' : 
                          validation.status === 'APPROVED_WITH_MODIFICATIONS' ? 'rgba(245, 158, 11, 0.1)' :
                          'rgba(239, 68, 68, 0.1)', 
          padding: '1rem', 
          borderRadius: '0.375rem',
          border: `1px solid ${validation.status === 'APPROVED' ? 'var(--success)' : 
                              validation.status === 'APPROVED_WITH_MODIFICATIONS' ? 'var(--warning)' :
                              'var(--error)'}`,
          marginBottom: '1rem'
        }}>
          <h3 style={{ marginBottom: '0.5rem', fontWeight: '600' }}>Enhanced Content</h3>
          <p>{validation.enhancement.enhanced_content}</p>
        </div>
        
        <h3 style={{ marginBottom: '0.5rem', fontWeight: '600' }}>Enhancement Reasoning</h3>
        <p>{validation.enhancement.reasoning}</p>
        
        <div style={{ marginTop: '1.5rem' }}>
          <Link to={`/enhancements/${validation.proposal_id}`} className="btn btn-primary">
            View Full Enhancement
          </Link>
        </div>
      </div>
    </div>
  );
};

export default ValidationDetail;
