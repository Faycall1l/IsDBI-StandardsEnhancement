from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import os
import json
from datetime import datetime, timedelta
import random
import sys

# Add parent directory to path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the knowledge graph and enhancement modules
from IslamicFinanceStandardsAI.database.knowledge_graph import KnowledgeGraph
from IslamicFinanceStandardsAI.enhancement.enhancement_generator import EnhancementGenerator
from IslamicFinanceStandardsAI.utils.web_retriever import WebRetriever
from IslamicFinanceStandardsAI.utils.custom_embeddings import CustomEmbeddings

app = Flask(__name__, 
            template_folder='IslamicFinanceStandardsAI/frontend/templates',
            static_folder='IslamicFinanceStandardsAI/frontend/static')
app.secret_key = 'simplified_secret_key'

# Initialize knowledge graph (using in-memory Neo4j for simplicity)
knowledge_graph = KnowledgeGraph(uri="bolt://localhost:7687", 
                               user="neo4j", 
                               password="password",
                               use_memory_db=True)

# Initialize web retriever and embeddings
web_retriever = WebRetriever()
custom_embeddings = CustomEmbeddings()

# Initialize enhancement generator
enhancement_generator = EnhancementGenerator(knowledge_graph=knowledge_graph,
                                          web_retriever=web_retriever,
                                          embeddings=custom_embeddings)

# Mock data for demonstration
STANDARDS = [
    {"id": "1", "name": "FAS 1", "title": "General Presentation and Disclosure in the Financial Statements of Islamic Banks and Financial Institutions"},
    {"id": "2", "name": "FAS 2", "title": "Murabaha and Murabaha to the Purchase Orderer"},
    {"id": "3", "name": "FAS 3", "title": "Mudaraba Financing"},
    {"id": "4", "name": "FAS 4", "title": "Musharaka Financing"},
    {"id": "5", "name": "FAS 8", "title": "Ijarah and Ijarah Muntahia Bittamleek"},
    {"id": "6", "name": "FAS 9", "title": "Zakah"},
    {"id": "7", "name": "FAS 17", "title": "Investments"},
    {"id": "8", "name": "FAS 23", "title": "Consolidation"},
    {"id": "9", "name": "FAS 28", "title": "Murabaha and Other Deferred Payment Sales"},
]

