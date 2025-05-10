"""
Monitoring and Observability Module

This module provides comprehensive monitoring and observability capabilities for the
Islamic Finance Standards Enhancement system, including performance metrics, health checks,
and alerting mechanisms.
"""

import os
import time
import json
import logging
import threading
import psutil
import socket
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime, timedelta
from functools import wraps

# Configure logging
logger = logging.getLogger(__name__)

class Metrics:
    """Class for collecting and managing system metrics"""
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(Metrics, cls).__new__(cls)
                cls._instance._initialize()
            return cls._instance
    
    def _initialize(self):
        """Initialize metrics storage"""
        self.metrics = {
            "system": {},
            "application": {},
            "agents": {
                "document_agent": {},
                "enhancement_agent": {},
                "validation_agent": {}
            },
            "database": {},
            "api": {}
        }
        self.start_time = datetime.now()
        self.hostname = socket.gethostname()
        
        # Start background collection thread
        self.collection_active = True
        self.collection_thread = threading.Thread(target=self._collect_system_metrics_periodically)
        self.collection_thread.daemon = True
        self.collection_thread.start()
    
    def _collect_system_metrics_periodically(self, interval=60):
        """Collect system metrics at regular intervals"""
        while self.collection_active:
            try:
                self.collect_system_metrics()
                time.sleep(interval)
            except Exception as e:
                logger.error(f"Error collecting system metrics: {str(e)}")
                time.sleep(interval)
    
    def collect_system_metrics(self):
        """Collect current system metrics"""
        # CPU metrics
        cpu_percent = psutil.cpu_percent(interval=1)
        cpu_count = psutil.cpu_count()
        
        # Memory metrics
        memory = psutil.virtual_memory()
        memory_used_percent = memory.percent
        memory_available_mb = memory.available / (1024 * 1024)
        
        # Disk metrics
        disk = psutil.disk_usage('/')
        disk_used_percent = disk.percent
        disk_free_gb = disk.free / (1024 * 1024 * 1024)
        
        # Network metrics
        net_io = psutil.net_io_counters()
        
        # Process metrics
        process = psutil.Process(os.getpid())
        process_cpu_percent = process.cpu_percent(interval=1)
        process_memory_mb = process.memory_info().rss / (1024 * 1024)
        
        # Update system metrics
        self.metrics["system"].update({
            "timestamp": datetime.now().isoformat(),
            "cpu": {
                "percent": cpu_percent,
                "count": cpu_count
            },
            "memory": {
                "percent_used": memory_used_percent,
                "available_mb": memory_available_mb
            },
            "disk": {
                "percent_used": disk_used_percent,
                "free_gb": disk_free_gb
            },
            "network": {
                "bytes_sent": net_io.bytes_sent,
                "bytes_recv": net_io.bytes_recv
            },
            "process": {
                "cpu_percent": process_cpu_percent,
                "memory_mb": process_memory_mb
            },
            "uptime_seconds": (datetime.now() - self.start_time).total_seconds()
        })
        
        return self.metrics["system"]
    
    def record_agent_metric(self, agent_type: str, metric_name: str, value: Any):
        """Record a metric for a specific agent"""
        if agent_type in self.metrics["agents"]:
            self.metrics["agents"][agent_type][metric_name] = {
                "value": value,
                "timestamp": datetime.now().isoformat()
            }
    
    def record_database_metric(self, metric_name: str, value: Any):
        """Record a database metric"""
        self.metrics["database"][metric_name] = {
            "value": value,
            "timestamp": datetime.now().isoformat()
        }
    
    def record_api_metric(self, metric_name: str, value: Any):
        """Record an API metric"""
        self.metrics["api"][metric_name] = {
            "value": value,
            "timestamp": datetime.now().isoformat()
        }
    
    def record_application_metric(self, metric_name: str, value: Any):
        """Record an application-level metric"""
        self.metrics["application"][metric_name] = {
            "value": value,
            "timestamp": datetime.now().isoformat()
        }
    
    def get_all_metrics(self) -> Dict[str, Any]:
        """Get all collected metrics"""
        # Ensure system metrics are up-to-date
        self.collect_system_metrics()
        return self.metrics
    
    def get_agent_metrics(self, agent_type: str) -> Dict[str, Any]:
        """Get metrics for a specific agent"""
        if agent_type in self.metrics["agents"]:
            return self.metrics["agents"][agent_type]
        return {}
    
    def reset_metrics(self):
        """Reset all metrics"""
        self._initialize()
    
    def stop_collection(self):
        """Stop the background metrics collection"""
        self.collection_active = False
        if self.collection_thread.is_alive():
            self.collection_thread.join(timeout=5)

