import React, { useState, useEffect } from 'react';
import { Link, useLocation } from 'react-router-dom';

const Standards = () => {
  const [standards, setStandards] = useState([]);
  const [loading, setLoading] = useState(true);
  const location = useLocation();
  const queryParams = new URLSearchParams(location.search);
  const typeFilter = queryParams.get('type');

  useEffect(() => {
    // In a real implementation, this would fetch data from the API
    // For the hackathon demo, we'll use mock data
    setTimeout(() => {
      const mockStandards = [
        {
          id: '1',
          title: 'Salam and Parallel Salam',
          standard_type: 'FAS',
          standard_number: '10',
          publication_date: '2020-01-01',
          description: 'This standard prescribes the accounting rules for Salam and Parallel Salam transactions and different types of revenues, expenses, gains and losses related to these transactions.'
        },
        {
          id: '2',
          title: 'Ijarah and Ijarah Muntahia Bittamleek',
          standard_type: 'FAS',
          standard_number: '32',
          publication_date: '2021-03-15',
          description: 'This standard sets out the principles for the classification, recognition, measurement, presentation and disclosure of Ijarah (asset leasing) transactions including different forms of Ijarah Muntahia Bittamleek.'
        },
        {
          id: '3',
          title: 'Murabaha and Other Deferred Payment Sales',
          standard_type: 'FAS',
          standard_number: '28',
          publication_date: '2019-11-30',
          description: 'This standard prescribes the accounting and reporting principles for recognition, measurement and disclosure for Murabaha and other deferred payment sales transactions.'
        },
        {
          id: '4',
          title: 'Salam and Parallel Salam',
          standard_type: 'SS',
          standard_number: '10',
          publication_date: '2018-06-22',
          description: 'This Shariah standard defines the Shariah rules for Salam and Parallel Salam contracts, their conditions, and permissible structures.'
        },
        {
          id: '5',
          title: 'Ijarah and Ijarah Muntahia Bittamleek',
          standard_type: 'SS',
          standard_number: '9',
          publication_date: '2017-09-10',
          description: 'This Shariah standard outlines the Shariah rules for Ijarah contracts, including conditions, rights, and obligations of the lessor and lessee.'
        }
      ];

      // Apply type filter if present
      const filteredStandards = typeFilter 
        ? mockStandards.filter(s => s.standard_type === typeFilter)
        : mockStandards;

      setStandards(filteredStandards);
      setLoading(false);
    }, 1000);
  }, [typeFilter]);

  return (
    <div>
      <div className="card-header" style={{ marginBottom: '1.5rem' }}>
        <h1 className="card-title">
          {typeFilter ? `${typeFilter} Standards` : 'All Standards'}
        </h1>
        <Link to="/process-document" className="btn btn-primary">
          <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="btn-icon">
            <line x1="12" y1="5" x2="12" y2="19"></line>
            <line x1="5" y1="12" x2="19" y2="12"></line>
          </svg>
          Process New Standard
        </Link>
      </div>
      
      {loading ? (
        <div className="card">
          <p>Loading standards...</p>
        </div>
      ) : (
        <div>
          {standards.map((standard) => (
            <div className="card" key={standard.id}>
              <div className="card-header">
                <h2 className="card-title">
                  {standard.title}
                  <span className="badge badge-primary" style={{ marginLeft: '0.75rem' }}>
                    {standard.standard_type} {standard.standard_number}
                  </span>
                </h2>
                <Link to={`/standards/${standard.id}`} className="btn btn-secondary">
                  View Details
                </Link>
              </div>
              <p style={{ marginBottom: '1rem' }}>{standard.description}</p>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <span style={{ color: 'var(--text-secondary)', fontSize: '0.875rem' }}>
                  Published: {new Date(standard.publication_date).toLocaleDateString()}
                </span>
                <div>
                  <Link to={`/enhancements?standard_id=${standard.id}`} className="btn btn-secondary" style={{ marginRight: '0.5rem' }}>
                    View Enhancements
                  </Link>
                  <Link to={`/standards/${standard.id}`} className="btn btn-primary">
                    Generate Enhancements
                  </Link>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default Standards;
