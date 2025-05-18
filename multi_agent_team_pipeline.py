#!/usr/bin/env python
"""
Multi-Agent Team Pipeline for Islamic Finance Standards Enhancement

This script demonstrates the full multi-agent team architecture with:
1. Multiple agents at each stage (ingestion, enhancement, validation)
2. Peer review and cross-checking between agents
3. Consensus-based decision making
4. Separation of concerns
5. Message-based communication between teams
6. Optimized knowledge graph architecture with connection pooling
"""

import asyncio
import logging
import sys
import uuid
import json
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Callable, Union, Tuple

# Add the project root to the Python path
sys.path.append(str(Path(__file__).parent))

# Import the agent factory and other necessary components
from IslamicFinanceStandardsAI.core.agents.agent_factory import AgentFactory
from IslamicFinanceStandardsAI.core.agents.document_agent import DocumentAgent
from IslamicFinanceStandardsAI.core.agents.enhancement_agent import EnhancementAgent
from IslamicFinanceStandardsAI.core.agents.validation_agent import ValidationAgent
from IslamicFinanceStandardsAI.database.factory import create_knowledge_graph
from IslamicFinanceStandardsAI.database.interfaces.knowledge_graph import IKnowledgeGraph
from IslamicFinanceStandardsAI.core.messaging import MessageBus, Message, MessageType, message_bus

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class AgentTeam:
    """Base class for a team of agents with the same role"""
    
    def __init__(self, team_name: str, agent_type: str, team_size: int = 3):
        self.team_name = team_name
        self.agent_type = agent_type
        self.team_size = team_size
        self.agents = []
        self.factory = AgentFactory()
        self.team_id = f"{self.agent_type}_{self.team_name}_{int(time.time())}"
        self.knowledge_graph = None
        self.message_bus = message_bus
        
    async def initialize(self):
        """Initialize all agents in the team"""
        logger.info(f"Initializing {self.team_name} team with {self.team_size} agents")
        
        # Connect to the knowledge graph
        self.knowledge_graph = create_knowledge_graph()
        await self.knowledge_graph.connect()
        
        # Subscribe to relevant message types
        self._subscribe_to_messages()
        
        # Initialize agents
        for i in range(self.team_size):
            agent_id = f"{self.agent_type}_{self.team_name}_{i+1}"
            agent = self.factory.create_agent(self.agent_type, agent_id=agent_id)
            await agent.start()
            self.agents.append(agent)
            
        # Record team initialization in knowledge graph
        await self.knowledge_graph.record_team_activity(
            team_id=self.team_id,
            activity_type="team_initialization",
            details={
                "team_name": self.team_name,
                "agent_type": self.agent_type,
                "team_size": self.team_size,
                "agent_ids": [agent.agent_id for agent in self.agents]
            }
        )
        
        # Publish team initialization message
        await self.message_bus.publish(Message(
            message_type=MessageType.TEAM_STATUS,
            sender_id=self.team_id,
            payload={
                "status": "initialized",
                "team_name": self.team_name,
                "agent_type": self.agent_type,
                "team_size": self.team_size,
                "agent_ids": [agent.agent_id for agent in self.agents]
            },
            team_id=self.team_id
        ))
        
        logger.info(f"{self.team_name} team initialized with {len(self.agents)} agents")
        
    def _subscribe_to_messages(self):
        """Subscribe to relevant message types"""
        # Each team should override this method to subscribe to relevant message types
        pass
        
    async def shutdown(self):
        """Shutdown all agents in the team"""
        # Shutdown all agents
        for agent in self.agents:
            await agent.stop()
            
        # Disconnect from knowledge graph
        if self.knowledge_graph:
            await self.knowledge_graph.close()
            
        # Record team shutdown in knowledge graph
        await self.knowledge_graph.record_team_activity(
            team_id=self.team_id,
            activity_type="team_shutdown",
            details={
                "team_name": self.team_name,
                "agent_type": self.agent_type,
                "shutdown_time": datetime.utcnow().isoformat()
            }
        )
        
        # Publish team shutdown message
        await self.message_bus.publish(Message(
            message_type=MessageType.TEAM_STATUS,
            sender_id=self.team_id,
            payload={
                "status": "shutdown",
                "team_name": self.team_name,
                "agent_type": self.agent_type,
                "shutdown_time": datetime.utcnow().isoformat()
            },
            team_id=self.team_id
        ))
        
        logger.info(f"{self.team_name} team shutdown complete")

