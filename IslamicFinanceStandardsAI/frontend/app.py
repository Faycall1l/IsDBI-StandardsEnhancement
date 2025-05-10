"""
Community Collaboration Platform for Islamic Finance Standards Enhancement

This module provides a web interface for:
1. Viewing enhancement proposals
2. Collaborative refinement of suggestions
3. Structured voting/ranking of proposed changes
4. Permission-based access for different stakeholder groups
"""

import os
import logging
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from flask_login import LoginManager, login_required, login_user, logout_user, current_user
from dotenv import load_dotenv

# Import custom modules
from IslamicFinanceStandardsAI.models.user import User, UserRole
from IslamicFinanceStandardsAI.models.enhancement_schema import EnhancementProposal, EnhancementStatus
from IslamicFinanceStandardsAI.models.validation_schema import ValidationResult
from IslamicFinanceStandardsAI.database.knowledge_graph import KnowledgeGraph
from IslamicFinanceStandardsAI.integration.hybrid_storage_manager import get_hybrid_storage_manager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__, 
            template_folder='templates',
            static_folder='static')
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'dev_secret_key')

# Initialize login manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Initialize knowledge graph and hybrid storage
knowledge_graph = KnowledgeGraph()
hybrid_storage = get_hybrid_storage_manager()

# User loader for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return User.get_by_id(user_id)

