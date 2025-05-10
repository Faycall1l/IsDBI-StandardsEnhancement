"""
Simple Frontend for Islamic Finance Standards Enhancement Platform

This script creates a simplified Flask application to demonstrate the
community collaboration platform interface.
"""

import os
import logging
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from dotenv import load_dotenv

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
            template_folder='IslamicFinanceStandardsAI/frontend/templates',
            static_folder='IslamicFinanceStandardsAI/frontend/static')
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'dev_secret_key')

# Mock data for demonstration
class MockUser:
    def __init__(self, id, name, email, role):
        self.id = id
        self.name = name
        self.email = email
        self.role = role
        self.is_authenticated = True
        self.is_active = True
        self.is_anonymous = False
    
    def get_id(self):
        return self.id

class MockRole:
    def __init__(self, value):
        self.value = value

# Create mock users
admin_user = MockUser("1", "Admin User", "admin@example.com", MockRole("admin"))
scholar_user = MockUser("2", "Scholar User", "scholar@example.com", MockRole("scholar"))
regulator_user = MockUser("3", "Regulator User", "regulator@example.com", MockRole("regulator"))
practitioner_user = MockUser("4", "Practitioner User", "practitioner@example.com", MockRole("practitioner"))

# Mock current user for demonstration
current_user = admin_user

# Mock proposals data
proposals = [
    {
        "id": "1",
        "properties": {
            "title": "Clarification of Musharaka Profit Distribution",
            "standard_id": "FAS 4",
            "section": "3.2",
            "current_text": "Profits shall be distributed among partners according to the agreed ratio.",
            "proposed_text": "Profits shall be distributed among partners according to the agreed ratio, which must be explicitly stated in the Musharaka agreement. The profit-sharing ratio must be a percentage of the actual profit, not a lump sum or guaranteed amount.",
            "rationale": "The current text lacks specificity regarding the nature of profit distribution, which could lead to practices that violate Shariah principles such as guaranteeing returns or using predetermined fixed amounts.",
            "impact_analysis": "This clarification will ensure that Musharaka contracts adhere more strictly to Shariah principles of profit-and-loss sharing, reducing the risk of non-compliant structures.",
            "status": "pending",
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        },
        "votes": {
            "upvotes": 12,
            "downvotes": 3,
            "score": 9
        }
    },
    {
        "id": "2",
        "properties": {
            "title": "Enhanced Disclosure Requirements for Diminishing Musharaka",
            "standard_id": "FAS 4",
            "section": "4.5",
            "current_text": "Institutions shall disclose the nature of Musharaka contracts in their financial statements.",
            "proposed_text": "Institutions shall disclose the nature of Musharaka contracts in their financial statements, including detailed information for Diminishing Musharaka arrangements. This disclosure must include: (a) the initial ownership ratio, (b) the schedule of ownership transfers, (c) the valuation methodology for ownership units, and (d) any rental or lease arrangements associated with the partner's use of the Musharaka asset.",
            "rationale": "Diminishing Musharaka structures are increasingly common in Islamic finance, particularly for home financing, but the current standard lacks specific disclosure requirements for these arrangements.",
            "impact_analysis": "Enhanced disclosure will improve transparency and comparability across institutions, helping stakeholders better understand the economic substance of Diminishing Musharaka arrangements.",
            "status": "approved",
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        },
        "votes": {
            "upvotes": 18,
            "downvotes": 2,
            "score": 16
        }
    },
    {
        "id": "3",
        "properties": {
            "title": "Clarification on Ijarah Rental Determination",
            "standard_id": "FAS 8",
            "section": "5.1",
            "current_text": "Rental must be determined at the time of contract for the entire period of the Ijarah.",
            "proposed_text": "Rental must be determined at the time of contract for the entire period of the Ijarah. For long-term Ijarah contracts, the rental amount may be adjusted periodically based on a clear formula or benchmark agreed upon by both parties at the time of the contract. Such adjustments must not be linked to interest rate benchmarks like LIBOR or EURIBOR.",
            "rationale": "The current standard does not adequately address the issue of rental adjustments in long-term Ijarah contracts, leading to practices that may indirectly link rentals to interest-based benchmarks.",
            "impact_analysis": "This clarification will provide a Shariah-compliant framework for rental adjustments in long-term Ijarah contracts, reducing reliance on interest-based benchmarks.",
            "status": "needs_revision",
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        },
        "votes": {
            "upvotes": 8,
            "downvotes": 5,
            "score": 3
        }
    }
]

# Mock comments
comments = [
    {
        "id": "1",
        "text": "This enhancement provides much-needed clarity on profit distribution in Musharaka contracts.",
        "user_id": "2",
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "proposal_id": "1",
        "user": {
            "name": "Scholar User",
            "role": "scholar"
        }
    },
    {
        "id": "2",
        "text": "I suggest adding a reference to AAOIFI Shariah Standard 12 which covers Musharaka in detail.",
        "user_id": "3",
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "proposal_id": "1",
        "user": {
            "name": "Regulator User",
            "role": "regulator"
        }
    },
    {
        "id": "3",
        "text": "The proposed text aligns well with the principles of profit and loss sharing in Islamic finance.",
        "user_id": "4",
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "proposal_id": "1",
        "user": {
            "name": "Practitioner User",
            "role": "practitioner"
        }
    }
]

# Mock suggestions
suggestions = [
    {
        "id": "1",
        "text": "Consider adding a clause about dispute resolution mechanisms for profit calculation disagreements.",
        "user_id": "2",
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "proposal_id": "1",
        "status": "pending",
        "user": {
            "name": "Scholar User",
            "role": "scholar"
        }
    },
    {
        "id": "2",
        "text": "The standard should explicitly prohibit any guaranteed returns to any partner.",
        "user_id": "3",
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "proposal_id": "1",
        "status": "accepted",
        "user": {
            "name": "Regulator User",
            "role": "regulator"
        }
    }
]

