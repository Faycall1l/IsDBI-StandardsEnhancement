"""
Event Bus for Islamic Finance Standards Enhancement System

This module provides an event bus implementation for communication between
different components of the system.
"""

import json
import logging
import uuid
from datetime import datetime
from enum import Enum, auto
from typing import Dict, List, Any, Optional, Callable

class EventType(Enum):
    """Event types for the event bus"""
    DOCUMENT_PROCESSED = auto()
    ENHANCEMENT_GENERATED = auto()
    ENHANCEMENT_VALIDATED = auto()
    ENHANCEMENT_APPROVED = auto()
    ENHANCEMENT_REJECTED = auto()
    ENHANCEMENT_NEEDS_REVISION = auto()
    COMMENT_ADDED = auto()
    VOTE_RECORDED = auto()
    SYSTEM_ERROR = auto()

class EventBus:
    """Event bus for communication between components"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(EventBus, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if hasattr(self, '_initialized') and self._initialized:
            return
            
        self._initialized = True
        self.logger = logging.getLogger(__name__)
        self.events = []
        self.listeners = {}
        self.logger.info("EventBus initialized")
    
    def subscribe(self, topic: str, callback: Callable):
        """Subscribe to events on a topic"""
        if topic not in self.listeners:
            self.listeners[topic] = []
        self.listeners[topic].append(callback)
        self.logger.info(f"Subscribed to topic: {topic}")
    
    def publish(self, topic: str, event_type: EventType, payload: Dict[str, Any]) -> str:
        """Publish an event to a topic"""
        event_id = str(uuid.uuid4())
        event = {
            "id": event_id,
            "topic": topic,
            "type": event_type.name,
            "payload": payload,
            "timestamp": datetime.now().isoformat()
        }
        self.events.append(event)
        self.logger.info(f"Published event to topic: {topic}, type: {event_type.name}")
        
        # Notify listeners
        if topic in self.listeners:
            for callback in self.listeners[topic]:
                try:
                    callback(event)
                except Exception as e:
                    self.logger.error(f"Error in event listener: {e}")
        
        return event_id
    
    def publish_event(self, event_data: Dict[str, Any]) -> str:
        """Publish an event with the given data"""
        event_id = str(uuid.uuid4())
        event = {
            "id": event_id,
            "topic": event_data.get("topic", "system"),
            "type": event_data.get("type", "SYSTEM_EVENT"),
            "payload": event_data.get("payload", {}),
            "timestamp": datetime.now().isoformat()
        }
        self.events.append(event)
        self.logger.info(f"Published event to topic: {event['topic']}, type: {event['type']}")
        
        # Notify listeners
        topic = event["topic"]
        if topic in self.listeners:
            for callback in self.listeners[topic]:
                try:
                    callback(event)
                except Exception as e:
                    self.logger.error(f"Error in event listener: {e}")
        
        return event_id
    
    def get_events(self, topic: Optional[str] = None, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent events, optionally filtered by topic"""
        if topic:
            filtered_events = [e for e in self.events if e["topic"] == topic]
            return sorted(filtered_events, key=lambda x: x["timestamp"], reverse=True)[:limit]
        else:
            return sorted(self.events, key=lambda x: x["timestamp"], reverse=True)[:limit]
    
    def get_recent_events(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent events across all topics"""
        return sorted(self.events, key=lambda x: x["timestamp"], reverse=True)[:limit]
    
    def clear_events(self):
        """Clear all events"""
        self.events = []
        self.logger.info("Cleared all events")
