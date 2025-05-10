import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';

const EnhancementDetail = () => {
  const { id } = useParams();
  const [enhancement, setEnhancement] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // In a real implementation, this would fetch data from the API
    // For the hackathon demo, we'll use mock data
    setTimeout(() => {
      // Mock data for an enhancement
      const mockEnhancement = {
        id,
        standard_id: '2',
        standard_title: 'Ijarah and Ijarah Muntahia Bittamleek',
        standard_type: 'FAS',
        standard_number: '32',
        enhancement_type: 'DEFINITION',
        target_id: 'd1',
        target_name: 'Ijarah',
        status: 'APPROVED',
        created_at: '2025-05-07T10:30:00Z',
        original_content: 'A lease contract whereby the lessor (owner) transfers the usufruct of an asset to another person (lessee) for an agreed period against an agreed consideration.',
        enhanced_content: 'A Shariah-compliant lease contract whereby the lessor (owner) transfers the usufruct (right to use) of a specified asset to another person (lessee) for an agreed period against an agreed consideration (rental), with the ownership of the asset remaining with the lessor along with all the liabilities arising from ownership.',
        reasoning: 'The enhanced definition provides greater clarity by explicitly mentioning that the contract is Shariah-compliant, specifying that the asset must be identified, clarifying that the consideration is specifically rental, and emphasizing that ownership and its associated liabilities remain with the lessor. These additions address potential ambiguities in the original definition and align more closely with Shariah requirements for valid Ijarah contracts.',
        references: 'AAOIFI Shariah Standard No. 9 on Ijarah and Ijarah Muntahia Bittamleek\nIslamic Fiqh Academy Resolution No. 110 (4/12)\nIbn Qudamah, Al-Mughni, Vol. 8, p. 146\nAl-Zuhayli, Islamic Jurisprudence and Its Proofs, Vol. 4, pp. 384-385',
        validations: [
          {
            id: 'v1',
            validation_date: '2025-05-07T14:45:00Z',
            overall_score: 0.92,
            status: 'APPROVED',
            feedback: 'The proposed enhancement to the definition of Ijarah significantly improves clarity and Shariah compliance. The addition of "Shariah-compliant" emphasizes the Islamic nature of the contract. Specifying that the asset must be "specified" aligns with the Shariah requirement that the subject matter of a contract must be known and determined. Clarifying that consideration is specifically "rental" distinguishes Ijarah from other contracts. The explicit mention that ownership and associated liabilities remain with the lessor is crucial for differentiating Ijarah from conventional leases and sales. The references provided are authoritative and relevant. Overall, this enhancement maintains the essence of the original definition while adding precision and Shariah alignment.',
            scores: {
              'SHARIAH_COMPLIANCE': 0.95,
              'TECHNICAL_ACCURACY': 0.90,
              'CLARITY_AND_PRECISION': 0.94,
              'PRACTICAL_IMPLEMENTATION': 0.88,
              'CONSISTENCY': 0.90
            }
          }
        ]
      };

      setEnhancement(mockEnhancement);
      setLoading(false);
    }, 1000);
  }, [id]);

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

  const getCriterionLabel = (criterion) => {
    switch (criterion) {
      case 'SHARIAH_COMPLIANCE':
        return 'Shariah Compliance';
      case 'TECHNICAL_ACCURACY':
        return 'Technical Accuracy';
      case 'CLARITY_AND_PRECISION':
        return 'Clarity & Precision';
      case 'PRACTICAL_IMPLEMENTATION':
        return 'Practical Implementation';
      case 'CONSISTENCY':
        return 'Consistency';
      default:
        return criterion;
    }
  };

  if (loading) {
    return (
      <div className="card">
        <p>Loading enhancement details...</p>
      </div>
    );
  }

  if (!enhancement) {
    return (
      <div className="card">
        <p>Enhancement not found.</p>
        <Link to="/enhancements" className="btn btn-primary">Back to Enhancements</Link>
      </div>
    );
  }

  return (
    <div>
      <div className="card-header" style={{ marginBottom: '1.5rem' }}>
        <div>
          <h1 className="card-title">
            {getEnhancementTypeLabel(enhancement.enhancement_type)}: {enhancement.target_name}
          </h1>
          <div style={{ display: 'flex', gap: '0.5rem', marginTop: '0.5rem' }}>
            <span className="badge badge-primary">
              {enhancement.standard_type} {enhancement.standard_number}
            </span>
            <span className={getStatusBadgeClass(enhancement.status)}>
              {enhancement.status.replace(/_/g, ' ')}
            </span>
          </div>
        </div>
        <div>
          <Link to={`/standards/${enhancement.standard_id}`} className="btn btn-secondary" style={{ marginRight: '0.5rem' }}>
            View Standard
          </Link>
          {enhancement.status === 'PROPOSED' || enhancement.status === 'UNDER_REVIEW' ? (
            <Link to={`/validations/new?proposal_id=${enhancement.id}`} className="btn btn-primary">
              Validate
            </Link>
          ) : null}
        </div>
      </div>

      <div className="card">
        <h2 className="card-title" style={{ marginBottom: '1rem' }}>Enhancement Details</h2>
        <p style={{ marginBottom: '1rem' }}>
          <strong>Standard:</strong> <Link to={`/standards/${enhancement.standard_id}`} style={{ color: 'var(--primary)' }}>
            {enhancement.standard_title}
          </Link>
        </p>
        <p style={{ marginBottom: '1rem' }}>
          <strong>Created:</strong> {new Date(enhancement.created_at).toLocaleString()}
        </p>

        <div style={{ 
          backgroundColor: 'var(--background)', 
          padding: '1.5rem', 
          borderRadius: '0.375rem',
          border: '1px solid var(--border)',
          marginBottom: '1.5rem'
        }}>
          <h3 style={{ marginBottom: '1rem', fontWeight: '600' }}>Original Content</h3>
          <p style={{ 
            fontStyle: 'italic',
            padding: '1rem',
            backgroundColor: 'white',
            borderRadius: '0.375rem',
            border: '1px solid var(--border)'
          }}>{enhancement.original_content}</p>
        </div>

        <div style={{ 
          backgroundColor: 'rgba(16, 185, 129, 0.1)', 
          padding: '1.5rem', 
          borderRadius: '0.375rem',
          border: '1px solid var(--primary)',
          marginBottom: '1.5rem'
        }}>
          <h3 style={{ marginBottom: '1rem', fontWeight: '600', color: 'var(--primary)' }}>Enhanced Content</h3>
          <p style={{ 
            padding: '1rem',
            backgroundColor: 'white',
            borderRadius: '0.375rem',
            border: '1px solid var(--border)'
          }}>{enhancement.enhanced_content}</p>
        </div>

        <h3 style={{ marginBottom: '1rem', fontWeight: '600' }}>Reasoning</h3>
        <p style={{ marginBottom: '1.5rem' }}>{enhancement.reasoning}</p>

        <h3 style={{ marginBottom: '1rem', fontWeight: '600' }}>References</h3>
        <div style={{ 
          padding: '1rem',
          backgroundColor: 'var(--background)',
          borderRadius: '0.375rem',
          border: '1px solid var(--border)',
          marginBottom: '1.5rem'
        }}>
          {enhancement.references.split('\n').map((ref, index) => (
            <p key={index} style={{ marginBottom: index < enhancement.references.split('\n').length - 1 ? '0.5rem' : 0 }}>
              {ref}
            </p>
          ))}
        </div>
      </div>

      {enhancement.validations && enhancement.validations.length > 0 && (
        <div className="card" style={{ marginTop: '1.5rem' }}>
          <h2 className="card-title" style={{ marginBottom: '1rem' }}>Validation Results</h2>
          
          {enhancement.validations.map((validation, index) => (
            <div key={index} style={{ marginBottom: index < enhancement.validations.length - 1 ? '2rem' : 0 }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
                <div>
                  <span className={getStatusBadgeClass(validation.status)} style={{ marginRight: '0.5rem' }}>
                    {validation.status.replace(/_/g, ' ')}
                  </span>
                  <span style={{ color: 'var(--text-secondary)', fontSize: '0.875rem' }}>
                    Validated on {new Date(validation.validation_date).toLocaleString()}
                  </span>
                </div>
                <div style={{ 
                  fontWeight: 'bold', 
                  color: validation.overall_score >= 0.8 ? 'var(--success)' : 
                         validation.overall_score >= 0.6 ? 'var(--warning)' : 'var(--error)'
                }}>
                  Score: {(validation.overall_score * 100).toFixed(0)}%
                </div>
              </div>

              <div style={{ marginBottom: '1.5rem' }}>
                <h3 style={{ marginBottom: '0.5rem', fontWeight: '600' }}>Validation Criteria Scores</h3>
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem' }}>
                  {Object.entries(validation.scores).map(([criterion, score]) => (
                    <div key={criterion} style={{ 
                      padding: '0.5rem',
                      backgroundColor: 'var(--background)',
                      borderRadius: '0.375rem',
                      border: '1px solid var(--border)',
                      minWidth: '150px'
                    }}>
                      <div style={{ fontSize: '0.875rem', marginBottom: '0.25rem' }}>{getCriterionLabel(criterion)}</div>
                      <div style={{ 
                        display: 'flex', 
                        alignItems: 'center',
                        justifyContent: 'space-between'
                      }}>
                        <div style={{ 
                          width: '70%', 
                          height: '8px', 
                          backgroundColor: 'var(--border)',
                          borderRadius: '4px'
                        }}>
                          <div style={{ 
                            width: `${score * 100}%`, 
                            height: '100%', 
                            backgroundColor: score >= 0.8 ? 'var(--success)' : 
                                            score >= 0.6 ? 'var(--warning)' : 'var(--error)',
                            borderRadius: '4px'
                          }}></div>
                        </div>
                        <div style={{ 
                          fontWeight: '500',
                          color: score >= 0.8 ? 'var(--success)' : 
                                 score >= 0.6 ? 'var(--warning)' : 'var(--error)'
                        }}>
                          {(score * 100).toFixed(0)}%
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              <h3 style={{ marginBottom: '0.5rem', fontWeight: '600' }}>Feedback</h3>
              <p>{validation.feedback}</p>

              <div style={{ marginTop: '1rem' }}>
                <Link to={`/validations/${validation.id}`} className="btn btn-secondary">
                  View Full Validation
                </Link>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default EnhancementDetail;
