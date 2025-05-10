import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import './App.css';

// Layout components
import Navbar from './components/layout/Navbar';
import Sidebar from './components/layout/Sidebar';

// Page components
import Dashboard from './pages/Dashboard';
import Standards from './pages/Standards';
import StandardDetail from './pages/StandardDetail';
import Enhancements from './pages/Enhancements';
import EnhancementDetail from './pages/EnhancementDetail';
import Validations from './pages/Validations';
import ValidationDetail from './pages/ValidationDetail';
import ProcessDocument from './pages/ProcessDocument';

function App() {
  return (
    <Router>
      <div className="app">
        <Navbar />
        <div className="content-container">
          <Sidebar />
          <main className="main-content">
            <Routes>
              <Route path="/" element={<Dashboard />} />
              <Route path="/standards" element={<Standards />} />
              <Route path="/standards/:id" element={<StandardDetail />} />
              <Route path="/enhancements" element={<Enhancements />} />
              <Route path="/enhancements/:id" element={<EnhancementDetail />} />
              <Route path="/validations" element={<Validations />} />
              <Route path="/validations/:id" element={<ValidationDetail />} />
              <Route path="/process-document" element={<ProcessDocument />} />
            </Routes>
          </main>
        </div>
      </div>
    </Router>
  );
}

export default App;
