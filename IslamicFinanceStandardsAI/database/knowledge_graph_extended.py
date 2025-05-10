"""
Extended Knowledge Graph with Community Features

This module extends the base KnowledgeGraph class with community collaboration features
to support the Islamic Finance Standards Enhancement system's collaborative platform.
"""

from database.knowledge_graph import KnowledgeGraph
from database.community_features import CommunityFeatures

class ExtendedKnowledgeGraph(KnowledgeGraph, CommunityFeatures):
    """
    Extended Knowledge Graph with community collaboration features
    
    This class combines the base KnowledgeGraph functionality with
    community features like comments, votes, and suggestions.
    """
    
    def __init__(self):
        """Initialize the extended knowledge graph"""
        # Initialize the base KnowledgeGraph
        KnowledgeGraph.__init__(self)
        
        # No need to initialize CommunityFeatures as it's a mixin class
        
        # Ensure the necessary indexes exist
        self._ensure_indexes()
    
    def _ensure_indexes(self):
        """Ensure necessary indexes exist for community features"""
        try:
            # Create index on Comment nodes
            query_comment = """
            CREATE INDEX IF NOT EXISTS FOR (c:Comment) ON (c.proposal_id)
            """
            
            # Create index on Suggestion nodes
            query_suggestion = """
            CREATE INDEX IF NOT EXISTS FOR (s:Suggestion) ON (s.proposal_id)
            """
            
            # Create index on User nodes
            query_user = """
            CREATE INDEX IF NOT EXISTS FOR (u:User) ON (u.id)
            """
            
            # Create index on EnhancementProposal nodes for status
            query_proposal = """
            CREATE INDEX IF NOT EXISTS FOR (p:EnhancementProposal) ON (p.status)
            """
            
            with self.driver.session() as session:
                session.run(query_comment)
                session.run(query_suggestion)
                session.run(query_user)
                session.run(query_proposal)
                
                self.logger.info("Created indexes for community features")
                
        except Exception as e:
            self.logger.error(f"Error creating indexes: {str(e)}")
    
    def store_enhancement_proposal(self, proposal):
        """
        Store an enhancement proposal in the knowledge graph with community features
        
        Args:
            proposal: EnhancementProposal object
            
        Returns:
            ID of the stored proposal
        """
        # Call the parent method to store the basic proposal
        proposal_id = super().store_enhancement_proposal(proposal)
        
        if proposal_id:
            # Initialize vote counts
            try:
                query = """
                MATCH (p:EnhancementProposal)
                WHERE id(p) = $proposal_id
                SET p.upvotes = 0, p.downvotes = 0, p.vote_score = 0
                """
                
                with self.driver.session() as session:
                    session.run(query, proposal_id=int(proposal_id))
                    self.logger.info(f"Initialized vote counts for proposal {proposal_id}")
            except Exception as e:
                self.logger.error(f"Error initializing vote counts: {str(e)}")
        
        return proposal_id
    
    def get_top_proposals(self, limit=10):
        """
        Get top-rated enhancement proposals
        
        Args:
            limit: Maximum number of proposals to return
            
        Returns:
            List of enhancement proposal dictionaries sorted by vote score
        """
        try:
            query = """
            MATCH (p:EnhancementProposal)
            RETURN id(p) AS id, properties(p) AS properties,
                   p.upvotes AS upvotes, p.downvotes AS downvotes, p.vote_score AS vote_score
            ORDER BY p.vote_score DESC, p.timestamp DESC
            LIMIT $limit
            """
            
            with self.driver.session() as session:
                result = session.run(query, limit=limit)
                proposals = []
                
                for record in result:
                    proposal = {
                        "id": str(record["id"]),
                        "properties": record["properties"],
                        "votes": {
                            "upvotes": record["upvotes"] or 0,
                            "downvotes": record["downvotes"] or 0,
                            "score": record["vote_score"] or 0
                        }
                    }
                    
                    proposals.append(proposal)
                
                return proposals
                
        except Exception as e:
            self.logger.error(f"Error getting top proposals: {str(e)}")
            return []
    
    def get_recent_activity(self, limit=20):
        """
        Get recent activity on enhancement proposals
        
        Args:
            limit: Maximum number of activities to return
            
        Returns:
            List of activity dictionaries
        """
        try:
            query = """
            MATCH (n)
            WHERE (n:Comment OR n:Suggestion OR n:ValidationResult)
            RETURN id(n) AS id, labels(n) AS labels, properties(n) AS properties,
                   n.timestamp AS timestamp
            ORDER BY n.timestamp DESC
            LIMIT $limit
            """
            
            with self.driver.session() as session:
                result = session.run(query, limit=limit)
                activities = []
                
                for record in result:
                    activity_type = record["labels"][0] if record["labels"] else "Unknown"
                    
                    activity = {
                        "id": str(record["id"]),
                        "type": activity_type,
                        "timestamp": record["timestamp"],
                        "properties": record["properties"]
                    }
                    
                    # Add user information if available
                    if "user_id" in record["properties"]:
                        from models.user import User
                        user = User.get_by_id(record["properties"]["user_id"])
                        if user:
                            activity["user"] = {
                                "name": user.name,
                                "role": user.role.value
                            }
                    
                    activities.append(activity)
                
                return activities
                
        except Exception as e:
            self.logger.error(f"Error getting recent activity: {str(e)}")
            return []
    
    def get_user_activity(self, user_id, limit=20):
        """
        Get activity by a specific user
        
        Args:
            user_id: ID of the user
            limit: Maximum number of activities to return
            
        Returns:
            List of activity dictionaries
        """
        try:
            query = """
            MATCH (n)
            WHERE (n:Comment OR n:Suggestion) AND n.user_id = $user_id
            RETURN id(n) AS id, labels(n) AS labels, properties(n) AS properties,
                   n.timestamp AS timestamp
            ORDER BY n.timestamp DESC
            LIMIT $limit
            """
            
            with self.driver.session() as session:
                result = session.run(query, user_id=user_id, limit=limit)
                activities = []
                
                for record in result:
                    activity_type = record["labels"][0] if record["labels"] else "Unknown"
                    
                    activity = {
                        "id": str(record["id"]),
                        "type": activity_type,
                        "timestamp": record["timestamp"],
                        "properties": record["properties"]
                    }
                    
                    # Get proposal information
                    if "proposal_id" in record["properties"]:
                        proposal_id = record["properties"]["proposal_id"]
                        proposal = self.get_node_by_id(proposal_id)
                        if proposal:
                            activity["proposal"] = {
                                "id": proposal_id,
                                "title": proposal["properties"].get("title", "Unknown Proposal")
                            }
                    
                    activities.append(activity)
                
                return activities
                
        except Exception as e:
            self.logger.error(f"Error getting user activity: {str(e)}")
            return []
    
    def search_proposals(self, query_text, limit=10):
        """
        Search for enhancement proposals by text
        
        Args:
            query_text: Text to search for
            limit: Maximum number of proposals to return
            
        Returns:
            List of matching enhancement proposal dictionaries
        """
        try:
            # Simple text search (in a production system, use full-text search capabilities)
            query = """
            MATCH (p:EnhancementProposal)
            WHERE p.title CONTAINS $query_text OR 
                  p.current_text CONTAINS $query_text OR 
                  p.proposed_text CONTAINS $query_text OR
                  p.rationale CONTAINS $query_text
            RETURN id(p) AS id, properties(p) AS properties,
                   p.upvotes AS upvotes, p.downvotes AS downvotes, p.vote_score AS vote_score
            ORDER BY p.vote_score DESC
            LIMIT $limit
            """
            
            with self.driver.session() as session:
                result = session.run(query, query_text=query_text, limit=limit)
                proposals = []
                
                for record in result:
                    proposal = {
                        "id": str(record["id"]),
                        "properties": record["properties"],
                        "votes": {
                            "upvotes": record["upvotes"] or 0,
                            "downvotes": record["downvotes"] or 0,
                            "score": record["vote_score"] or 0
                        }
                    }
                    
                    proposals.append(proposal)
                
                return proposals
                
        except Exception as e:
            self.logger.error(f"Error searching proposals: {str(e)}")
            return []