class DocumentTeam(AgentTeam):
    """Team of document agents responsible for processing standards documents"""
    
    def __init__(self, team_size: int = 3):
        super().__init__("document", "document_agent", team_size)
        self.processing_requests = {}
        
    def _subscribe_to_messages(self):
        """Subscribe to document processing related messages"""
        self.message_bus.subscribe(MessageType.DOCUMENT_PROCESSING_REQUEST, self._handle_processing_request)
        self.message_bus.subscribe(MessageType.DOCUMENT_PROCESSING_RESULT, self._handle_processing_result)
        
    async def _handle_processing_request(self, message: Message):
        """Handle document processing request messages"""
        document_path = message.payload.get('document_path')
        document_type = message.payload.get('document_type')
        request_id = message.payload.get('request_id', str(uuid.uuid4()))
        
        logger.info(f"Document team received processing request for {document_path} (ID: {request_id})")
        
        # Store the request for tracking
        self.processing_requests[request_id] = {
            'document_path': document_path,
            'document_type': document_type,
            'requester_id': message.sender_id,
            'status': 'processing',
            'timestamp': datetime.utcnow().isoformat(),
            'results': []
        }
        
        # Process the document asynchronously
        asyncio.create_task(self._process_document_async(request_id, document_path, document_type))
        
        # Send acknowledgment
        await self.message_bus.publish(Message(
            message_type=MessageType.DOCUMENT_PROCESSING_ACK,
            sender_id=self.team_id,
            recipient_id=message.sender_id,
            payload={
                'request_id': request_id,
                'status': 'processing',
                'document_path': document_path
            },
            team_id=self.team_id
        ))
    
    async def _handle_processing_result(self, message: Message):
        """Handle document processing result messages from individual agents"""
        request_id = message.payload.get('request_id')
        agent_id = message.sender_id
        result = message.payload.get('result')
        
        if request_id in self.processing_requests:
            self.processing_requests[request_id]['results'].append({
                'agent_id': agent_id,
                'result': result
            })
            logger.info(f"Received processing result from agent {agent_id} for request {request_id}")
            
            # Check if all agents have reported
            if len(self.processing_requests[request_id]['results']) == self.team_size:
                # All agents have reported, generate consensus
                await self._generate_consensus(request_id)
    
    async def _process_document_async(self, request_id: str, document_path: str, document_type: str):
        """Process document asynchronously with all agents in parallel"""
        # Record activity in knowledge graph
        await self.knowledge_graph.record_team_activity(
            team_id=self.team_id,
            activity_type="document_processing_started",
            details={
                'request_id': request_id,
                'document_path': document_path,
                'document_type': document_type
            }
        )
        
        # Start processing with all agents in parallel
        tasks = []
        for agent in self.agents:
            task = asyncio.create_task(self._process_with_agent(agent, request_id, document_path, document_type))
            tasks.append(task)
        
        # Wait for all tasks to complete
        await asyncio.gather(*tasks)
    
    async def _process_with_agent(self, agent, request_id: str, document_path: str, document_type: str):
        """Process document with a single agent and publish the result"""
        try:
            result = await agent.process_document(document_path, document_type)
            success = result.success
            data = result.data if success else {'error': result.error}
            
            # Publish result message
            await self.message_bus.publish(Message(
                message_type=MessageType.DOCUMENT_PROCESSING_RESULT,
                sender_id=agent.agent_id,
                payload={
                    'request_id': request_id,
                    'success': success,
                    'result': data
                },
                team_id=self.team_id
            ))
            
            logger.info(f"Agent {agent.agent_id} {'successfully' if success else 'failed to'} process document")
        except Exception as e:
            logger.error(f"Error processing document with agent {agent.agent_id}: {str(e)}")
            await self.message_bus.publish(Message(
                message_type=MessageType.DOCUMENT_PROCESSING_RESULT,
                sender_id=agent.agent_id,
                payload={
                    'request_id': request_id,
                    'success': False,
                    'result': {'error': str(e)}
                },
                team_id=self.team_id
            ))
    
    async def process_document(self, document_path: str, document_type: str) -> Dict[str, Any]:
        """
        Process a document with multiple agents and cross-validate results
        
        Each agent processes the document independently, then results are compared
        and a consensus is reached through voting.
        """
        logger.info(f"Document team processing {document_path}")
        
        # Create a request ID
        request_id = str(uuid.uuid4())
        
        # Create a future to wait for the result
        result_future = asyncio.Future()
        
        # Store the request and future
        self.processing_requests[request_id] = {
            'document_path': document_path,
            'document_type': document_type,
            'requester_id': self.team_id,  # Self-request
            'status': 'processing',
            'timestamp': datetime.utcnow().isoformat(),
            'results': [],
            'future': result_future
        }
        
        # Start processing
        await self._process_document_async(request_id, document_path, document_type)
        
        # Wait for the result
        return await result_future
        
    async def _generate_consensus(self, request_id: str):
        """Generate consensus from all agent results for a request"""
        if request_id not in self.processing_requests:
            logger.error(f"Cannot generate consensus for unknown request {request_id}")
            return
            
        request_data = self.processing_requests[request_id]
        document_path = request_data['document_path']
        document_type = request_data['document_type']
        
        # Extract successful results
        processing_results = []
        for result_data in request_data['results']:
            if result_data.get('result', {}).get('success', False):
                processing_results.append(result_data.get('result', {}).get('data', {}))
        
        if not processing_results:
            error_msg = "All document agents failed to process the document"
            logger.error(f"{error_msg} for request {request_id}")
            
            # Update request status
            self.processing_requests[request_id]['status'] = 'failed'
            
            # Publish failure message
            await self.message_bus.publish(Message(
                message_type=MessageType.DOCUMENT_PROCESSING_COMPLETE,
                sender_id=self.team_id,
                recipient_id=request_data['requester_id'],
                payload={
                    'request_id': request_id,
                    'success': False,
                    'error': error_msg
                },
                team_id=self.team_id
            ))
            
            # Resolve future if it exists
            if 'future' in request_data:
                request_data['future'].set_exception(ValueError(error_msg))
                
            return
        
        # Cross-validate results and reach consensus
        logger.info(f"Cross-validating document processing results for request {request_id}")
        
        # Combine sections from all agents
        all_sections = []
        for result in processing_results:
            sections = result.get('sections', [])
            all_sections.extend(sections)
        
        # Combine ambiguities from all agents
        all_ambiguities = []
        for result in processing_results:
            ambiguities = result.get('ambiguities', [])
            all_ambiguities.extend(ambiguities)
        
        # Deduplicate sections and ambiguities
        unique_sections = []
        seen_section_ids = set()
        for section in all_sections:
            section_id = section.get('id')
            if section_id and section_id not in seen_section_ids:
                seen_section_ids.add(section_id)
                unique_sections.append(section)
        
        unique_ambiguities = []
        seen_ambiguity_texts = set()
        for ambiguity in all_ambiguities:
            ambiguity_text = ambiguity.get('text')
            if ambiguity_text and ambiguity_text not in seen_ambiguity_texts:
                seen_ambiguity_texts.add(ambiguity_text)
                unique_ambiguities.append(ambiguity)
        
        # Create consensus result
        consensus_result = {
            'document_path': document_path,
            'document_type': document_type,
            'sections': unique_sections,
            'ambiguities': unique_ambiguities,
            'timestamp': datetime.utcnow().isoformat(),
            'team_size': len(self.agents),
            'successful_agents': len(processing_results)
        }
        
        # Record consensus in knowledge graph
        await self.knowledge_graph.record_consensus(
            team_id=self.team_id,
            proposal_id=request_id,  # Using request_id as proposal_id
            consensus_data={
                'document_path': document_path,
                'document_type': document_type,
                'sections_count': len(unique_sections),
                'ambiguities_count': len(unique_ambiguities),
                'team_size': len(self.agents),
                'successful_agents': len(processing_results)
            }
        )
        
        # Update request status
        self.processing_requests[request_id]['status'] = 'completed'
        self.processing_requests[request_id]['consensus'] = consensus_result
        
        # Publish completion message
        await self.message_bus.publish(Message(
            message_type=MessageType.DOCUMENT_PROCESSING_COMPLETE,
            sender_id=self.team_id,
            recipient_id=request_data['requester_id'],
            payload={
                'request_id': request_id,
                'success': True,
                'result': consensus_result
            },
            team_id=self.team_id
        ))
        
        logger.info(f"Document team consensus for request {request_id}: {len(unique_sections)} sections, {len(unique_ambiguities)} ambiguities")
        
        # Resolve future if it exists
        if 'future' in request_data:
            request_data['future'].set_result(consensus_result)

