"""
Event Bus for Islamic Finance Standards Enhancement System

This module provides an event-driven communication mechanism between agents.
It simulates a Kafka-like event streaming platform.
"""

import logging
import uuid
import json
from typing import Dict, List, Any, Callable
from datetime import datetime
from enum import Enum, auto

class EventType(Enum):
    """Event types for the Islamic Finance Standards Enhancement System"""
    # Document processing events
    DOCUMENT_RECEIVED = "document.received"
    DOCUMENT_PROCESSED = "document.processed"
    DOCUMENT_FAILED = "document.failed"
    
    # Enhancement events
    ENHANCEMENT_CREATED = "enhancement.created"
    ENHANCEMENT_UPDATED = "enhancement.updated"
    
    # Validation events
    VALIDATION_STARTED = "validation.started"
    VALIDATION_COMPLETED = "validation.completed"
    
    # Knowledge graph events
    KNOWLEDGE_GRAPH_UPDATED = "knowledge_graph.updated"
    
    # Neo4j integration events
    NEO4J_CONNECTED = "neo4j.connected"
    NEO4J_DISCONNECTED = "neo4j.disconnected"
    
    # System events
    SYSTEM_ERROR = "system.error"
    SYSTEM_WARNING = "system.warning"

logger = logging.getLogger(__name__)

class EventBus:
    """
    Event bus for agent communication.
    Simulates a Kafka-like event streaming platform.
    """
    
    def __init__(self):
        """Initialize the event bus"""
        self.subscribers = {}
        self.events = []
        logger.info("Event bus initialized")
    
    def publish(self, event_type: str | EventType, payload: Dict[str, Any]) -> str:
        """
        Publish an event to the bus
        
        Args:
            event_type: Type of the event (e.g., 'standard.processed')
            event_data: Data associated with the event
            
        Returns:
            Event ID
        """
        event_id = str(uuid.uuid4())
        timestamp = datetime.now().isoformat()
        
        # Convert EventType enum to string if needed
        event_type_str = event_type.value if isinstance(event_type, EventType) else event_type
        
        event = {
            "id": event_id,
            "type": event_type_str,
            "timestamp": timestamp,
            "payload": payload
        }
        
        self.events.append(event)
        logger.info(f"Published event: {event_type_str} (ID: {event_id})")
        
        # Notify subscribers
        if event_type_str in self.subscribers:
            for callback in self.subscribers[event_type_str]:
                try:
                    callback(event)
                except Exception as e:
                    logger.error(f"Error in event handler for {event_type_str}: {str(e)}")
        
        return event_id
    
    def subscribe(self, event_type: str | EventType, callback: Callable[[Dict[str, Any]], None]) -> None:
        """
        Subscribe to an event type
        
        Args:
            event_type: Type of the event to subscribe to
            callback: Function to call when the event is published
        """
        # Convert EventType enum to string if needed
        event_type_str = event_type.value if isinstance(event_type, EventType) else event_type
        
        if event_type_str not in self.subscribers:
            self.subscribers[event_type_str] = []
        
        self.subscribers[event_type_str].append(callback)
        logger.info(f"Subscribed to event: {event_type_str}")
    
    def get_events(self, event_type: str | EventType = None) -> List[Dict[str, Any]]:
        """
        Get events from the bus
        
        Args:
            event_type: Optional type of events to filter by
            
        Returns:
            List of events
        """
        if event_type:
            # Convert EventType enum to string if needed
            event_type_str = event_type.value if isinstance(event_type, EventType) else event_type
            return [event for event in self.events if event["type"] == event_type_str]
        else:
            return self.events
    
    def clear_events(self) -> None:
        """Clear all events from the bus"""
        self.events = []
        logger.info("Event bus cleared")
