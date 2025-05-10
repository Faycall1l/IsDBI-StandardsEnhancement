import axios from 'axios';

// Create an axios instance with default config
const api = axios.create({
  baseURL: 'http://localhost:8000',
  headers: {
    'Content-Type': 'application/json'
  }
});

// Document API services
export const documentService = {
  // Process a document
  processDocument: (filePath) => {
    return api.post('/documents/process', { file_path: filePath });
  },
  
  // Get all standards
  getStandards: () => {
    return api.get('/documents');
  },
  
  // Get standard details by ID
  getStandardById: (standardId) => {
    return api.get(`/documents/${standardId}`);
  }
};

// Enhancement API services
export const enhancementService = {
  // Generate enhancements for a standard
  generateEnhancements: (standardId) => {
    return api.post('/enhancements/generate', { standard_id: standardId });
  },
  
  // Get all enhancements with optional filters
  getEnhancements: (filters = {}) => {
    const { standard_id, enhancement_type, status } = filters;
    let url = '/enhancements';
    
    const params = new URLSearchParams();
    if (standard_id) params.append('standard_id', standard_id);
    if (enhancement_type) params.append('enhancement_type', enhancement_type);
    if (status) params.append('status', status);
    
    const queryString = params.toString();
    if (queryString) url += `?${queryString}`;
    
    return api.get(url);
  },
  
  // Get enhancement details by ID
  getEnhancementById: (enhancementId) => {
    return api.get(`/enhancements/${enhancementId}`);
  }
};

// Validation API services
export const validationService = {
  // Validate a proposal
  validateProposal: (proposalId) => {
    return api.post('/validations/validate', { proposal_id: proposalId });
  },
  
  // Get all validations with optional filters
  getValidations: (filters = {}) => {
    const { proposal_id, status } = filters;
    let url = '/validations';
    
    const params = new URLSearchParams();
    if (proposal_id) params.append('proposal_id', proposal_id);
    if (status) params.append('status', status);
    
    const queryString = params.toString();
    if (queryString) url += `?${queryString}`;
    
    return api.get(url);
  },
  
  // Get validation details by ID
  getValidationById: (validationId) => {
    return api.get(`/validations/${validationId}`);
  }
};

export default {
  documentService,
  enhancementService,
  validationService
};
