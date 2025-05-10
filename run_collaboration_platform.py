"""
Run the Islamic Finance Standards Enhancement Community Collaboration Platform

This script initializes and runs the Flask web application for the
community collaboration platform, allowing stakeholders to view, vote on,
and refine enhancement proposals.
"""

import os
import logging
from dotenv import load_dotenv

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Set Flask environment variables
os.environ['FLASK_APP'] = 'IslamicFinanceStandardsAI/frontend/app.py'
os.environ['FLASK_ENV'] = 'development'
os.environ['FLASK_DEBUG'] = '1'

# Set a secret key for Flask sessions if not already set
if 'FLASK_SECRET_KEY' not in os.environ:
    os.environ['FLASK_SECRET_KEY'] = 'dev_secret_key_change_in_production'

# Import the app after setting environment variables
from IslamicFinanceStandardsAI.frontend.app import app
from IslamicFinanceStandardsAI.database.knowledge_graph_extended import ExtendedKnowledgeGraph
from IslamicFinanceStandardsAI.models.user import User, UserRole

# Initialize the extended knowledge graph
knowledge_graph = ExtendedKnowledgeGraph()

# Create sample data for testing
def create_sample_data():
    """Create sample data for testing the platform"""
    from IslamicFinanceStandardsAI.models.enhancement_schema import EnhancementProposal, EnhancementStatus
    from datetime import datetime
    
    logger.info("Creating sample data for testing...")
    
    # Create sample enhancement proposals
    proposals = [
        {
            "title": "Clarification of Musharaka Profit Distribution",
            "standard_id": "FAS 4",
            "section": "3.2",
            "current_text": "Profits shall be distributed among partners according to the agreed ratio.",
            "proposed_text": "Profits shall be distributed among partners according to the agreed ratio, which must be explicitly stated in the Musharaka agreement. The profit-sharing ratio must be a percentage of the actual profit, not a lump sum or guaranteed amount.",
            "rationale": "The current text lacks specificity regarding the nature of profit distribution, which could lead to practices that violate Shariah principles such as guaranteeing returns or using predetermined fixed amounts.",
            "impact_analysis": "This clarification will ensure that Musharaka contracts adhere more strictly to Shariah principles of profit-and-loss sharing, reducing the risk of non-compliant structures.",
            "status": EnhancementStatus.PENDING.value,
            "timestamp": datetime.now().isoformat()
        },
        {
            "title": "Enhanced Disclosure Requirements for Diminishing Musharaka",
            "standard_id": "FAS 4",
            "section": "4.5",
            "current_text": "Institutions shall disclose the nature of Musharaka contracts in their financial statements.",
            "proposed_text": "Institutions shall disclose the nature of Musharaka contracts in their financial statements, including detailed information for Diminishing Musharaka arrangements. This disclosure must include: (a) the initial ownership ratio, (b) the schedule of ownership transfers, (c) the valuation methodology for ownership units, and (d) any rental or lease arrangements associated with the partner's use of the Musharaka asset.",
            "rationale": "Diminishing Musharaka structures are increasingly common in Islamic finance, particularly for home financing, but the current standard lacks specific disclosure requirements for these arrangements.",
            "impact_analysis": "Enhanced disclosure will improve transparency and comparability across institutions, helping stakeholders better understand the economic substance of Diminishing Musharaka arrangements.",
            "status": EnhancementStatus.APPROVED.value,
            "timestamp": datetime.now().isoformat()
        },
        {
            "title": "Clarification on Ijarah Rental Determination",
            "standard_id": "FAS 8",
            "section": "5.1",
            "current_text": "Rental must be determined at the time of contract for the entire period of the Ijarah.",
            "proposed_text": "Rental must be determined at the time of contract for the entire period of the Ijarah. For long-term Ijarah contracts, the rental amount may be adjusted periodically based on a clear formula or benchmark agreed upon by both parties at the time of the contract. Such adjustments must not be linked to interest rate benchmarks like LIBOR or EURIBOR.",
            "rationale": "The current standard does not adequately address the issue of rental adjustments in long-term Ijarah contracts, leading to practices that may indirectly link rentals to interest-based benchmarks.",
            "impact_analysis": "This clarification will provide a Shariah-compliant framework for rental adjustments in long-term Ijarah contracts, reducing reliance on interest-based benchmarks.",
            "status": EnhancementStatus.NEEDS_REVISION.value,
            "timestamp": datetime.now().isoformat()
        }
    ]
    
    # Store proposals in the knowledge graph
    proposal_ids = []
    for proposal_data in proposals:
        # Create proposal object
        proposal = EnhancementProposal(
            title=proposal_data["title"],
            standard_id=proposal_data["standard_id"],
            section=proposal_data["section"],
            current_text=proposal_data["current_text"],
            proposed_text=proposal_data["proposed_text"],
            rationale=proposal_data["rationale"],
            impact_analysis=proposal_data["impact_analysis"],
            status=EnhancementStatus(proposal_data["status"]),
            timestamp=datetime.now()
        )
        
        # Store in knowledge graph
        proposal_id = knowledge_graph.store_enhancement_proposal(proposal)
        if proposal_id:
            proposal_ids.append(proposal_id)
            logger.info(f"Created proposal: {proposal_data['title']} with ID: {proposal_id}")
    
    # Add some comments and votes
    if proposal_ids:
        # Add comments
        users = [
            {"id": "1", "name": "Admin User", "role": UserRole.ADMIN.value},
            {"id": "2", "name": "Scholar User", "role": UserRole.SCHOLAR.value},
            {"id": "3", "name": "Regulator User", "role": UserRole.REGULATOR.value},
            {"id": "4", "name": "Practitioner User", "role": UserRole.PRACTITIONER.value}
        ]
        
        comments = [
            "This enhancement provides much-needed clarity on profit distribution in Musharaka contracts.",
            "I suggest adding a reference to AAOIFI Shariah Standard 12 which covers Musharaka in detail.",
            "The proposed text aligns well with the principles of profit and loss sharing in Islamic finance.",
            "Consider adding examples to illustrate compliant and non-compliant profit distribution mechanisms."
        ]
        
        for i, proposal_id in enumerate(proposal_ids):
            # Add comments
            for j, user in enumerate(users):
                comment_text = comments[(i + j) % len(comments)]
                comment_id = knowledge_graph.add_comment(proposal_id, user["id"], comment_text)
                if comment_id:
                    logger.info(f"Added comment by {user['name']} to proposal {proposal_id}")
            
            # Add votes
            for j, user in enumerate(users):
                vote_type = "upvote" if j % 2 == 0 else "downvote"
                success = knowledge_graph.record_vote(proposal_id, user["id"], vote_type)
                if success:
                    logger.info(f"Added {vote_type} by {user['name']} to proposal {proposal_id}")
            
            # Add suggestions for the first proposal
            if i == 0:
                suggestions = [
                    "Consider adding a clause about dispute resolution mechanisms for profit calculation disagreements.",
                    "The standard should explicitly prohibit any guaranteed returns to any partner."
                ]
                
                for j, suggestion in enumerate(suggestions):
                    user = users[j % len(users)]
                    suggestion_id = knowledge_graph.add_suggestion(proposal_id, user["id"], suggestion)
                    if suggestion_id:
                        logger.info(f"Added suggestion by {user['name']} to proposal {proposal_id}")
    
    logger.info("Sample data creation completed")

# Update app configuration
def configure_app():
    """Configure the Flask application"""
    from flask import request, jsonify
    
    # Set the knowledge graph instance
    app.config['KNOWLEDGE_GRAPH'] = knowledge_graph
    
    # Set up routes to use the extended knowledge graph
    @app.context_processor
    def inject_global_variables():
        """Inject global variables into templates"""
        return {
            'top_proposals': knowledge_graph.get_top_proposals(limit=5),
            'recent_activities': knowledge_graph.get_recent_activity(limit=5)
        }
    
    # Override the get_all_enhancement_proposals route
    @app.route('/api/proposals', methods=['GET'])
    def api_get_proposals():
        """API endpoint to get proposals"""
        status = request.args.get('status')
        proposals = knowledge_graph.get_all_enhancement_proposals(status=status)
        return jsonify([p for p in proposals])

if __name__ == '__main__':
    try:
        # Create sample data
        create_sample_data()
        
        # Configure the app
        configure_app()
        
        # Run the app
        logger.info("Starting the Community Collaboration Platform...")
        app.run(host='0.0.0.0', port=5000, debug=True)
    except Exception as e:
        logger.error(f"Error starting the platform: {str(e)}")
    finally:
        # Close connections
        knowledge_graph.close()