class PerformanceMonitor:
    """Class for monitoring function performance"""
    
    def __init__(self):
        self.metrics = Metrics()
        self.function_stats = {}
    
    def measure_execution_time(self, category: str = "application"):
        """Decorator to measure function execution time"""
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                start_time = time.time()
                result = func(*args, **kwargs)
                execution_time = time.time() - start_time
                
                # Record the execution time
                func_name = func.__name__
                if func_name not in self.function_stats:
                    self.function_stats[func_name] = {
                        "count": 0,
                        "total_time": 0,
                        "min_time": float('inf'),
                        "max_time": 0,
                        "last_execution_time": 0
                    }
                
                stats = self.function_stats[func_name]
                stats["count"] += 1
                stats["total_time"] += execution_time
                stats["min_time"] = min(stats["min_time"], execution_time)
                stats["max_time"] = max(stats["max_time"], execution_time)
                stats["last_execution_time"] = execution_time
                
                # Calculate average
                stats["avg_time"] = stats["total_time"] / stats["count"]
                
                # Record in appropriate category
                if category == "document_agent" or category == "enhancement_agent" or category == "validation_agent":
                    self.metrics.record_agent_metric(category, f"{func_name}_execution_time", execution_time)
                elif category == "database":
                    self.metrics.record_database_metric(f"{func_name}_execution_time", execution_time)
                elif category == "api":
                    self.metrics.record_api_metric(f"{func_name}_execution_time", execution_time)
                else:
                    self.metrics.record_application_metric(f"{func_name}_execution_time", execution_time)
                
                return result
            return wrapper
        return decorator
    
    def get_function_stats(self) -> Dict[str, Any]:
        """Get statistics for all monitored functions"""
        return self.function_stats

class HealthCheck:
    """Class for performing health checks on system components"""
    
    def __init__(self):
        self.health_checks = {}
        self.last_check_results = {}
    
    def register_check(self, name: str, check_function: Callable[[], bool], description: str = ""):
        """Register a health check function"""
        self.health_checks[name] = {
            "function": check_function,
            "description": description
        }
    
    def run_all_checks(self) -> Dict[str, Any]:
        """Run all registered health checks"""
        results = {
            "timestamp": datetime.now().isoformat(),
            "overall_status": "healthy",
            "checks": {}
        }
        
        for name, check_info in self.health_checks.items():
            try:
                status = check_info["function"]()
                check_result = {
                    "status": "healthy" if status else "unhealthy",
                    "description": check_info["description"]
                }
                
                if not status:
                    results["overall_status"] = "degraded"
            except Exception as e:
                check_result = {
                    "status": "error",
                    "description": check_info["description"],
                    "error": str(e)
                }
                results["overall_status"] = "degraded"
            
            results["checks"][name] = check_result
        
        self.last_check_results = results
        return results
    
    def get_last_results(self) -> Dict[str, Any]:
        """Get results of the last health check run"""
        return self.last_check_results

class AlertManager:
    """Class for managing alerts based on metrics and health checks"""
    
    def __init__(self):
        self.alert_rules = {}
        self.active_alerts = {}
        self.alert_history = []
        self.metrics = Metrics()
        
        # Maximum number of alerts to keep in history
        self.max_history = 100
    
    def register_alert_rule(self, 
                           name: str, 
                           metric_path: str, 
                           threshold: Any, 
                           comparison: str = "greater_than",
                           severity: str = "warning",
                           description: str = ""):
        """Register an alert rule"""
        self.alert_rules[name] = {
            "metric_path": metric_path,
            "threshold": threshold,
            "comparison": comparison,
            "severity": severity,
            "description": description,
            "active": False,
            "last_triggered": None
        }
    
    def check_alerts(self) -> List[Dict[str, Any]]:
        """Check all alert rules against current metrics"""
        all_metrics = self.metrics.get_all_metrics()
        triggered_alerts = []
        
        for name, rule in self.alert_rules.items():
            # Extract the metric value using the path
            path_parts = rule["metric_path"].split(".")
            metric_value = all_metrics
            
            try:
                for part in path_parts:
                    metric_value = metric_value[part]
                
                # If the metric path points to a dictionary with a 'value' key, use that
                if isinstance(metric_value, dict) and "value" in metric_value:
                    metric_value = metric_value["value"]
                
                # Compare the metric value to the threshold
                alert_triggered = False
                
                if rule["comparison"] == "greater_than":
                    alert_triggered = metric_value > rule["threshold"]
                elif rule["comparison"] == "less_than":
                    alert_triggered = metric_value < rule["threshold"]
                elif rule["comparison"] == "equals":
                    alert_triggered = metric_value == rule["threshold"]
                elif rule["comparison"] == "not_equals":
                    alert_triggered = metric_value != rule["threshold"]
                
                # Update alert status
                if alert_triggered:
                    if not rule["active"]:
                        # New alert
                        alert = {
                            "name": name,
                            "severity": rule["severity"],
                            "description": rule["description"],
                            "metric_path": rule["metric_path"],
                            "threshold": rule["threshold"],
                            "actual_value": metric_value,
                            "triggered_at": datetime.now().isoformat()
                        }
                        
                        triggered_alerts.append(alert)
                        self.alert_history.append(alert)
                        
                        # Trim history if needed
                        if len(self.alert_history) > self.max_history:
                            self.alert_history = self.alert_history[-self.max_history:]
                    
                    rule["active"] = True
                    rule["last_triggered"] = datetime.now().isoformat()
                    self.active_alerts[name] = {
                        "rule": rule,
                        "current_value": metric_value,
                        "triggered_at": rule["last_triggered"]
                    }
                else:
                    # Alert condition no longer met
                    if rule["active"]:
                        rule["active"] = False
                        if name in self.active_alerts:
                            del self.active_alerts[name]
            
            except (KeyError, TypeError) as e:
                logger.warning(f"Error checking alert rule {name}: {str(e)}")
        
        return triggered_alerts
    
    def get_active_alerts(self) -> Dict[str, Any]:
        """Get all currently active alerts"""
        return self.active_alerts
    
    def get_alert_history(self) -> List[Dict[str, Any]]:
        """Get alert history"""
        return self.alert_history