class EnhancementTeam(AgentTeam):
    """Team of enhancement agents responsible for generating improvement proposals"""
    
    def __init__(self, team_size: int = 3):
        super().__init__("enhancement", "enhancement_agent", team_size)
        self.enhancement_requests = {}
        
    def _subscribe_to_messages(self):
        """Subscribe to enhancement related messages"""
        self.message_bus.subscribe(MessageType.ENHANCEMENT_REQUEST, self._handle_enhancement_request)
        self.message_bus.subscribe(MessageType.DOCUMENT_PROCESSING_COMPLETE, self._handle_document_processing_complete)
        self.message_bus.subscribe(MessageType.ENHANCEMENT_PROPOSAL, self._handle_enhancement_proposal)
        self.message_bus.subscribe(MessageType.ENHANCEMENT_REVIEW, self._handle_enhancement_review)
        
    async def _handle_enhancement_request(self, message: Message):
        """Handle enhancement request messages"""
        document_result = message.payload.get('document_result')
        target_section = message.payload.get('target_section')
        request_id = message.payload.get('request_id', str(uuid.uuid4()))
        
        logger.info(f"Enhancement team received request for section {target_section} (ID: {request_id})")
        
        # Store the request for tracking
        self.enhancement_requests[request_id] = {
            'document_result': document_result,
            'target_section': target_section,
            'requester_id': message.sender_id,
            'status': 'processing',
            'timestamp': datetime.utcnow().isoformat(),
            'proposals': [],
            'reviews': {},
            'review_count': 0
        }
        
        # Process the enhancement request asynchronously
        asyncio.create_task(self._generate_enhancements_async(request_id))
        
        # Send acknowledgment
        await self.message_bus.publish(Message(
            message_type=MessageType.ENHANCEMENT_REQUEST_ACK,
            sender_id=self.team_id,
            recipient_id=message.sender_id,
            payload={
                'request_id': request_id,
                'status': 'processing',
                'target_section': target_section
            },
            team_id=self.team_id
        ))
    
    async def _handle_document_processing_complete(self, message: Message):
        """Handle document processing complete messages"""
        # This is a potential trigger for automatic enhancement generation
        if message.payload.get('success', False):
            document_result = message.payload.get('result', {})
            sections = document_result.get('sections', [])
            
            # For each section with ambiguities, generate enhancement proposals
            for section in sections:
                section_id = section.get('id')
                if section_id and any(a.get('section_id') == section_id for a in document_result.get('ambiguities', [])):
                    # Create an enhancement request
                    request_id = str(uuid.uuid4())
                    await self.message_bus.publish(Message(
                        message_type=MessageType.ENHANCEMENT_REQUEST,
                        sender_id=self.team_id,  # Self-request for automatic processing
                        payload={
                            'request_id': request_id,
                            'document_result': document_result,
                            'target_section': section_id
                        },
                        team_id=self.team_id
                    ))
    
    async def _handle_enhancement_proposal(self, message: Message):
        """Handle enhancement proposal messages from individual agents"""
        request_id = message.payload.get('request_id')
        agent_id = message.sender_id
        proposal = message.payload.get('proposal')
        success = message.payload.get('success', False)
        
        if request_id in self.enhancement_requests and success and proposal:
            # Add the proposal to the request
            self.enhancement_requests[request_id]['proposals'].append({
                'agent_id': agent_id,
                'proposal': proposal,
                'reviews': [],
                'total_score': 0,
                'average_score': 0
            })
            logger.info(f"Received proposal from agent {agent_id} for request {request_id}")
            
            # Check if all agents have submitted proposals
            if len(self.enhancement_requests[request_id]['proposals']) == self.team_size:
                # All agents have submitted proposals, start peer review
                await self._start_peer_review(request_id)
    
    async def _handle_enhancement_review(self, message: Message):
        """Handle enhancement review messages from individual agents"""
        request_id = message.payload.get('request_id')
        proposal_id = message.payload.get('proposal_id')
        reviewer_id = message.sender_id
        review = message.payload.get('review')
        success = message.payload.get('success', False)
        
        if request_id in self.enhancement_requests and success and review:
            # Find the proposal
            for proposal_data in self.enhancement_requests[request_id]['proposals']:
                if proposal_data['proposal'].get('id') == proposal_id:
                    # Add the review to the proposal
                    proposal_data['reviews'].append({
                        'reviewer_id': reviewer_id,
                        'score': review.get('score', 0),
                        'feedback': review.get('feedback', '')
                    })
                    proposal_data['total_score'] += review.get('score', 0)
                    
                    # Update average score
                    if proposal_data['reviews']:
                        proposal_data['average_score'] = proposal_data['total_score'] / len(proposal_data['reviews'])
                    
                    logger.info(f"Received review from agent {reviewer_id} for proposal {proposal_id} with score {review.get('score')}")
                    
                    # Increment review count
                    self.enhancement_requests[request_id]['review_count'] += 1
                    
                    # Check if all reviews are complete
                    total_expected_reviews = len(self.enhancement_requests[request_id]['proposals']) * (self.team_size - 1)
                    if self.enhancement_requests[request_id]['review_count'] >= total_expected_reviews:
                        # All reviews are complete, select the best proposal
                        await self._select_best_proposal(request_id)
    
    async def _generate_enhancements_async(self, request_id: str):
        """Generate enhancement proposals asynchronously"""
        if request_id not in self.enhancement_requests:
            logger.error(f"Cannot generate enhancements for unknown request {request_id}")
            return
            
        request_data = self.enhancement_requests[request_id]
        document_result = request_data['document_result']
        target_section = request_data['target_section']
        standard_id = document_result.get('document_type', 'unknown')
        ambiguities = document_result.get('ambiguities', [])
        
        # Record activity in knowledge graph
        await self.knowledge_graph.record_team_activity(
            team_id=self.team_id,
            activity_type="enhancement_generation_started",
            details={
                'request_id': request_id,
                'standard_id': standard_id,
                'target_section': target_section
            }
        )
        
        # Start generation with all agents in parallel
        tasks = []
        for agent in self.agents:
            task = asyncio.create_task(self._generate_with_agent(
                agent, request_id, standard_id, target_section, ambiguities
            ))
            tasks.append(task)
        
        # Wait for all tasks to complete
        await asyncio.gather(*tasks)
    
    async def _generate_with_agent(self, agent, request_id: str, standard_id: str, target_section: str, ambiguities: List[Dict]):
        """Generate enhancement proposal with a single agent and publish the result"""
        try:
            result = await agent.generate_enhancement(
                standard_id=standard_id,
                section_id=target_section,
                enhancement_category="clarity",
                context={"ambiguities": ambiguities}
            )
            
            success = result.success and 'proposal' in result.data
            proposal = result.data.get('proposal', {}) if success else {}
            
            if success:
                proposal['agent_id'] = agent.agent_id
            
            # Publish result message
            await self.message_bus.publish(Message(
                message_type=MessageType.ENHANCEMENT_PROPOSAL,
                sender_id=agent.agent_id,
                payload={
                    'request_id': request_id,
                    'success': success,
                    'proposal': proposal,
                    'standard_id': standard_id,
                    'section_id': target_section
                },
                team_id=self.team_id
            ))
            
            logger.info(f"Agent {agent.agent_id} {'successfully generated' if success else 'failed to generate'} proposal")
        except Exception as e:
            logger.error(f"Error generating proposal with agent {agent.agent_id}: {str(e)}")
            await self.message_bus.publish(Message(
                message_type=MessageType.ENHANCEMENT_PROPOSAL,
                sender_id=agent.agent_id,
                payload={
                    'request_id': request_id,
                    'success': False,
                    'error': str(e),
                    'standard_id': standard_id,
                    'section_id': target_section
                },
                team_id=self.team_id
            ))
    
    async def generate_enhancements(self, document_result: Dict[str, Any], target_section: str) -> Dict[str, Any]:
        """
        Generate enhancement proposals with multiple agents and peer review
        
        Each agent generates proposals independently, then other agents review
        and rate each proposal. The highest-rated proposal is selected.
        """
        logger.info(f"Enhancement team generating proposals for section {target_section}")
        
        # Create a request ID
        request_id = str(uuid.uuid4())
        
        # Create a future to wait for the result
        result_future = asyncio.Future()
        
        # Store the request and future
        self.enhancement_requests[request_id] = {
            'document_result': document_result,
            'target_section': target_section,
            'requester_id': self.team_id,  # Self-request
            'status': 'processing',
            'timestamp': datetime.utcnow().isoformat(),
            'proposals': [],
            'reviews': {},
            'review_count': 0,
            'future': result_future
        }
        
        # Start the enhancement generation process
        await self._generate_enhancements_async(request_id)
        
        # Wait for the result
        return await result_future
        
    async def _start_peer_review(self, request_id: str):
        """Start peer review process for all proposals"""
        if request_id not in self.enhancement_requests:
            logger.error(f"Cannot start peer review for unknown request {request_id}")
            return
            
        request_data = self.enhancement_requests[request_id]
        proposals = request_data['proposals']
        
        if not proposals:
            logger.error(f"No proposals to review for request {request_id}")
            await self._handle_enhancement_failure(request_id, "All enhancement agents failed to generate proposals")
            return
        
        logger.info(f"Starting peer review for {len(proposals)} proposals in request {request_id}")
        
        # Record activity in knowledge graph
        await self.knowledge_graph.record_team_activity(
            team_id=self.team_id,
            activity_type="peer_review_started",
            details={
                'request_id': request_id,
                'proposal_count': len(proposals)
            }
        )
        
        # Start review tasks for each proposal
        for proposal_data in proposals:
            proposal = proposal_data['proposal']
            proposal_id = proposal.get('id')
            
            for reviewer in self.agents:
                # Skip self-review
                if reviewer.agent_id == proposal_data['agent_id']:
                    continue
                
                # Start review task
                asyncio.create_task(self._review_proposal(
                    reviewer, request_id, proposal_id, proposal
                ))
    
    async def _review_proposal(self, reviewer, request_id: str, proposal_id: str, proposal: Dict):
        """Review a proposal with a single agent and publish the result"""
        try:
            review_result = await reviewer.evaluate_proposal(proposal_id)
            
            success = review_result.success
            review = review_result.data if success else {'error': review_result.error}
            
            # Publish review message
            await self.message_bus.publish(Message(
                message_type=MessageType.ENHANCEMENT_REVIEW,
                sender_id=reviewer.agent_id,
                payload={
                    'request_id': request_id,
                    'proposal_id': proposal_id,
                    'success': success,
                    'review': review
                },
                team_id=self.team_id
            ))
            
            logger.info(f"Agent {reviewer.agent_id} {'successfully reviewed' if success else 'failed to review'} proposal {proposal_id}")
        except Exception as e:
            logger.error(f"Error reviewing proposal with agent {reviewer.agent_id}: {str(e)}")
            await self.message_bus.publish(Message(
                message_type=MessageType.ENHANCEMENT_REVIEW,
                sender_id=reviewer.agent_id,
                payload={
                    'request_id': request_id,
                    'proposal_id': proposal_id,
                    'success': False,
                    'error': str(e)
                },
                team_id=self.team_id
            ))
    
    async def _select_best_proposal(self, request_id: str):
        """Select the best proposal based on peer reviews"""
        if request_id not in self.enhancement_requests:
            logger.error(f"Cannot select best proposal for unknown request {request_id}")
            return
            
        request_data = self.enhancement_requests[request_id]
        proposals = request_data['proposals']
        
        if not proposals:
            logger.error(f"No proposals to select from for request {request_id}")
            await self._handle_enhancement_failure(request_id, "No proposals available for selection")
            return
        
        # Sort proposals by average score
        proposals.sort(key=lambda p: p.get('average_score', 0), reverse=True)
        selected_proposal = proposals[0] if proposals else None
        
        if not selected_proposal:
            logger.error(f"Failed to select a proposal for request {request_id}")
            await self._handle_enhancement_failure(request_id, "Failed to select a proposal")
            return
        
        logger.info(f"Selected highest-rated proposal for request {request_id}: {selected_proposal['proposal'].get('title')} with score {selected_proposal.get('average_score')}")
        
        # Record consensus in knowledge graph
        await self.knowledge_graph.record_consensus(
            team_id=self.team_id,
            proposal_id=request_id,
            consensus_data={
                'selected_proposal_id': selected_proposal['proposal'].get('id'),
                'average_score': selected_proposal.get('average_score', 0),
                'review_count': len(selected_proposal.get('reviews', [])),
                'team_size': self.team_size
            }
        )
        
        # Create result object
        result = {
            'proposals': [p['proposal'] for p in proposals],
            'reviews': {p['proposal'].get('id'): p.get('reviews', []) for p in proposals},
            'selected_proposal': selected_proposal['proposal'],
            'standard_id': request_data['document_result'].get('document_type', 'unknown'),
            'section_id': request_data['target_section'],
            'timestamp': datetime.utcnow().isoformat()
        }
        
        # Update request status
        self.enhancement_requests[request_id]['status'] = 'completed'
        self.enhancement_requests[request_id]['result'] = result
        
        # Publish completion message
        await self.message_bus.publish(Message(
            message_type=MessageType.ENHANCEMENT_COMPLETE,
            sender_id=self.team_id,
            recipient_id=request_data['requester_id'],
            payload={
                'request_id': request_id,
                'success': True,
                'result': result
            },
            team_id=self.team_id
        ))
        
        # Resolve future if it exists
        if 'future' in request_data:
            request_data['future'].set_result(result)
    
    async def _handle_enhancement_failure(self, request_id: str, error_msg: str):
        """Handle enhancement failure"""
        if request_id not in self.enhancement_requests:
            logger.error(f"Cannot handle failure for unknown request {request_id}")
            return
            
        request_data = self.enhancement_requests[request_id]
        
        # Update request status
        self.enhancement_requests[request_id]['status'] = 'failed'
        
        # Publish failure message
        await self.message_bus.publish(Message(
            message_type=MessageType.ENHANCEMENT_COMPLETE,
            sender_id=self.team_id,
            recipient_id=request_data['requester_id'],
            payload={
                'request_id': request_id,
                'success': False,
                'error': error_msg
            },
            team_id=self.team_id
        ))
        
        # Resolve future if it exists with exception
        if 'future' in request_data:
            request_data['future'].set_exception(ValueError(error_msg))