# Routes
@app.route('/')
def index():
    """Home page"""
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login page"""
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        user = User.authenticate(email, password)
        if user:
            login_user(user)
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password', 'danger')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    """User logout"""
    logout_user()
    flash('You have been logged out', 'info')
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    """User registration page"""
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        role = request.form.get('role', UserRole.PRACTITIONER.value)
        
        # Simple validation
        if not all([name, email, password]):
            flash('All fields are required', 'danger')
            return render_template('register.html')
        
        # Check if user already exists
        if User.get_by_email(email):
            flash('Email already registered', 'danger')
            return render_template('register.html')
        
        # Create new user
        user = User.create(name, email, password, role)
        if user:
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('login'))
        else:
            flash('Registration failed', 'danger')
    
    return render_template('register.html')

@app.route('/dashboard')
@login_required
def dashboard():
    """User dashboard"""
    return render_template('dashboard.html')

@app.route('/proposals')
@login_required
def proposals():
    """View all enhancement proposals"""
    # Get proposals from knowledge graph
    all_proposals = knowledge_graph.get_all_enhancement_proposals()
    
    return render_template('proposals.html', proposals=all_proposals)

@app.route('/proposals/<proposal_id>')
@login_required
def view_proposal(proposal_id):
    """View a specific proposal"""
    proposal = knowledge_graph.get_enhancement_proposal(proposal_id)
    validation_results = knowledge_graph.get_validation_results_for_proposal(proposal_id)
    comments = knowledge_graph.get_comments_for_proposal(proposal_id)
    
    return render_template('proposal_detail.html', 
                          proposal=proposal,
                          validation_results=validation_results,
                          comments=comments)

@app.route('/proposals/<proposal_id>/vote', methods=['POST'])
@login_required
def vote_proposal(proposal_id):
    """Vote on a proposal"""
    vote_type = request.form.get('vote_type')
    
    if vote_type not in ['upvote', 'downvote']:
        flash('Invalid vote type', 'danger')
        return redirect(url_for('view_proposal', proposal_id=proposal_id))
    
    # Record the vote
    result = knowledge_graph.record_vote(proposal_id, current_user.id, vote_type)
    
    if result:
        flash('Vote recorded successfully', 'success')
    else:
        flash('Failed to record vote', 'danger')
    
    return redirect(url_for('view_proposal', proposal_id=proposal_id))

@app.route('/proposals/<proposal_id>/comment', methods=['POST'])
@login_required
def comment_proposal(proposal_id):
    """Comment on a proposal"""
    comment_text = request.form.get('comment')
    
    if not comment_text:
        flash('Comment cannot be empty', 'danger')
        return redirect(url_for('view_proposal', proposal_id=proposal_id))
    
    # Add the comment
    result = knowledge_graph.add_comment(proposal_id, current_user.id, comment_text)
    
    if result:
        flash('Comment added successfully', 'success')
    else:
        flash('Failed to add comment', 'danger')
    
    return redirect(url_for('view_proposal', proposal_id=proposal_id))

@app.route('/proposals/<proposal_id>/suggest', methods=['POST'])
@login_required
def suggest_improvement(proposal_id):
    """Suggest improvement to a proposal"""
    suggestion_text = request.form.get('suggestion')
    
    if not suggestion_text:
        flash('Suggestion cannot be empty', 'danger')
        return redirect(url_for('view_proposal', proposal_id=proposal_id))
    
    # Add the suggestion
    result = knowledge_graph.add_suggestion(proposal_id, current_user.id, suggestion_text)
    
    if result:
        flash('Suggestion added successfully', 'success')
    else:
        flash('Failed to add suggestion', 'danger')
    
    return redirect(url_for('view_proposal', proposal_id=proposal_id))

@app.route('/api/proposals', methods=['GET'])
def api_get_proposals():
    """API endpoint to get proposals"""
    proposals = knowledge_graph.get_all_enhancement_proposals()
    return jsonify([p.to_dict() for p in proposals])

@app.route('/api/proposals/<proposal_id>', methods=['GET'])
def api_get_proposal(proposal_id):
    """API endpoint to get a specific proposal"""
    proposal = knowledge_graph.get_enhancement_proposal(proposal_id)
    if proposal:
        return jsonify(proposal.to_dict())
    return jsonify({"error": "Proposal not found"}), 404

@app.route('/api/search', methods=['GET'])
def api_search():
    """API endpoint for semantic search"""
    query = request.args.get('q', '')
    use_web = request.args.get('web', 'false').lower() == 'true'
    
    if not query:
        return jsonify({"error": "Query parameter 'q' is required"}), 400
    
    # Perform semantic search
    results = hybrid_storage.get_similar_documents(query, top_k=5, use_web=use_web)
    
    return jsonify(results)

# Admin routes
@app.route('/admin')
@login_required
def admin_dashboard():
    """Admin dashboard"""
    if current_user.role != UserRole.ADMIN and current_user.role != UserRole.SCHOLAR:
        flash('Access denied', 'danger')
        return redirect(url_for('dashboard'))
    
    return render_template('admin/dashboard.html')

@app.route('/admin/users')
@login_required
def admin_users():
    """Manage users"""
    if current_user.role != UserRole.ADMIN:
        flash('Access denied', 'danger')
        return redirect(url_for('dashboard'))
    
    users = User.get_all()
    return render_template('admin/users.html', users=users)

@app.route('/admin/proposals')
@login_required
def admin_proposals():
    """Manage proposals"""
    if current_user.role != UserRole.ADMIN and current_user.role != UserRole.SCHOLAR:
        flash('Access denied', 'danger')
        return redirect(url_for('dashboard'))
    
    proposals = knowledge_graph.get_all_enhancement_proposals()
    return render_template('admin/proposals.html', proposals=proposals)

@app.route('/admin/proposals/<proposal_id>/status', methods=['POST'])
@login_required
def update_proposal_status(proposal_id):
    """Update proposal status"""
    if current_user.role != UserRole.ADMIN and current_user.role != UserRole.SCHOLAR:
        flash('Access denied', 'danger')
        return redirect(url_for('dashboard'))
    
    new_status = request.form.get('status')
    if new_status not in [s.value for s in EnhancementStatus]:
        flash('Invalid status', 'danger')
        return redirect(url_for('admin_proposals'))
    
    # Update the status
    result = knowledge_graph.update_proposal_status(proposal_id, new_status)
    
    if result:
        flash('Status updated successfully', 'success')
    else:
        flash('Failed to update status', 'danger')
    
    return redirect(url_for('admin_proposals'))

if __name__ == '__main__':
    # Create necessary directories
    os.makedirs('frontend/templates', exist_ok=True)
    os.makedirs('frontend/static/css', exist_ok=True)
    os.makedirs('frontend/static/js', exist_ok=True)
    
    # Run the app
    app.run(debug=True, host='0.0.0.0', port=5000)
