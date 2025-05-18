#!/usr/bin/env python
"""
Run Autonomous System

This script runs the autonomous multi-agent system for Islamic Finance Standards Enhancement.
It initializes the agent teams, message bus, and knowledge graph, and starts the monitoring
for regulatory updates.
"""

import asyncio
import logging
import os
from pathlib import Path
from datetime import datetime

from IslamicFinanceStandardsAI.core.agents.agent_factory import AgentFactory
from IslamicFinanceStandardsAI.core.messaging.message_bus import MessageBus, MessageType
from IslamicFinanceStandardsAI.database.interfaces.knowledge_graph import get_knowledge_graph
from IslamicFinanceStandardsAI.utils.regulatory_monitoring import MonitoringService
from IslamicFinanceStandardsAI.utils.monitoring import metrics, health_check, export_metrics_to_json
from IslamicFinanceStandardsAI.utils.config import load_config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(f"logs/autonomous_system_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
    ]
)
logger = logging.getLogger(__name__)

class AutonomousSystem:
    """
    Autonomous System for Islamic Finance Standards Enhancement.
    
    This class manages the autonomous operation of the multi-agent system,
    including team creation, message bus initialization, and monitoring service.
    """
    
    def __init__(self, config_path=None):
        """Initialize the autonomous system."""
        self.config = load_config(config_path)
        self.agent_factory = AgentFactory()
        self.message_bus = MessageBus()
        self.knowledge_graph = None
        self.monitoring_service = None
        self.teams = {}
        
        # Create logs directory if it doesn't exist
        os.makedirs("logs", exist_ok=True)
        
        logger.info("Autonomous system initialized")
        
    async def initialize(self):
        """Initialize all components of the autonomous system."""
        # Initialize knowledge graph
        logger.info("Initializing knowledge graph...")
        self.knowledge_graph = await get_knowledge_graph()
        await self.agent_factory.initialize_knowledge_graph()
        
        # Create agent teams
        await self._create_teams()
        
        # Initialize monitoring service
        self.monitoring_service = MonitoringService(
            self.message_bus,
            self.config.get('monitoring', {})
        )
        
        logger.info("Autonomous system components initialized")
        
    async def _create_teams(self):
        """Create agent teams for document processing, enhancement, and validation."""
        # Create document processing team
        logger.info("Creating document processing team...")
        self.teams['document_team'] = self.agent_factory.create_agent_team(
            'document_team',
            'document_agent',
            count=self.config.get('teams', {}).get('document_team_size', 3)
        )
        
        # Create enhancement team
        logger.info("Creating enhancement team...")
        self.teams['enhancement_team'] = self.agent_factory.create_agent_team(
            'enhancement_team',
            'enhancement_agent',
            count=self.config.get('teams', {}).get('enhancement_team_size', 3)
        )
        
        # Create validation team
        logger.info("Creating validation team...")
        self.teams['validation_team'] = self.agent_factory.create_agent_team(
            'validation_team',
            'validation_agent',
            count=self.config.get('teams', {}).get('validation_team_size', 3)
        )
        
        # Create blockchain team for recording final results
        logger.info("Creating blockchain team...")
        self.teams['blockchain_team'] = self.agent_factory.create_agent_team(
            'blockchain_team',
            'blockchain_agent',
            count=1  # Only need one blockchain agent
        )
        
        # Subscribe teams to relevant message types
        await self._subscribe_teams()
        
        logger.info(f"Created {sum(len(team) for team in self.teams.values())} agents in {len(self.teams)} teams")
        
    async def _subscribe_teams(self):
        """Subscribe teams to relevant message types."""
        # Document team subscriptions
        for agent_id in self.teams['document_team']:
            self.agent_factory.subscribe_agent_to_messages(
                agent_id,
                [MessageType.REGULATORY_UPDATE, MessageType.DOCUMENT_REQUEST]
            )
            
        # Enhancement team subscriptions
        for agent_id in self.teams['enhancement_team']:
            self.agent_factory.subscribe_agent_to_messages(
                agent_id,
                [MessageType.DOCUMENT_PROCESSED, MessageType.ENHANCEMENT_REQUEST]
            )
            
        # Validation team subscriptions
        for agent_id in self.teams['validation_team']:
            self.agent_factory.subscribe_agent_to_messages(
                agent_id,
                [MessageType.ENHANCEMENT_COMPLETE, MessageType.VALIDATION_REQUEST]
            )
            
        # Blockchain team subscriptions
        for agent_id in self.teams['blockchain_team']:
            self.agent_factory.subscribe_agent_to_messages(
                agent_id,
                [MessageType.VALIDATION_RESULT]
            )
            
        logger.info("Teams subscribed to relevant message types")
        
    async def start(self):
        """Start the autonomous system."""
        logger.info("Starting autonomous system...")
        
        # Start all teams
        for team_name in self.teams:
            await self.agent_factory.start_team(team_name)
            
        # Start monitoring service
        await self.monitoring_service.start()
        
        logger.info("Autonomous system started")
        
        # Keep the system running
        try:
            while True:
                await asyncio.sleep(10)
                # Perform periodic health checks
                await self._health_check()
        except asyncio.CancelledError:
            logger.info("Autonomous system shutdown requested")
            await self.stop()
        except Exception as e:
            logger.error(f"Error in autonomous system: {e}")
            await self.stop()
            
    async def _health_check(self):
        """Perform health checks on all components."""
        # Update system metrics
        metrics.update_system_metrics()
        
        # Check message bus
        message_count = len(self.message_bus._message_history)
        logger.info(f"Message bus status: {message_count} messages processed")
        metrics.record_metric("application.message_bus.message_count", message_count)
        
        # Check agent teams
        for team_name, agent_ids in self.teams.items():
            active_agents = 0
            for agent_id in agent_ids:
                status = await self.agent_factory.get_agent_status(agent_id)
                if status.get('status') == 'running':
                    active_agents += 1
                # Record agent-specific metrics
                agent_type = agent_id.split('_')[1] if '_' in agent_id else 'unknown'
                metrics.record_metric(f"agents.{agent_type}.{agent_id}.status", status.get('status', 'unknown'))
                
            logger.info(f"Team {team_name}: {active_agents}/{len(agent_ids)} agents active")
            metrics.record_metric(f"application.teams.{team_name}.active_agents", active_agents)
            metrics.record_metric(f"application.teams.{team_name}.total_agents", len(agent_ids))
            
        # Check monitoring service
        if self.monitoring_service:
            status = await self.monitoring_service.get_status()
            logger.info(f"Monitoring service status: {status}")
            for key, value in status.items():
                if isinstance(value, (int, float, bool)):
                    metrics.record_metric(f"application.monitoring.{key}", value)
        
        # Run health checks
        health_results = health_check.run_all_checks()
        metrics.record_metric("application.health.overall_status", all(health_results.values()))
        
        # Export metrics to JSON every hour
        current_time = datetime.now()
        if not hasattr(self, '_last_metrics_export') or \
           (current_time - self._last_metrics_export).total_seconds() > 3600:
            self._last_metrics_export = current_time
            metrics_dir = Path("metrics")
            metrics_dir.mkdir(exist_ok=True)
            metrics_file = metrics_dir / f"metrics_{current_time.strftime('%Y%m%d_%H%M%S')}.json"
            export_metrics_to_json(str(metrics_file))
            logger.info(f"Exported metrics to {metrics_file}")
            
    async def stop(self):
        """Stop the autonomous system."""
        logger.info("Stopping autonomous system...")
        
        # Stop monitoring service
        if self.monitoring_service:
            await self.monitoring_service.stop()
            
        # Stop all teams
        for team_name in self.teams:
            await self.agent_factory.stop_team(team_name)
            
        logger.info("Autonomous system stopped")
        
    async def trigger_update(self, update_data):
        """
        Manually trigger a regulatory update for testing.
        
        Args:
            update_data: Data about the regulatory update
        """
        logger.info(f"Manually triggering update: {update_data.get('title', 'Unknown update')}")
        
        # Create a message for the update
        await self.agent_factory.publish_message(
            message_type=MessageType.REGULATORY_UPDATE,
            content=update_data,
            sender="manual_trigger",
            metadata={"source": "manual", "timestamp": datetime.now().isoformat()}
        )
        
        logger.info("Manual update triggered")

async def main():
    """Run the autonomous system."""
    # Parse command line arguments
    import argparse
    parser = argparse.ArgumentParser(description='Run the autonomous system for Islamic Finance Standards Enhancement')
    parser.add_argument('--config', help='Path to configuration file')
    parser.add_argument('--test', action='store_true', help='Run in test mode with a mock trigger')
    args = parser.parse_args()
    
    # Create and initialize the autonomous system
    system = AutonomousSystem(args.config)
    await system.initialize()
    
    # If in test mode, trigger a mock update
    if args.test:
        logger.info("Running in test mode with mock trigger")
        # Wait for system to initialize fully
        await asyncio.sleep(2)
        
        # Trigger mock update
        await system.trigger_update({
            "title": "AAOIFI Updates to Murabaha Standards",
            "source": "AAOIFI",
            "url": "https://aaoifi.com/updates/2025/murabaha",
            "date": datetime.now().isoformat(),
            "summary": "Updates to accounting treatments for Murabaha transactions",
            "standards_affected": ["FAS 28"],
            "priority": "high"
        })
    
    # Start the system
    await system.start()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Keyboard interrupt received, shutting down")
    except Exception as e:
        logger.error(f"Error running autonomous system: {e}")