PROPOSALS = [
    {
        "id": "1",
        "standard_id": "4",
        "title": "Enhancement to Musharaka Loss Allocation Mechanism",
        "current_text": "Losses are shared strictly according to capital contribution ratios.",
        "proposed_text": "Losses are shared according to capital contribution ratios, with provisions for special circumstances where partners may agree to different allocations based on documented negligence or breach of contract.",
        "rationale": "The current strict allocation doesn't account for situations where losses are caused by one partner's negligence.",
        "status": "pending",
        "created_at": (datetime.now() - timedelta(days=5)).strftime("%Y-%m-%d"),
        "votes_up": 12,
        "votes_down": 3,
        "comments": [
            {"id": "1", "user": "Scholar", "text": "This enhancement aligns with the principle of fairness in Islamic finance.", "created_at": (datetime.now() - timedelta(days=4)).strftime("%Y-%m-%d")},
            {"id": "2", "user": "Practitioner", "text": "This would be very helpful for practical implementation in complex partnerships.", "created_at": (datetime.now() - timedelta(days=3)).strftime("%Y-%m-%d")},
        ],
        "suggestions": [
            {"id": "1", "user": "Regulator", "text": "Consider adding specific documentation requirements for proving negligence.", "created_at": (datetime.now() - timedelta(days=2)).strftime("%Y-%m-%d")},
        ],
        "validation": {"is_valid": True, "reason": "Compliant with Shariah principles of justice and fairness"}
    },
    {
        "id": "2",
        "standard_id": "5",
        "title": "Clarification on Digital Assets in Ijarah Contracts",
        "current_text": "Ijarah applies to tangible assets that provide usufruct over time.",
        "proposed_text": "Ijarah applies to tangible assets and certain digital assets that provide usufruct over time. Digital assets qualifying for Ijarah must have defined useful life, identifiable value, and separable usufruct from ownership.",
        "rationale": "The digital economy has created new asset types that weren't considered in the original standard.",
        "status": "approved",
        "created_at": (datetime.now() - timedelta(days=15)).strftime("%Y-%m-%d"),
        "votes_up": 25,
        "votes_down": 2,
        "comments": [
            {"id": "3", "user": "Scholar", "text": "This is a necessary adaptation to modern economic realities.", "created_at": (datetime.now() - timedelta(days=14)).strftime("%Y-%m-%d")},
            {"id": "4", "user": "Practitioner", "text": "Will help financial institutions offer more innovative products.", "created_at": (datetime.now() - timedelta(days=12)).strftime("%Y-%m-%d")},
        ],
        "suggestions": [],
        "validation": {"is_valid": True, "reason": "Maintains the essence of Ijarah while adapting to technological changes"}
    },
    {
        "id": "3",
        "standard_id": "2",
        "title": "Enhanced Disclosure Requirements for Murabaha Transactions",
        "current_text": "Financial institutions shall disclose the general structure of Murabaha transactions.",
        "proposed_text": "Financial institutions shall disclose the general structure of Murabaha transactions, including detailed profit calculation methodologies, risk management practices, and any special arrangements affecting the effective profit rate.",
        "rationale": "Greater transparency is needed to build trust and ensure compliance with Shariah principles.",
        "status": "needs_revision",
        "created_at": (datetime.now() - timedelta(days=10)).strftime("%Y-%m-%d"),
        "votes_up": 8,
        "votes_down": 7,
        "comments": [
            {"id": "5", "user": "Regulator", "text": "This level of disclosure may be excessive for some institutions.", "created_at": (datetime.now() - timedelta(days=9)).strftime("%Y-%m-%d")},
            {"id": "6", "user": "Scholar", "text": "The principle is sound but implementation details need work.", "created_at": (datetime.now() - timedelta(days=8)).strftime("%Y-%m-%d")},
        ],
        "suggestions": [
            {"id": "2", "user": "Practitioner", "text": "Consider a tiered disclosure approach based on transaction size.", "created_at": (datetime.now() - timedelta(days=6)).strftime("%Y-%m-%d")},
        ],
        "validation": {"is_valid": True, "reason": "Promotes transparency but implementation concerns remain"}
    },
    {
        "id": "4",
        "standard_id": "9",
        "title": "Standardization of Deferred Payment Sales Documentation",
        "current_text": "Documentation should clearly state all terms and conditions of the sale.",
        "proposed_text": "Documentation should follow standardized templates that clearly state all terms and conditions of the sale, with specific sections addressing: asset description, cost price, markup calculation, payment schedule, late payment policies, and early settlement options.",
        "rationale": "Standardized documentation improves transparency and reduces Shariah compliance risks.",
        "status": "rejected",
        "created_at": (datetime.now() - timedelta(days=20)).strftime("%Y-%m-%d"),
        "votes_up": 5,
        "votes_down": 15,
        "comments": [
            {"id": "7", "user": "Scholar", "text": "Too prescriptive and doesn't allow for necessary flexibility.", "created_at": (datetime.now() - timedelta(days=18)).strftime("%Y-%m-%d")},
            {"id": "8", "user": "Practitioner", "text": "Different jurisdictions have different legal requirements that make standardization difficult.", "created_at": (datetime.now() - timedelta(days=17)).strftime("%Y-%m-%d")},
        ],
        "suggestions": [],
        "validation": {"is_valid": False, "reason": "Overly prescriptive and impractical across different jurisdictions"}
    },
]

