import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';

const StandardDetail = () => {
  const { id } = useParams();
  const [standard, setStandard] = useState(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('definitions');

  useEffect(() => {
    // In a real implementation, this would fetch data from the API
    // For the hackathon demo, we'll use mock data
    setTimeout(() => {
      // Mock data for a standard
      const mockStandard = {
        id,
        title: 'Ijarah and Ijarah Muntahia Bittamleek',
        standard_type: 'FAS',
        standard_number: '32',
        publication_date: '2021-03-15',
        description: 'This standard sets out the principles for the classification, recognition, measurement, presentation and disclosure of Ijarah (asset leasing) transactions including different forms of Ijarah Muntahia Bittamleek.',
        definitions: [
          {
            term: 'Ijarah',
            definition: 'A lease contract whereby the lessor (owner) transfers the usufruct of an asset to another person (lessee) for an agreed period against an agreed consideration.'
          },
          {
            term: 'Ijarah Muntahia Bittamleek',
            definition: 'A form of leasing contract which includes a promise by the lessor to transfer the ownership of the leased asset to the lessee at the end of the lease period or during it, by means of gift or sale.'
          },
          {
            term: 'Usufruct',
            definition: 'The right to use and derive profit from a property belonging to another, provided the property itself remains undiminished and uninjured in any way.'
          }
        ],
        accounting_treatments: [
          {
            title: 'Recognition and Measurement of Ijarah',
            description: 'Ijarah assets shall be recognized at the time when the asset is made available for use by the lessee. Ijarah assets shall be measured at cost less accumulated depreciation and impairment losses. The cost of Ijarah assets shall include the acquisition cost and initial direct costs.'
          },
          {
            title: 'Ijarah Revenue Recognition',
            description: 'Ijarah revenue shall be allocated proportionately to the financial periods over the lease term. Ijarah revenue shall be presented as a separate line item in the statement of income.'
          }
        ],
        transaction_structures: [
          {
            title: 'Basic Ijarah Structure',
            description: 'The basic structure of an Ijarah transaction involves the following parties: lessor, lessee, and supplier.',
            steps: [
              '1. The customer identifies an asset and approaches the Islamic bank',
              '2. The bank purchases the asset from the supplier',
              '3. The bank leases the asset to the customer for an agreed period',
              '4. The customer pays periodic rental payments to the bank',
              '5. At the end of the lease term, the asset is returned to the bank unless there is a separate agreement for transfer of ownership'
            ]
          },
          {
            title: 'Ijarah Muntahia Bittamleek Structure',
            description: 'This structure includes a promise to transfer ownership at the end of the lease term.',
            steps: [
              '1. The customer identifies an asset and approaches the Islamic bank',
              '2. The bank purchases the asset from the supplier',
              '3. The bank leases the asset to the customer for an agreed period with a promise to transfer ownership',
              '4. The customer pays periodic rental payments to the bank',
              '5. At the end of the lease term, ownership is transferred to the customer through one of the following methods: gift, sale at a nominal price, gradual transfer, or sale prior to the end of the lease term'
            ]
          }
        ],
        ambiguities: [
          {
            text: 'The standard may not clearly address the treatment of variable lease payments that depend on an index or rate.',
            context: 'In some cases, Ijarah contracts may include variable payments that depend on an index or rate, such as inflation adjustments. The current standard does not provide specific guidance on how to account for these variable payments.',
            indicator: 'not specified'
          },
          {
            text: 'The treatment of modifications to Ijarah contracts is ambiguous.',
            context: 'When the terms of an Ijarah contract are modified, it is not clear whether this should be treated as a new contract or a continuation of the existing contract with adjustments.',
            indicator: 'ambiguous'
          }
        ]
      };

      setStandard(mockStandard);
      setLoading(false);
    }, 1000);
  }, [id]);

  if (loading) {
    return (
      <div className="card">
        <p>Loading standard details...</p>
      </div>
    );
  }

  if (!standard) {
    return (
      <div className="card">
        <p>Standard not found.</p>
        <Link to="/standards" className="btn btn-primary">Back to Standards</Link>
      </div>
    );
  }

  return (
    <div>
      <div className="card-header" style={{ marginBottom: '1.5rem' }}>
        <div>
          <h1 className="card-title">{standard.title}</h1>
          <div style={{ display: 'flex', gap: '0.5rem', marginTop: '0.5rem' }}>
            <span className="badge badge-primary">
              {standard.standard_type} {standard.standard_number}
            </span>
            <span className="badge badge-secondary">
              Published: {new Date(standard.publication_date).toLocaleDateString()}
            </span>
          </div>
        </div>
        <div>
          <Link to={`/enhancements?standard_id=${standard.id}`} className="btn btn-secondary" style={{ marginRight: '0.5rem' }}>
            View Enhancements
          </Link>
          <button className="btn btn-primary">
            Generate Enhancements
          </button>
        </div>
      </div>

      <div className="card">
        <p style={{ marginBottom: '1.5rem' }}>{standard.description}</p>
        
        <div style={{ 
          display: 'flex', 
          borderBottom: '1px solid var(--border)', 
          marginBottom: '1.5rem' 
        }}>
          <button 
            className={`btn ${activeTab === 'definitions' ? 'btn-primary' : 'btn-secondary'}`}
            onClick={() => setActiveTab('definitions')}
            style={{ 
              borderRadius: '0.375rem 0.375rem 0 0',
              marginRight: '0.25rem',
              borderBottom: activeTab === 'definitions' ? '3px solid var(--primary)' : 'none'
            }}
          >
            Definitions
          </button>
          <button 
            className={`btn ${activeTab === 'accounting' ? 'btn-primary' : 'btn-secondary'}`}
            onClick={() => setActiveTab('accounting')}
            style={{ 
              borderRadius: '0.375rem 0.375rem 0 0',
              marginRight: '0.25rem',
              borderBottom: activeTab === 'accounting' ? '3px solid var(--primary)' : 'none'
            }}
          >
            Accounting Treatments
          </button>
          <button 
            className={`btn ${activeTab === 'structures' ? 'btn-primary' : 'btn-secondary'}`}
            onClick={() => setActiveTab('structures')}
            style={{ 
              borderRadius: '0.375rem 0.375rem 0 0',
              marginRight: '0.25rem',
              borderBottom: activeTab === 'structures' ? '3px solid var(--primary)' : 'none'
            }}
          >
            Transaction Structures
          </button>
          <button 
            className={`btn ${activeTab === 'ambiguities' ? 'btn-primary' : 'btn-secondary'}`}
            onClick={() => setActiveTab('ambiguities')}
            style={{ 
              borderRadius: '0.375rem 0.375rem 0 0',
              borderBottom: activeTab === 'ambiguities' ? '3px solid var(--primary)' : 'none'
            }}
          >
            Ambiguities
          </button>
        </div>

        {activeTab === 'definitions' && (
          <div>
            <h2 className="card-title" style={{ marginBottom: '1rem' }}>Key Definitions</h2>
            {standard.definitions.map((def, index) => (
              <div key={index} style={{ marginBottom: '1.5rem' }}>
                <h3 style={{ fontWeight: '600', marginBottom: '0.5rem' }}>{def.term}</h3>
                <p>{def.definition}</p>
              </div>
            ))}
          </div>
        )}

        {activeTab === 'accounting' && (
          <div>
            <h2 className="card-title" style={{ marginBottom: '1rem' }}>Accounting Treatments</h2>
            {standard.accounting_treatments.map((treatment, index) => (
              <div key={index} style={{ marginBottom: '1.5rem' }}>
                <h3 style={{ fontWeight: '600', marginBottom: '0.5rem' }}>{treatment.title}</h3>
                <p>{treatment.description}</p>
              </div>
            ))}
          </div>
        )}

        {activeTab === 'structures' && (
          <div>
            <h2 className="card-title" style={{ marginBottom: '1rem' }}>Transaction Structures</h2>
            {standard.transaction_structures.map((structure, index) => (
              <div key={index} style={{ marginBottom: '2rem' }}>
                <h3 style={{ fontWeight: '600', marginBottom: '0.5rem' }}>{structure.title}</h3>
                <p style={{ marginBottom: '1rem' }}>{structure.description}</p>
                <div style={{ 
                  backgroundColor: 'var(--background)', 
                  padding: '1rem', 
                  borderRadius: '0.375rem',
                  border: '1px solid var(--border)'
                }}>
                  <h4 style={{ marginBottom: '0.5rem', fontWeight: '500' }}>Steps:</h4>
                  <ul style={{ paddingLeft: '1.5rem' }}>
                    {structure.steps.map((step, stepIndex) => (
                      <li key={stepIndex} style={{ marginBottom: '0.5rem' }}>{step}</li>
                    ))}
                  </ul>
                </div>
              </div>
            ))}
          </div>
        )}

        {activeTab === 'ambiguities' && (
          <div>
            <h2 className="card-title" style={{ marginBottom: '1rem' }}>Identified Ambiguities</h2>
            {standard.ambiguities.map((ambiguity, index) => (
              <div key={index} style={{ 
                marginBottom: '1.5rem',
                backgroundColor: 'rgba(245, 158, 11, 0.1)',
                border: '1px solid var(--warning)',
                borderRadius: '0.375rem',
                padding: '1rem'
              }}>
                <h3 style={{ fontWeight: '600', marginBottom: '0.5rem', color: 'var(--warning)' }}>
                  Ambiguity {index + 1}
                </h3>
                <p style={{ fontWeight: '500', marginBottom: '0.5rem' }}>{ambiguity.text}</p>
                <p style={{ marginBottom: '0.5rem' }}><strong>Context:</strong> {ambiguity.context}</p>
                <p><strong>Indicator:</strong> <span className="badge badge-warning">{ambiguity.indicator}</span></p>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default StandardDetail;