# Mock validation results
validation_results = [
    {
        "id": "1",
        "properties": {
            "is_shariah_compliant": True,
            "feedback": "The proposed enhancement aligns with Shariah principles of profit-and-loss sharing in Musharaka contracts.",
            "improvement_suggestions": "Consider adding explicit examples of compliant and non-compliant profit distribution mechanisms.",
            "references": ["Quran 4:12", "AAOIFI Shariah Standard 12", "IFSB Standard 15"],
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
    }
]

# Routes
@app.route('/')
def index():
    """Home page"""
    top_proposals = sorted(proposals, key=lambda p: p["votes"]["score"], reverse=True)[:5]
    recent_activities = []
    return render_template('index.html', top_proposals=top_proposals, recent_activities=recent_activities)

@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login page"""
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        # Simple mock login
        if email == "admin@example.com" and password == "admin123":
            global current_user
            current_user = admin_user
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        elif email == "scholar@example.com" and password == "scholar123":
            current_user = scholar_user
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        elif email == "regulator@example.com" and password == "regulator123":
            current_user = regulator_user
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        elif email == "practitioner@example.com" and password == "practitioner123":
            current_user = practitioner_user
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password', 'danger')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    """User logout"""
    global current_user
    current_user = None
    flash('You have been logged out', 'info')
    return redirect(url_for('index'))

@app.route('/dashboard')
def dashboard():
    """User dashboard"""
    user_stats = {
        "comments": 3,
        "votes": 5,
        "suggestions": 2
    }
    user_activity = []
    top_proposals = sorted(proposals, key=lambda p: p["votes"]["score"], reverse=True)[:5]
    return render_template('dashboard.html', user_stats=user_stats, user_activity=user_activity, top_proposals=top_proposals)

@app.route('/proposals')
def proposals_list():
    """View all enhancement proposals"""
    return render_template('proposals.html', proposals=proposals)

@app.route('/proposals/<proposal_id>')
def view_proposal(proposal_id):
    """View a specific proposal"""
    proposal = next((p for p in proposals if p["id"] == proposal_id), None)
    if not proposal:
        flash('Proposal not found', 'danger')
        return redirect(url_for('proposals_list'))
    
    proposal_comments = [c for c in comments if c["proposal_id"] == proposal_id]
    proposal_suggestions = [s for s in suggestions if s["proposal_id"] == proposal_id]
    
    return render_template('proposal_detail.html', 
                          proposal=proposal,
                          comments=proposal_comments,
                          suggestions=proposal_suggestions,
                          validation_results=validation_results)

@app.route('/proposals/<proposal_id>/vote', methods=['POST'])
def vote_proposal(proposal_id):
    """Vote on a proposal"""
    vote_type = request.form.get('vote_type')
    
    if vote_type not in ['upvote', 'downvote']:
        flash('Invalid vote type', 'danger')
        return redirect(url_for('view_proposal', proposal_id=proposal_id))
    
    # Mock vote recording
    proposal = next((p for p in proposals if p["id"] == proposal_id), None)
    if proposal:
        if vote_type == 'upvote':
            proposal["votes"]["upvotes"] += 1
            proposal["votes"]["score"] += 1
        else:
            proposal["votes"]["downvotes"] += 1
            proposal["votes"]["score"] -= 1
        
        flash('Vote recorded successfully', 'success')
    else:
        flash('Failed to record vote', 'danger')
    
    return redirect(url_for('view_proposal', proposal_id=proposal_id))

@app.route('/proposals/<proposal_id>/comment', methods=['POST'])
def comment_proposal(proposal_id):
    """Comment on a proposal"""
    comment_text = request.form.get('comment')
    
    if not comment_text:
        flash('Comment cannot be empty', 'danger')
        return redirect(url_for('view_proposal', proposal_id=proposal_id))
    
    # Mock comment creation
    new_comment = {
        "id": str(len(comments) + 1),
        "text": comment_text,
        "user_id": current_user.id,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "proposal_id": proposal_id,
        "user": {
            "name": current_user.name,
            "role": current_user.role.value
        }
    }
    
    comments.append(new_comment)
    flash('Comment added successfully', 'success')
    
    return redirect(url_for('view_proposal', proposal_id=proposal_id))

@app.route('/proposals/<proposal_id>/suggest', methods=['POST'])
def suggest_improvement(proposal_id):
    """Suggest improvement to a proposal"""
    suggestion_text = request.form.get('suggestion')
    
    if not suggestion_text:
        flash('Suggestion cannot be empty', 'danger')
        return redirect(url_for('view_proposal', proposal_id=proposal_id))
    
    # Mock suggestion creation
    new_suggestion = {
        "id": str(len(suggestions) + 1),
        "text": suggestion_text,
        "user_id": current_user.id,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "proposal_id": proposal_id,
        "status": "pending",
        "user": {
            "name": current_user.name,
            "role": current_user.role.value
        }
    }
    
    suggestions.append(new_suggestion)
    flash('Suggestion added successfully', 'success')
    
    return redirect(url_for('view_proposal', proposal_id=proposal_id))

@app.route('/admin')
def admin_dashboard():
    """Admin dashboard"""
    if current_user.role.value != "admin" and current_user.role.value != "scholar":
        flash('Access denied', 'danger')
        return redirect(url_for('dashboard'))
    
    return render_template('admin/dashboard.html')

# Template context processor
@app.context_processor
def inject_current_user():
    return {"current_user": current_user}

if __name__ == '__main__':
    app.run(debug=True, port=5000)