# Routes
@app.route('/')
def index():
    # Get top proposals by votes
    top_proposals = sorted(PROPOSALS, key=lambda x: x['votes_up'] - x['votes_down'], reverse=True)[:3]
    
    # Get recent activities (comments and suggestions)
    recent_activities = []
    for proposal in PROPOSALS:
        for comment in proposal['comments']:
            recent_activities.append({
                'type': 'comment',
                'user': comment['user'],
                'proposal_id': proposal['id'],
                'proposal_title': proposal['title'],
                'text': comment['text'],
                'created_at': comment['created_at']
            })
        for suggestion in proposal['suggestions']:
            recent_activities.append({
                'type': 'suggestion',
                'user': suggestion['user'],
                'proposal_id': proposal['id'],
                'proposal_title': proposal['title'],
                'text': suggestion['text'],
                'created_at': suggestion['created_at']
            })
    
    # Sort by date (newest first) and limit to 5
    recent_activities = sorted(recent_activities, key=lambda x: x['created_at'], reverse=True)[:5]
    
    return render_template('simple_index.html', top_proposals=top_proposals, recent_activities=recent_activities)

@app.route('/dashboard')
def dashboard():
    # Get user's recent activity
    user_activities = []
    for proposal in PROPOSALS:
        for comment in proposal['comments']:
            if comment['user'] == 'Demo User':
                user_activities.append({
                    'type': 'comment',
                    'proposal_id': proposal['id'],
                    'proposal_title': proposal['title'],
                    'text': comment['text'],
                    'created_at': comment['created_at']
                })
        for suggestion in proposal['suggestions']:
            if suggestion['user'] == 'Demo User':
                user_activities.append({
                    'type': 'suggestion',
                    'proposal_id': proposal['id'],
                    'proposal_title': proposal['title'],
                    'text': suggestion['text'],
                    'created_at': suggestion['created_at']
                })
    
    # Sort by date (newest first)
    user_activities = sorted(user_activities, key=lambda x: x['created_at'], reverse=True)
    
    # Get proposals with most activity
    proposals_with_activity = []
    for proposal in PROPOSALS:
        activity_count = len(proposal['comments']) + len(proposal['suggestions'])
        proposals_with_activity.append({
            'id': proposal['id'],
            'title': proposal['title'],
            'status': proposal['status'],
            'activity_count': activity_count,
            'votes': proposal['votes_up'] - proposal['votes_down']
        })
    
    # Sort by activity count (highest first)
    proposals_with_activity = sorted(proposals_with_activity, key=lambda x: x['activity_count'], reverse=True)
    
    return render_template('simple_dashboard.html', 
                          user_activities=user_activities, 
                          proposals_with_activity=proposals_with_activity)

@app.route('/proposals')
def proposals_list():
    # Filter by status if provided
    status = request.args.get('status')
    sort_by = request.args.get('sort', 'newest')
    
    filtered_proposals = PROPOSALS
    if status:
        filtered_proposals = [p for p in PROPOSALS if p['status'] == status]
    
    # Sort proposals
    if sort_by == 'votes':
        filtered_proposals = sorted(filtered_proposals, key=lambda x: x['votes_up'] - x['votes_down'], reverse=True)
    elif sort_by == 'comments':
        filtered_proposals = sorted(filtered_proposals, key=lambda x: len(x['comments']), reverse=True)
    else:  # newest
        filtered_proposals = sorted(filtered_proposals, key=lambda x: x['created_at'], reverse=True)
    
    return render_template('simple_proposals.html', proposals=filtered_proposals)

@app.route('/proposal/<proposal_id>')
def proposal_detail(proposal_id):
    # Find the proposal by ID
    proposal = next((p for p in PROPOSALS if p['id'] == proposal_id), None)
    
    if not proposal:
        flash('Proposal not found', 'danger')
        return redirect(url_for('proposals_list'))
    
    # Find the standard
    standard = next((s for s in STANDARDS if s['id'] == proposal['standard_id']), None)
    
    return render_template('simple_proposal_detail.html', proposal=proposal, standard=standard)