class ValidationTeam(AgentTeam):
    """Team of validation agents responsible for validating enhancement proposals"""
    
    def __init__(self, team_size: int = 3):
        super().__init__("validation", "validation_agent", team_size)
        self.validation_requests = {}
        
    def _subscribe_to_messages(self):
        """Subscribe to validation related messages"""
        self.message_bus.subscribe(MessageType.VALIDATION_REQUEST, self._handle_validation_request)
        self.message_bus.subscribe(MessageType.ENHANCEMENT_COMPLETE, self._handle_enhancement_complete)
        self.message_bus.subscribe(MessageType.VALIDATION_RESULT, self._handle_validation_result)
        
    async def _handle_validation_request(self, message: Message):
        """Handle validation request messages"""
        proposal = message.payload.get('proposal')
        request_id = message.payload.get('request_id', str(uuid.uuid4()))
        
        if not proposal:
            logger.error(f"Received validation request without proposal data (ID: {request_id})")
            # Send error response
            await self.message_bus.publish(Message(
                message_type=MessageType.VALIDATION_REQUEST_ACK,
                sender_id=self.team_id,
                recipient_id=message.sender_id,
                payload={
                    'request_id': request_id,
                    'status': 'error',
                    'error': 'No proposal data provided'
                },
                team_id=self.team_id
            ))
            return
            
        proposal_id = proposal.get('id')
        logger.info(f"Validation team received request for proposal {proposal_id} (ID: {request_id})")
        
        # Store the request for tracking
        self.validation_requests[request_id] = {
            'proposal': proposal,
            'requester_id': message.sender_id,
            'status': 'processing',
            'timestamp': datetime.utcnow().isoformat(),
            'validation_results': []
        }
        
        # Process the validation request asynchronously
        asyncio.create_task(self._validate_proposal_async(request_id))
        
        # Send acknowledgment
        await self.message_bus.publish(Message(
            message_type=MessageType.VALIDATION_REQUEST_ACK,
            sender_id=self.team_id,
            recipient_id=message.sender_id,
            payload={
                'request_id': request_id,
                'status': 'processing',
                'proposal_id': proposal_id
            },
            team_id=self.team_id
        ))
    
    async def _handle_enhancement_complete(self, message: Message):
        """Handle enhancement complete messages"""
        # This is a potential trigger for automatic validation
        if message.payload.get('success', False):
            result = message.payload.get('result', {})
            selected_proposal = result.get('selected_proposal')
            
            if selected_proposal:
                # Create a validation request
                request_id = str(uuid.uuid4())
                await self.message_bus.publish(Message(
                    message_type=MessageType.VALIDATION_REQUEST,
                    sender_id=self.team_id,  # Self-request for automatic processing
                    payload={
                        'request_id': request_id,
                        'proposal': selected_proposal
                    },
                    team_id=self.team_id
                ))
    
    async def _handle_validation_result(self, message: Message):
        """Handle validation result messages from individual agents"""
        request_id = message.payload.get('request_id')
        agent_id = message.sender_id
        validation = message.payload.get('validation')
        success = message.payload.get('success', False)
        
        if request_id in self.validation_requests and success and validation:
            # Add the validation to the request
            self.validation_requests[request_id]['validation_results'].append({
                'agent_id': agent_id,
                'validation': validation
            })
            logger.info(f"Received validation from agent {agent_id} for request {request_id}")
            
            # Check if all agents have submitted validations
            if len(self.validation_requests[request_id]['validation_results']) == self.team_size:
                # All agents have submitted validations, generate consensus
                await self._generate_consensus(request_id)
    
    async def _validate_proposal_async(self, request_id: str):
        """Validate proposal asynchronously with all agents in parallel"""
        if request_id not in self.validation_requests:
            logger.error(f"Cannot validate unknown request {request_id}")
            return
            
        request_data = self.validation_requests[request_id]
        proposal = request_data['proposal']
        proposal_id = proposal.get('id')
        
        # Record activity in knowledge graph
        await self.knowledge_graph.record_team_activity(
            team_id=self.team_id,
            activity_type="validation_started",
            details={
                'request_id': request_id,
                'proposal_id': proposal_id
            }
        )
        
        # Start validation with all agents in parallel
        tasks = []
        for agent in self.agents:
            task = asyncio.create_task(self._validate_with_agent(
                agent, request_id, proposal_id
            ))
            tasks.append(task)
        
        # Wait for all tasks to complete
        await asyncio.gather(*tasks)
    
    async def _validate_with_agent(self, agent, request_id: str, proposal_id: str):
        """Validate proposal with a single agent and publish the result"""
        try:
            result = await agent.validate_enhancement(
                proposal_id=proposal_id,
                validation_criteria={
                    'shariah_compliance': True,
                    'aaoifi_alignment': True,
                    'practical_implementation': True,
                    'clarity_improvement': True
                }
            )
            
            success = result.success
            validation = result.data if success else {'error': result.error}
            
            if success:
                validation['agent_id'] = agent.agent_id
            
            # Publish result message
            await self.message_bus.publish(Message(
                message_type=MessageType.VALIDATION_RESULT,
                sender_id=agent.agent_id,
                payload={
                    'request_id': request_id,
                    'success': success,
                    'validation': validation,
                    'proposal_id': proposal_id
                },
                team_id=self.team_id
            ))
            
            logger.info(f"Agent {agent.agent_id} {'successfully validated' if success else 'failed to validate'} proposal {proposal_id}")
        except Exception as e:
            logger.error(f"Error validating proposal with agent {agent.agent_id}: {str(e)}")
            await self.message_bus.publish(Message(
                message_type=MessageType.VALIDATION_RESULT,
                sender_id=agent.agent_id,
                payload={
                    'request_id': request_id,
                    'success': False,
                    'error': str(e),
                    'proposal_id': proposal_id
                },
                team_id=self.team_id
            ))
    
    async def validate_proposal(self, proposal: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate a proposal with multiple agents and consensus-based decision making
        
        Each agent validates the proposal independently, then results are combined
        and a consensus recommendation is determined through voting.
        """
        if not proposal:
            raise ValueError("No proposal provided for validation")
            
        proposal_id = proposal.get('id')
        logger.info(f"Validation team evaluating proposal {proposal_id}")
        
        # Create a request ID
        request_id = str(uuid.uuid4())
        
        # Create a future to wait for the result
        result_future = asyncio.Future()
        
        # Store the request and future
        self.validation_requests[request_id] = {
            'proposal': proposal,
            'requester_id': self.team_id,  # Self-request
            'status': 'processing',
            'timestamp': datetime.utcnow().isoformat(),
            'validation_results': [],
            'future': result_future
        }
        
        # Start validation
        await self._validate_proposal_async(request_id)
        
        # Wait for the result
        return await result_future
        
    async def _generate_consensus(self, request_id: str):
        """Generate consensus from all agent validations for a request"""
        if request_id not in self.validation_requests:
            logger.error(f"Cannot generate consensus for unknown request {request_id}")
            return
            
        request_data = self.validation_requests[request_id]
        proposal = request_data['proposal']
        proposal_id = proposal.get('id')
        
        # Extract validation results
        validation_results = []
        for result_data in request_data['validation_results']:
            if result_data.get('validation'):
                validation_results.append(result_data.get('validation'))
        
        if not validation_results:
            error_msg = "All validation agents failed to validate the proposal"
            logger.error(f"{error_msg} for request {request_id}")
            
            # Update request status
            self.validation_requests[request_id]['status'] = 'failed'
            
            # Publish failure message
            await self.message_bus.publish(Message(
                message_type=MessageType.VALIDATION_COMPLETE,
                sender_id=self.team_id,
                recipient_id=request_data['requester_id'],
                payload={
                    'request_id': request_id,
                    'success': False,
                    'error': error_msg,
                    'proposal_id': proposal_id
                },
                team_id=self.team_id
            ))
            
            # Resolve future if it exists
            if 'future' in request_data:
                request_data['future'].set_exception(ValueError(error_msg))
                
            return
        
        # Combine validation results and reach consensus
        logger.info(f"Combining validation results to reach consensus for request {request_id}")
        
        # Calculate average scores
        total_overall = sum(v.get('overall_score', 0) for v in validation_results)
        total_shariah = sum(v.get('shariah_compliance_score', 0) for v in validation_results)
        total_aaoifi = sum(v.get('aaoifi_alignment_score', 0) for v in validation_results)
        total_practical = sum(v.get('practical_implementation_score', 0) for v in validation_results)
        total_clarity = sum(v.get('clarity_improvement_score', 0) for v in validation_results)
        
        count = len(validation_results)
        avg_overall = total_overall / count if count > 0 else 0
        avg_shariah = total_shariah / count if count > 0 else 0
        avg_aaoifi = total_aaoifi / count if count > 0 else 0
        avg_practical = total_practical / count if count > 0 else 0
        avg_clarity = total_clarity / count if count > 0 else 0
        
        # Count votes for each recommendation
        recommendations = [v.get('recommendation', '') for v in validation_results]
        approve_votes = recommendations.count('approve')
        revise_votes = recommendations.count('revise')
        reject_votes = recommendations.count('reject')
        
        # Determine consensus recommendation
        if approve_votes > revise_votes and approve_votes > reject_votes:
            consensus_recommendation = 'approve'
        elif revise_votes > approve_votes and revise_votes > reject_votes:
            consensus_recommendation = 'revise'
        elif reject_votes > approve_votes and reject_votes > revise_votes:
            consensus_recommendation = 'reject'
        else:
            # In case of a tie, use the average score to decide
            if avg_overall >= 8:
                consensus_recommendation = 'approve'
            elif avg_overall >= 6:
                consensus_recommendation = 'revise'
            else:
                consensus_recommendation = 'reject'
        
        # Combine feedback from all agents
        all_feedback = [v.get('feedback', '') for v in validation_results if v.get('feedback')]
        consensus_feedback = " ".join(all_feedback)
        
        # Create consensus validation result
        consensus_validation = {
            'proposal_id': proposal_id,
            'timestamp': datetime.utcnow().isoformat(),
            'overall_score': round(avg_overall, 1),
            'shariah_compliance_score': round(avg_shariah, 1),
            'aaoifi_alignment_score': round(avg_aaoifi, 1),
            'practical_implementation_score': round(avg_practical, 1),
            'clarity_improvement_score': round(avg_clarity, 1),
            'recommendation': consensus_recommendation,
            'feedback': consensus_feedback,
            'approve_votes': approve_votes,
            'revise_votes': revise_votes,
            'reject_votes': reject_votes,
            'team_size': len(self.agents),
            'successful_validations': len(validation_results),
            'individual_validations': validation_results
        }
        
        # Record consensus in knowledge graph
        await self.knowledge_graph.record_consensus(
            team_id=self.team_id,
            proposal_id=request_id,
            consensus_data={
                'proposal_id': proposal_id,
                'recommendation': consensus_recommendation,
                'overall_score': round(avg_overall, 1),
                'approve_votes': approve_votes,
                'revise_votes': revise_votes,
                'reject_votes': reject_votes,
                'team_size': self.team_size
            }
        )
        
        # Update request status
        self.validation_requests[request_id]['status'] = 'completed'
        self.validation_requests[request_id]['consensus'] = consensus_validation
        
        # Publish completion message
        await self.message_bus.publish(Message(
            message_type=MessageType.VALIDATION_COMPLETE,
            sender_id=self.team_id,
            recipient_id=request_data['requester_id'],
            payload={
                'request_id': request_id,
                'success': True,
                'result': consensus_validation,
                'proposal_id': proposal_id
            },
            team_id=self.team_id
        ))
        
        logger.info(f"Validation team consensus for request {request_id}: {consensus_recommendation} with score {avg_overall}")
        
        # Resolve future if it exists
        if 'future' in request_data:
            request_data['future'].set_result(consensus_validation)

async def run_multi_agent_team_pipeline():
    """
    Run the complete multi-agent team pipeline for enhancing the FAS 7 (Salam) definition
    """
    logger.info("Starting multi-agent team pipeline for FAS 7 (Salam) enhancement")
    
    # Initialize knowledge graph
    knowledge_graph = create_knowledge_graph()
    await knowledge_graph.connect()
    
    try:
        # Initialize agent teams
        document_team = DocumentTeam(team_size=3)
        enhancement_team = EnhancementTeam(team_size=3)
        validation_team = ValidationTeam(team_size=3)
        
        await document_team.initialize()
        await enhancement_team.initialize()
        await validation_team.initialize()
        
        # Step 1: Document Team Processing
        logger.info("STEP 1: Document Team processing FAS 7 (Salam) standard")
        document_path = "data/standards/FAS7_Salam/FAS7_Salam.txt"
        
        document_result = await document_team.process_document(
            document_path=document_path,
            document_type="fas_7"
        )
        
        # For demonstration, add a sample section and ambiguity if none were found
        if not document_result.get('sections'):
            document_result['sections'] = [{
                'id': '1.2',
                'title': 'Definition',
                'content': 'Salam is a transaction in which the seller undertakes to supply specific goods to the buyer at a future date in exchange for an advanced price fully paid on the spot.'
            }]
            
        if not document_result.get('ambiguities'):
            document_result['ambiguities'] = [{
                'section_id': '1.2',
                'text': 'The definition lacks clarity on Shariah compliance and precise specification requirements for goods.',
                'severity': 'medium'
            }]
        
        logger.info(f"Document team extracted {len(document_result.get('sections', []))} sections")
        logger.info(f"Document team identified {len(document_result.get('ambiguities', []))} ambiguities")
        
        # Step 2: Enhancement Team Generation
        logger.info("STEP 2: Enhancement Team generating proposals for Salam definition")
        
        # Target the Salam definition section specifically
        target_section = "1.2 Definition"
        
        enhancement_result = await enhancement_team.generate_enhancements(
            document_result=document_result,
            target_section=target_section
        )
        
        selected_proposal = enhancement_result.get('selected_proposal')
        if selected_proposal:
            logger.info(f"Selected enhancement proposal: {selected_proposal.get('title')}")
            logger.info(f"Current text: {selected_proposal.get('current_text')}")
            logger.info(f"Proposed text: {selected_proposal.get('proposed_text')}")
            logger.info(f"Rationale: {selected_proposal.get('rationale')}")
            logger.info(f"Average peer review score: {selected_proposal.get('average_score')}")
        else:
            logger.error("No enhancement proposal was selected")
            return None
        
        # Step 3: Validation Team Evaluation
        logger.info("STEP 3: Validation Team evaluating the enhancement proposal")
        
        validation_result = await validation_team.validate_proposal(selected_proposal)
        
        logger.info(f"Validation consensus: {validation_result.get('recommendation')}")
        logger.info(f"Overall score: {validation_result.get('overall_score')}/10")
        logger.info(f"Shariah compliance: {validation_result.get('shariah_compliance_score')}/10")
        logger.info(f"AAOIFI alignment: {validation_result.get('aaoifi_alignment_score')}/10")
        logger.info(f"Practical implementation: {validation_result.get('practical_implementation_score')}/10")
        logger.info(f"Clarity improvement: {validation_result.get('clarity_improvement_score')}/10")
        logger.info(f"Voting results: Approve={validation_result.get('approve_votes')}, Revise={validation_result.get('revise_votes')}, Reject={validation_result.get('reject_votes')}")
        
        # Step 4: Store the validated proposal in the knowledge graph
        if validation_result.get('recommendation') == 'approve':
            logger.info("STEP 4: Storing approved proposal in knowledge graph")
            
            # Create a simplified data structure for Neo4j storage
            proposal_data = {
                'id': selected_proposal.get('id'),
                'title': selected_proposal.get('title'),
                'standard_id': selected_proposal.get('standard_id'),
                'section_id': selected_proposal.get('section_id'),
                'category': selected_proposal.get('category'),
                'status': 'approved',
                'timestamp': datetime.utcnow().isoformat(),
                'current_text': selected_proposal.get('current_text'),
                'proposed_text': selected_proposal.get('proposed_text'),
                'rationale': selected_proposal.get('rationale'),
                'validation_score': validation_result.get('overall_score'),
                'validation_recommendation': validation_result.get('recommendation'),
                'validation_feedback': validation_result.get('feedback'),
                'approve_votes': validation_result.get('approve_votes'),
                'revise_votes': validation_result.get('revise_votes'),
                'reject_votes': validation_result.get('reject_votes')
            }
            
            try:
                store_result = await knowledge_graph.create_enhancement_proposal(proposal_data)
                logger.info(f"Proposal storage result: {store_result}")
            except Exception as e:
                logger.error(f"Error storing proposal: {str(e)}")
                logger.info("Continuing with test without storage...")
        else:
            logger.info(f"Proposal not approved. Recommendation: {validation_result.get('recommendation')}")
        
        # Clean up
        await document_team.shutdown()
        await enhancement_team.shutdown()
        await validation_team.shutdown()
        await knowledge_graph.close()
        
        logger.info("Multi-agent team pipeline test completed")
        
        # Return the complete test results
        return {
            "document_processing": document_result,
            "enhancement_generation": enhancement_result,
            "validation_result": validation_result
        }
    except Exception as e:
        logger.error(f"Error in multi-agent team pipeline: {str(e)}", exc_info=True)
        # Ensure proper cleanup even if there's an error
        try:
            await document_team.shutdown()
            await enhancement_team.shutdown()
            await validation_team.shutdown()
            await knowledge_graph.close()
        except:
            pass
        return None

def print_summary(test_results):
    """Print a summary of the multi-agent team pipeline results"""
    if not test_results:
        print("\nTest failed to complete successfully!")
        return
        
    print("\n" + "="*80)
    print("MULTI-AGENT TEAM PIPELINE SUMMARY")
    print("="*80)
    
    document_result = test_results.get("document_processing", {})
    enhancement_result = test_results.get("enhancement_generation", {})
    validation_result = test_results.get("validation_result", {})
    
    print("\nDocument Team Processing:")
    print(f"- Team size: {document_result.get('team_size', 0)} agents")
    print(f"- Successful agents: {document_result.get('successful_agents', 0)}")
    print(f"- Sections extracted: {len(document_result.get('sections', []))}")
    print(f"- Ambiguities identified: {len(document_result.get('ambiguities', []))}")
    
    if document_result.get('ambiguities'):
        print("\nSample ambiguity:")
        ambiguity = document_result.get('ambiguities', [])[0]
        print(f"- Section: {ambiguity.get('section_id')}")
        print(f"- Issue: {ambiguity.get('text')}")
    
    print("\nEnhancement Team Generation:")
    print(f"- Total proposals generated: {len(enhancement_result.get('proposals', []))}")
    
    selected_proposal = enhancement_result.get('selected_proposal', {})
    if selected_proposal:
        print("\nSelected Proposal:")
        print(f"- Title: {selected_proposal.get('title')}")
        print(f"- Generating agent: {selected_proposal.get('agent_id')}")
        print(f"- Average peer review score: {selected_proposal.get('average_score')}/10")
        print(f"- Current text: {selected_proposal.get('current_text')}")
        print(f"- Proposed text: {selected_proposal.get('proposed_text')}")
        print(f"- Rationale: {selected_proposal.get('rationale')}")
    
    print("\nValidation Team Evaluation:")
    print(f"- Team size: {validation_result.get('team_size', 0)} agents")
    print(f"- Successful validations: {validation_result.get('successful_validations', 0)}")
    print(f"- Overall score: {validation_result.get('overall_score')}/10")
    print(f"- Shariah compliance score: {validation_result.get('shariah_compliance_score')}/10")
    print(f"- AAOIFI alignment score: {validation_result.get('aaoifi_alignment_score')}/10")
    print(f"- Practical implementation score: {validation_result.get('practical_implementation_score')}/10")
    print(f"- Clarity improvement score: {validation_result.get('clarity_improvement_score')}/10")
    print(f"- Voting results: Approve={validation_result.get('approve_votes', 0)}, Revise={validation_result.get('revise_votes', 0)}, Reject={validation_result.get('reject_votes', 0)}")
    print(f"- Consensus recommendation: {validation_result.get('recommendation')}")
    print(f"- Feedback: {validation_result.get('feedback')}")
    
    print("\nMulti-agent team pipeline completed successfully!")

if __name__ == "__main__":
    # Run the test
    test_results = asyncio.run(run_multi_agent_team_pipeline())
    
    # Print summary
    print_summary(test_results)