# Initialize global instances
metrics = Metrics()
performance_monitor = PerformanceMonitor()
health_check = HealthCheck()
alert_manager = AlertManager()

def initialize_monitoring():
    """Initialize the monitoring system with default checks and alerts"""
    # Register default health checks
    health_check.register_check(
        "system_cpu",
        lambda: metrics.metrics["system"].get("cpu", {}).get("percent", 0) < 90,
        "Check if CPU usage is below 90%"
    )
    
    health_check.register_check(
        "system_memory",
        lambda: metrics.metrics["system"].get("memory", {}).get("percent_used", 0) < 90,
        "Check if memory usage is below 90%"
    )
    
    health_check.register_check(
        "disk_space",
        lambda: metrics.metrics["system"].get("disk", {}).get("percent_used", 0) < 90,
        "Check if disk usage is below 90%"
    )
    
    # Register default alert rules
    alert_manager.register_alert_rule(
        "high_cpu_usage",
        "system.cpu.percent",
        80,
        "greater_than",
        "warning",
        "CPU usage is above 80%"
    )
    
    alert_manager.register_alert_rule(
        "high_memory_usage",
        "system.memory.percent_used",
        80,
        "greater_than",
        "warning",
        "Memory usage is above 80%"
    )
    
    alert_manager.register_alert_rule(
        "low_disk_space",
        "system.disk.free_gb",
        5,
        "less_than",
        "critical",
        "Less than 5GB of free disk space"
    )
    
    logger.info("Monitoring system initialized with default checks and alerts")

def get_system_status() -> Dict[str, Any]:
    """Get comprehensive system status including metrics, health, and alerts"""
    return {
        "timestamp": datetime.now().isoformat(),
        "metrics": metrics.get_all_metrics(),
        "health": health_check.run_all_checks(),
        "alerts": {
            "active": alert_manager.get_active_alerts(),
            "recent_history": alert_manager.get_alert_history()[-10:]  # Last 10 alerts
        }
    }

def export_metrics_to_json(file_path: str) -> bool:
    """Export current metrics to a JSON file"""
    try:
        with open(file_path, 'w') as f:
            json.dump(metrics.get_all_metrics(), f, indent=2)
        return True
    except Exception as e:
        logger.error(f"Error exporting metrics to JSON: {str(e)}")
        return False

# Decorator for monitoring API endpoints
def monitor_endpoint(endpoint_name: str):
    """Decorator to monitor API endpoint performance"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            
            try:
                result = func(*args, **kwargs)
                status = "success"
            except Exception as e:
                status = "error"
                raise
            finally:
                execution_time = time.time() - start_time
                
                # Record metrics
                metrics.record_api_metric(f"{endpoint_name}_execution_time", execution_time)
                metrics.record_api_metric(f"{endpoint_name}_status", status)
                
                # Update request count
                current_count = metrics.metrics["api"].get(f"{endpoint_name}_request_count", {"value": 0})["value"]
                metrics.record_api_metric(f"{endpoint_name}_request_count", current_count + 1)
            
            return result
        return wrapper
    return decorator

# Initialize monitoring on module import
initialize_monitoring()