# Enhancement generation route
@app.route('/generate-enhancement', methods=['GET', 'POST'])
def generate_enhancement():
    if request.method == 'POST':
        standard_id = request.form.get('standard_id')
        standard_text = request.form.get('standard_text')
        
        if not standard_id or not standard_text:
            flash('Please provide both standard ID and text', 'danger')
            return redirect(url_for('generate_enhancement'))
        
        try:
            # Generate enhancement using the actual enhancement generator
            enhancement_result = enhancement_generator.generate_enhancement(
                standard_id=standard_id,
                standard_text=standard_text,
                use_web_search=True
            )
            
            # Create a new proposal with the generated enhancement
            new_proposal = {
                "id": str(len(PROPOSALS) + 1),
                "standard_id": standard_id,
                "title": f"Enhancement to {next((s['name'] for s in STANDARDS if s['id'] == standard_id), 'Standard')} - AI Generated",
                "current_text": standard_text,
                "proposed_text": enhancement_result['enhanced_text'],
                "rationale": enhancement_result['rationale'],
                "status": "pending",
                "created_at": datetime.now().strftime("%Y-%m-%d"),
                "votes_up": 0,
                "votes_down": 0,
                "comments": [],
                "suggestions": [],
                "validation": {"is_valid": None, "reason": "Awaiting validation"}
            }
            
            # Add the new proposal to our mock data
            PROPOSALS.append(new_proposal)
            
            flash('Enhancement generated successfully!', 'success')
            return redirect(url_for('proposal_detail', proposal_id=new_proposal['id']))
            
        except Exception as e:
            flash(f'Error generating enhancement: {str(e)}', 'danger')
            return redirect(url_for('generate_enhancement'))
    
    # GET request - show the form
    return render_template('generate_enhancement.html', standards=STANDARDS)

# API routes for interaction (simplified, no authentication)
@app.route('/api/vote/<proposal_id>/<vote_type>', methods=['POST'])
def vote(proposal_id, vote_type):
    proposal = next((p for p in PROPOSALS if p['id'] == proposal_id), None)
    
    if not proposal:
        return {'success': False, 'message': 'Proposal not found'}, 404
    
    if vote_type == 'up':
        proposal['votes_up'] += 1
    elif vote_type == 'down':
        proposal['votes_down'] += 1
    
    return {'success': True, 'votes_up': proposal['votes_up'], 'votes_down': proposal['votes_down']}

@app.route('/api/comment/<proposal_id>', methods=['POST'])
def add_comment(proposal_id):
    proposal = next((p for p in PROPOSALS if p['id'] == proposal_id), None)
    
    if not proposal:
        return {'success': False, 'message': 'Proposal not found'}, 404
    
    comment_text = request.json.get('text', '')
    
    if not comment_text:
        return {'success': False, 'message': 'Comment text is required'}, 400
    
    new_comment = {
        'id': str(len(proposal['comments']) + 1),
        'user': 'Demo User',
        'text': comment_text,
        'created_at': datetime.now().strftime("%Y-%m-%d")
    }
    
    proposal['comments'].append(new_comment)
    
    return {'success': True, 'comment': new_comment}

@app.route('/api/suggestion/<proposal_id>', methods=['POST'])
def add_suggestion(proposal_id):
    proposal = next((p for p in PROPOSALS if p['id'] == proposal_id), None)
    
    if not proposal:
        return {'success': False, 'message': 'Proposal not found'}, 404
    
    suggestion_text = request.json.get('text', '')
    
    if not suggestion_text:
        return {'success': False, 'message': 'Suggestion text is required'}, 400
    
    new_suggestion = {
        'id': str(len(proposal['suggestions']) + 1),
        'user': 'Demo User',
        'text': suggestion_text,
        'created_at': datetime.now().strftime("%Y-%m-%d")
    }
    
    proposal['suggestions'].append(new_suggestion)
    
    return {'success': True, 'suggestion': new_suggestion}

if __name__ == '__main__':
    app.run(debug=True, port=5001)
