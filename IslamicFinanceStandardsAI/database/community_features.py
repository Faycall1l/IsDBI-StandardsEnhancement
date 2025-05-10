"""
Community Collaboration Features for Knowledge Graph

This module extends the KnowledgeGraph class with methods to support:
1. Comments on enhancement proposals
2. Voting/ranking of proposals
3. Suggestions for improvements
4. User interactions tracking
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
from uuid import uuid4

class CommunityFeatures:
    """Mixin class for community collaboration features"""
    
    def add_comment(self, proposal_id: str, user_id: str, comment_text: str) -> str:
        """
        Add a comment to an enhancement proposal
        
        Args:
            proposal_id: ID of the enhancement proposal
            user_id: ID of the user making the comment
            comment_text: Text of the comment
            
        Returns:
            ID of the created comment, or None if failed
        """
        try:
            # Create comment node
            comment_properties = {
                "text": comment_text,
                "user_id": user_id,
                "timestamp": datetime.now().isoformat(),
                "proposal_id": proposal_id
            }
            
            comment_id = self.create_node("Comment", comment_properties)
            
            if not comment_id:
                self.logger.error("Failed to create comment node")
                return None
            
            # Create relationship to proposal
            relationship = self.create_relationship(
                comment_id, 
                proposal_id, 
                "COMMENTS_ON", 
                {"timestamp": datetime.now().isoformat()}
            )
            
            if not relationship:
                self.logger.error("Failed to create comment relationship")
                self.delete_node(comment_id)
                return None
            
            self.logger.info(f"Added comment {comment_id} to proposal {proposal_id}")
            return comment_id
            
        except Exception as e:
            self.logger.error(f"Error adding comment: {str(e)}")
            return None
    
    def get_comments_for_proposal(self, proposal_id: str) -> List[Dict[str, Any]]:
        """
        Get all comments for an enhancement proposal
        
        Args:
            proposal_id: ID of the enhancement proposal
            
        Returns:
            List of comment dictionaries with user information
        """
        try:
            query = """
            MATCH (c:Comment)-[:COMMENTS_ON]->(p)
            WHERE id(p) = $proposal_id
            RETURN id(c) AS id, c.text AS text, c.user_id AS user_id, 
                   c.timestamp AS timestamp, properties(c) AS properties
            ORDER BY c.timestamp DESC
            """
            
            with self.driver.session() as session:
                result = session.run(query, proposal_id=int(proposal_id))
                comments = []
                
                for record in result:
                    comment = {
                        "id": str(record["id"]),
                        "text": record["text"],
                        "user_id": record["user_id"],
                        "timestamp": record["timestamp"],
                        "properties": record["properties"]
                    }
                    
                    # Add user information if available
                    from models.user import User
                    user = User.get_by_id(record["user_id"])
                    if user:
                        comment["user"] = {
                            "name": user.name,
                            "role": user.role.value
                        }
                    
                    comments.append(comment)
                
                return comments
                
        except Exception as e:
            self.logger.error(f"Error getting comments: {str(e)}")
            return []
    
    def record_vote(self, proposal_id: str, user_id: str, vote_type: str) -> bool:
        """
        Record a vote on an enhancement proposal
        
        Args:
            proposal_id: ID of the enhancement proposal
            user_id: ID of the user voting
            vote_type: Type of vote ('upvote' or 'downvote')
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Check if user has already voted
            query = """
            MATCH (u)-[r:VOTED_ON]->(p)
            WHERE id(p) = $proposal_id AND r.user_id = $user_id
            RETURN r
            """
            
            with self.driver.session() as session:
                result = session.run(query, proposal_id=int(proposal_id), user_id=user_id)
                existing_vote = result.single()
                
                if existing_vote:
                    # Update existing vote
                    update_query = """
                    MATCH (u)-[r:VOTED_ON]->(p)
                    WHERE id(p) = $proposal_id AND r.user_id = $user_id
                    SET r.vote_type = $vote_type, r.timestamp = $timestamp
                    RETURN r
                    """
                    
                    result = session.run(
                        update_query, 
                        proposal_id=int(proposal_id), 
                        user_id=user_id,
                        vote_type=vote_type,
                        timestamp=datetime.now().isoformat()
                    )
                    
                    self.logger.info(f"Updated vote for user {user_id} on proposal {proposal_id}")
                    
                else:
                    # Create new vote relationship
                    # First, get the user node
                    user_node_id = None
                    user_query = """
                    MATCH (u:User {id: $user_id})
                    RETURN id(u) AS user_node_id
                    """
                    
                    user_result = session.run(user_query, user_id=user_id)
                    user_record = user_result.single()
                    
                    if user_record:
                        user_node_id = str(user_record["user_node_id"])
                    else:
                        # Create user node if it doesn't exist
                        from models.user import User
                        user = User.get_by_id(user_id)
                        if not user:
                            self.logger.error(f"User {user_id} not found")
                            return False
                        
                        user_properties = {
                            "id": user_id,
                            "name": user.name,
                            "email": user.email,
                            "role": user.role.value
                        }
                        
                        user_node_id = self.create_node("User", user_properties)
                    
                    if not user_node_id:
                        self.logger.error("Failed to get or create user node")
                        return False
                    
                    # Create vote relationship
                    vote_properties = {
                        "user_id": user_id,
                        "vote_type": vote_type,
                        "timestamp": datetime.now().isoformat()
                    }
                    
                    relationship = self.create_relationship(
                        user_node_id,
                        proposal_id,
                        "VOTED_ON",
                        vote_properties
                    )
                    
                    if not relationship:
                        self.logger.error("Failed to create vote relationship")
                        return False
                    
                    self.logger.info(f"Recorded vote for user {user_id} on proposal {proposal_id}")
            
            # Update vote count on proposal
            self.update_vote_count(proposal_id)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error recording vote: {str(e)}")
            return False
    
    def update_vote_count(self, proposal_id: str) -> bool:
        """
        Update the vote count on an enhancement proposal
        
        Args:
            proposal_id: ID of the enhancement proposal
            
        Returns:
            True if successful, False otherwise
        """
        try:
            query = """
            MATCH (p)
            WHERE id(p) = $proposal_id
            
            OPTIONAL MATCH (u)-[r:VOTED_ON]->(p)
            WITH p, 
                 sum(CASE WHEN r.vote_type = 'upvote' THEN 1 ELSE 0 END) AS upvotes,
                 sum(CASE WHEN r.vote_type = 'downvote' THEN 1 ELSE 0 END) AS downvotes
            
            SET p.upvotes = upvotes,
                p.downvotes = downvotes,
                p.vote_score = upvotes - downvotes
                
            RETURN p.upvotes AS upvotes, p.downvotes AS downvotes, p.vote_score AS vote_score
            """
            
            with self.driver.session() as session:
                result = session.run(query, proposal_id=int(proposal_id))
                record = result.single()
                
                if record:
                    self.logger.info(f"Updated vote count for proposal {proposal_id}: "
                                    f"upvotes={record['upvotes']}, downvotes={record['downvotes']}, "
                                    f"score={record['vote_score']}")
                    return True
                
                return False
                
        except Exception as e:
            self.logger.error(f"Error updating vote count: {str(e)}")
            return False
    
    def get_vote_count(self, proposal_id: str) -> Dict[str, int]:
        """
        Get the vote count for an enhancement proposal
        
        Args:
            proposal_id: ID of the enhancement proposal
            
        Returns:
            Dictionary with upvotes, downvotes, and score
        """
        try:
            query = """
            MATCH (p)
            WHERE id(p) = $proposal_id
            RETURN p.upvotes AS upvotes, p.downvotes AS downvotes, p.vote_score AS vote_score
            """
            
            with self.driver.session() as session:
                result = session.run(query, proposal_id=int(proposal_id))
                record = result.single()
                
                if record:
                    return {
                        "upvotes": record["upvotes"] or 0,
                        "downvotes": record["downvotes"] or 0,
                        "score": record["vote_score"] or 0
                    }
                
                return {"upvotes": 0, "downvotes": 0, "score": 0}
                
        except Exception as e:
            self.logger.error(f"Error getting vote count: {str(e)}")
            return {"upvotes": 0, "downvotes": 0, "score": 0}
    
    def add_suggestion(self, proposal_id: str, user_id: str, suggestion_text: str) -> str:
        """
        Add a suggestion for improvement to an enhancement proposal
        
        Args:
            proposal_id: ID of the enhancement proposal
            user_id: ID of the user making the suggestion
            suggestion_text: Text of the suggestion
            
        Returns:
            ID of the created suggestion, or None if failed
        """
        try:
            # Create suggestion node
            suggestion_properties = {
                "text": suggestion_text,
                "user_id": user_id,
                "timestamp": datetime.now().isoformat(),
                "proposal_id": proposal_id,
                "status": "pending"  # pending, accepted, rejected
            }
            
            suggestion_id = self.create_node("Suggestion", suggestion_properties)
            
            if not suggestion_id:
                self.logger.error("Failed to create suggestion node")
                return None
            
            # Create relationship to proposal
            relationship = self.create_relationship(
                suggestion_id, 
                proposal_id, 
                "SUGGESTS_FOR", 
                {"timestamp": datetime.now().isoformat()}
            )
            
            if not relationship:
                self.logger.error("Failed to create suggestion relationship")
                self.delete_node(suggestion_id)
                return None
            
            self.logger.info(f"Added suggestion {suggestion_id} to proposal {proposal_id}")
            return suggestion_id
            
        except Exception as e:
            self.logger.error(f"Error adding suggestion: {str(e)}")
            return None
    
    def get_suggestions_for_proposal(self, proposal_id: str) -> List[Dict[str, Any]]:
        """
        Get all suggestions for an enhancement proposal
        
        Args:
            proposal_id: ID of the enhancement proposal
            
        Returns:
            List of suggestion dictionaries with user information
        """
        try:
            query = """
            MATCH (s:Suggestion)-[:SUGGESTS_FOR]->(p)
            WHERE id(p) = $proposal_id
            RETURN id(s) AS id, s.text AS text, s.user_id AS user_id, 
                   s.timestamp AS timestamp, s.status AS status, properties(s) AS properties
            ORDER BY s.timestamp DESC
            """
            
            with self.driver.session() as session:
                result = session.run(query, proposal_id=int(proposal_id))
                suggestions = []
                
                for record in result:
                    suggestion = {
                        "id": str(record["id"]),
                        "text": record["text"],
                        "user_id": record["user_id"],
                        "timestamp": record["timestamp"],
                        "status": record["status"],
                        "properties": record["properties"]
                    }
                    
                    # Add user information if available
                    from models.user import User
                    user = User.get_by_id(record["user_id"])
                    if user:
                        suggestion["user"] = {
                            "name": user.name,
                            "role": user.role.value
                        }
                    
                    suggestions.append(suggestion)
                
                return suggestions
                
        except Exception as e:
            self.logger.error(f"Error getting suggestions: {str(e)}")
            return []
    
    def update_suggestion_status(self, suggestion_id: str, status: str) -> bool:
        """
        Update the status of a suggestion
        
        Args:
            suggestion_id: ID of the suggestion
            status: New status ('pending', 'accepted', 'rejected')
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if status not in ['pending', 'accepted', 'rejected']:
                self.logger.error(f"Invalid suggestion status: {status}")
                return False
            
            query = """
            MATCH (s:Suggestion)
            WHERE id(s) = $suggestion_id
            SET s.status = $status, s.updated_at = $timestamp
            RETURN s
            """
            
            with self.driver.session() as session:
                result = session.run(
                    query, 
                    suggestion_id=int(suggestion_id),
                    status=status,
                    timestamp=datetime.now().isoformat()
                )
                
                record = result.single()
                
                if record:
                    self.logger.info(f"Updated suggestion {suggestion_id} status to {status}")
                    return True
                
                return False
                
        except Exception as e:
            self.logger.error(f"Error updating suggestion status: {str(e)}")
            return False
    
    def get_all_enhancement_proposals(self, status: str = None, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get all enhancement proposals, optionally filtered by status
        
        Args:
            status: Optional status filter
            limit: Maximum number of proposals to return
            
        Returns:
            List of enhancement proposal dictionaries with vote counts
        """
        try:
            # Build query based on whether status filter is provided
            if status:
                query = """
                MATCH (p:EnhancementProposal)
                WHERE p.status = $status
                RETURN id(p) AS id, properties(p) AS properties,
                       p.upvotes AS upvotes, p.downvotes AS downvotes, p.vote_score AS vote_score
                ORDER BY p.timestamp DESC
                LIMIT $limit
                """
                params = {"status": status, "limit": limit}
            else:
                query = """
                MATCH (p:EnhancementProposal)
                RETURN id(p) AS id, properties(p) AS properties,
                       p.upvotes AS upvotes, p.downvotes AS downvotes, p.vote_score AS vote_score
                ORDER BY p.timestamp DESC
                LIMIT $limit
                """
                params = {"limit": limit}
            
            with self.driver.session() as session:
                result = session.run(query, **params)
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
            self.logger.error(f"Error getting enhancement proposals: {str(e)}")
            return []
    
    def get_enhancement_proposal(self, proposal_id: str) -> Dict[str, Any]:
        """
        Get an enhancement proposal by ID
        
        Args:
            proposal_id: ID of the enhancement proposal
            
        Returns:
            Enhancement proposal dictionary with vote counts and related information
        """
        try:
            query = """
            MATCH (p:EnhancementProposal)
            WHERE id(p) = $proposal_id
            RETURN id(p) AS id, properties(p) AS properties,
                   p.upvotes AS upvotes, p.downvotes AS downvotes, p.vote_score AS vote_score
            """
            
            with self.driver.session() as session:
                result = session.run(query, proposal_id=int(proposal_id))
                record = result.single()
                
                if record:
                    proposal = {
                        "id": str(record["id"]),
                        "properties": record["properties"],
                        "votes": {
                            "upvotes": record["upvotes"] or 0,
                            "downvotes": record["downvotes"] or 0,
                            "score": record["vote_score"] or 0
                        }
                    }
                    
                    # Get comments
                    proposal["comments"] = self.get_comments_for_proposal(proposal_id)
                    
                    # Get suggestions
                    proposal["suggestions"] = self.get_suggestions_for_proposal(proposal_id)
                    
                    # Get validation results
                    proposal["validation_results"] = self.get_validation_results_for_proposal(proposal_id)
                    
                    return proposal
                
                return None
                
        except Exception as e:
            self.logger.error(f"Error getting enhancement proposal: {str(e)}")
            return None
    
    def update_proposal_status(self, proposal_id: str, status: str) -> bool:
        """
        Update the status of an enhancement proposal
        
        Args:
            proposal_id: ID of the enhancement proposal
            status: New status
            
        Returns:
            True if successful, False otherwise
        """
        try:
            from models.enhancement_schema import EnhancementStatus
            
            # Validate status
            valid_statuses = [s.value for s in EnhancementStatus]
            if status not in valid_statuses:
                self.logger.error(f"Invalid proposal status: {status}")
                return False
            
            query = """
            MATCH (p:EnhancementProposal)
            WHERE id(p) = $proposal_id
            SET p.status = $status, p.updated_at = $timestamp
            RETURN p
            """
            
            with self.driver.session() as session:
                result = session.run(
                    query, 
                    proposal_id=int(proposal_id),
                    status=status,
                    timestamp=datetime.now().isoformat()
                )
                
                record = result.single()
                
                if record:
                    self.logger.info(f"Updated proposal {proposal_id} status to {status}")
                    return True
                
                return False
                
        except Exception as e:
            self.logger.error(f"Error updating proposal status: {str(e)}")
            return False
    
    def get_validation_results_for_proposal(self, proposal_id: str) -> List[Dict[str, Any]]:
        """
        Get all validation results for an enhancement proposal
        
        Args:
            proposal_id: ID of the enhancement proposal
            
        Returns:
            List of validation result dictionaries
        """
        try:
            query = """
            MATCH (v:ValidationResult)-[:VALIDATES]->(p:EnhancementProposal)
            WHERE id(p) = $proposal_id
            RETURN id(v) AS id, properties(v) AS properties
            ORDER BY v.timestamp DESC
            """
            
            with self.driver.session() as session:
                result = session.run(query, proposal_id=int(proposal_id))
                validation_results = []
                
                for record in result:
                    validation_result = {
                        "id": str(record["id"]),
                        "properties": record["properties"]
                    }
                    
                    validation_results.append(validation_result)
                
                return validation_results
                
        except Exception as e:
            self.logger.error(f"Error getting validation results: {str(e)}")
            return []
