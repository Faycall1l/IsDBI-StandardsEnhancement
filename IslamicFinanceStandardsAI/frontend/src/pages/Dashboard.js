import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';

const Dashboard = () => {
  const [stats, setStats] = useState({
    standards: 0,
    enhancements: 0,
    validations: 0,
    approvalRate: 0
  });

  const [recentActivity, setRecentActivity] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // In a real implementation, this would fetch data from the API
    // For the hackathon demo, we'll use mock data
    setTimeout(() => {
      setStats({
        standards: 3,
        enhancements: 12,
        validations: 8,
        approvalRate: 75
      });

      setRecentActivity([
        {
          id: '1',
          type: 'enhancement',
          title: 'Improved definition of Murabaha',
          standard: 'FAS 28',
          timestamp: '2025-05-08T14:30:00Z',
          status: 'APPROVED'
        },
        {
          id: '2',
          type: 'validation',
          title: 'Validation of Ijarah accounting treatment',
          standard: 'FAS 32',
          timestamp: '2025-05-08T12:15:00Z',
          status: 'APPROVED_WITH_MODIFICATIONS'
        },
        {
          id: '3',
          type: 'document',
          title: 'Processed Salam and Parallel Salam standard',
          standard: 'FAS 10',
          timestamp: '2025-05-08T10:45:00Z',
          status: 'COMPLETED'
        }
      ]);

      setLoading(false);
    }, 1000);
  }, []);

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

  return (
    <div>
      <h1 className="card-title" style={{ marginBottom: '1.5rem' }}>Dashboard</h1>
      
      {loading ? (
        <div className="card">
          <p>Loading dashboard data...</p>
        </div>
      ) : (
        <>
          <div className="dashboard-grid">
            <div className="card">
              <h2 className="card-title">Standards</h2>
              <div style={{ fontSize: '2rem', fontWeight: 'bold', color: 'var(--primary)' }}>
                {stats.standards}
              </div>
              <p>AAOIFI standards processed</p>
              <Link to="/standards" className="btn btn-primary" style={{ marginTop: '1rem' }}>
                View Standards
              </Link>
            </div>

            <div className="card">
              <h2 className="card-title">Enhancements</h2>
              <div style={{ fontSize: '2rem', fontWeight: 'bold', color: 'var(--primary)' }}>
                {stats.enhancements}
              </div>
              <p>AI-generated enhancement proposals</p>
              <Link to="/enhancements" className="btn btn-primary" style={{ marginTop: '1rem' }}>
                View Enhancements
              </Link>
            </div>

            <div className="card">
              <h2 className="card-title">Validations</h2>
              <div style={{ fontSize: '2rem', fontWeight: 'bold', color: 'var(--primary)' }}>
                {stats.validations}
              </div>
              <p>Shariah compliance validations</p>
              <Link to="/validations" className="btn btn-primary" style={{ marginTop: '1rem' }}>
                View Validations
              </Link>
            </div>

            <div className="card">
              <h2 className="card-title">Approval Rate</h2>
              <div style={{ fontSize: '2rem', fontWeight: 'bold', color: 'var(--primary)' }}>
                {stats.approvalRate}%
              </div>
              <p>Enhancement approval rate</p>
              <div style={{ 
                width: '100%', 
                height: '8px', 
                backgroundColor: 'var(--border)',
                borderRadius: '4px',
                marginTop: '1rem'
              }}>
                <div style={{ 
                  width: `${stats.approvalRate}%`, 
                  height: '100%', 
                  backgroundColor: 'var(--primary)',
                  borderRadius: '4px'
                }}></div>
              </div>
            </div>
          </div>

          <div className="card" style={{ marginTop: '1.5rem' }}>
            <div className="card-header">
              <h2 className="card-title">Recent Activity</h2>
            </div>
            <table className="table">
              <thead>
                <tr>
                  <th>Activity</th>
                  <th>Standard</th>
                  <th>Time</th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody>
                {recentActivity.map((activity) => (
                  <tr key={activity.id}>
                    <td>
                      <Link 
                        to={`/${activity.type}s/${activity.id}`}
                        style={{ color: 'var(--primary)', textDecoration: 'none', fontWeight: '500' }}
                      >
                        {activity.title}
                      </Link>
                    </td>
                    <td>{activity.standard}</td>
                    <td>{new Date(activity.timestamp).toLocaleString()}</td>
                    <td>
                      <span className={getStatusBadgeClass(activity.status)}>
                        {activity.status.replace(/_/g, ' ')}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </>
      )}
    </div>
  );
};

export default Dashboard;
