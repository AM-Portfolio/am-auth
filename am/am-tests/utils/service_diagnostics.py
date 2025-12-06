"""
Service Diagnostics Utility Module
Programmatic access to system health checks, service status, and diagnostics
Used for testing and monitoring the entire AM system
"""

import requests
import asyncio
import json
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
import sys
from pathlib import Path


@dataclass
class ServiceStatus:
    """Service health status"""
    name: str
    status: str  # online, offline, degraded
    response_time_ms: Optional[float] = None
    error: Optional[str] = None


@dataclass
class SystemHealth:
    """Complete system health report"""
    timestamp: str
    overall_status: str  # healthy, degraded, unhealthy
    services_up: int
    services_down: int
    services: List[ServiceStatus]
    database_connected: bool


class ServiceDiagnostics:
    """
    Programmatic interface to test and verify system health
    Use this in your Python test scripts
    """
    
    def __init__(self, gateway_url: str = "http://localhost:8000", auth_token: Optional[str] = None):
        """
        Initialize diagnostics client
        
        Args:
            gateway_url: API Gateway URL
            auth_token: Optional JWT authentication token
        """
        self.gateway_url = gateway_url.rstrip("/")
        self.auth_token = auth_token
        self.headers = self._build_headers()
    
    def _build_headers(self) -> Dict[str, str]:
        """Build request headers with authentication if available"""
        headers = {"Content-Type": "application/json"}
        if self.auth_token:
            headers["Authorization"] = f"Bearer {self.auth_token}"
        return headers
    
    def get_system_health(self) -> Dict[str, Any]:
        """
        Get complete system health diagnostics
        
        Returns:
            Dict with complete health report including all services and database status
        
        Raises:
            requests.RequestException: If request fails
        """
        url = f"{self.gateway_url}/api/v1/system/health"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json()
    
    def get_services_status(self) -> Dict[str, Any]:
        """
        Get quick status of all services
        
        Returns:
            Dict with services count and status details
        """
        url = f"{self.gateway_url}/api/v1/system/services/status"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json()
    
    def get_database_status(self) -> Dict[str, Any]:
        """
        Get database connectivity status
        
        Returns:
            Dict with database connection details
        """
        url = f"{self.gateway_url}/api/v1/system/database/status"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json()
    
    def get_python_scripts_status(self) -> Dict[str, Any]:
        """
        Get status of all Python test scripts
        
        Returns:
            Dict with available Python test scripts
        """
        url = f"{self.gateway_url}/api/v1/system/python-scripts/status"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json()
    
    def get_system_info(self) -> Dict[str, Any]:
        """
        Get system information and available endpoints
        
        Returns:
            Dict with system info and diagnostics endpoints
        """
        url = f"{self.gateway_url}/api/v1/system/info"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json()
    
    def run_full_diagnostics(self, include_python_tests: bool = True) -> Dict[str, Any]:
        """
        Run complete system diagnostics
        
        Args:
            include_python_tests: Whether to check Python test scripts
        
        Returns:
            Dict with full diagnostics report including execution time
        """
        url = f"{self.gateway_url}/api/v1/system/diagnostics/run"
        params = {"include_python_tests": include_python_tests}
        response = requests.post(url, headers=self.headers, params=params)
        response.raise_for_status()
        return response.json()
    
    def assert_all_services_up(self, fail_on_degraded: bool = False) -> bool:
        """
        Assert that all services are online
        
        Args:
            fail_on_degraded: If True, also fail if any service is degraded
        
        Returns:
            True if all services are up
        
        Raises:
            AssertionError: If any service is down or degraded (depending on fail_on_degraded)
        """
        status = self.get_services_status()
        services_down = status.get("services_down", 0)
        services_degraded = status.get("services_degraded", 0) if fail_on_degraded else 0
        
        message = f"Services down: {services_down}, degraded: {services_degraded}"
        assert services_down == 0 and services_degraded == 0, message
        
        return True
    
    def assert_database_connected(self) -> bool:
        """
        Assert that database is connected
        
        Returns:
            True if database is connected
        
        Raises:
            AssertionError: If database is not connected
        """
        status = self.get_database_status()
        db_status = status.get("database", {})
        connection_status = db_status.get("connection_status", "unknown")
        
        assert connection_status == "connected", f"Database connection status: {connection_status}"
        return True
    
    def get_services_count(self) -> Dict[str, int]:
        """
        Get count of services up, down, and degraded
        
        Returns:
            Dict with counts of each service status
        """
        status = self.get_services_status()
        return {
            "total": status.get("total_services", 0),
            "up": status.get("services_up", 0),
            "down": status.get("services_down", 0),
            "degraded": status.get("services_degraded", 0)
        }
    
    def print_health_report(self):
        """Print a formatted health report"""
        try:
            health = self.get_system_health()
            
            print("\n" + "="*70)
            print("SYSTEM DIAGNOSTICS REPORT")
            print("="*70)
            print(f"Timestamp: {health.get('timestamp')}")
            print(f"Overall Status: {health.get('overall_status').upper()}")
            print(f"Services: {health.get('services_up')}/{health.get('total_services')} online")
            print(f"Database: {health.get('database', {}).get('connection_status')}")
            
            print("\nService Status:")
            for service in health.get('services', []):
                status_icon = "✅" if service.get('status') == 'online' else "❌"
                response_time = service.get('response_time_ms')
                time_str = f" ({response_time}ms)" if response_time else ""
                print(f"  {status_icon} {service.get('service_name')}: {service.get('status')}{time_str}")
                if service.get('error'):
                    print(f"     Error: {service.get('error')}")
            
            print("\n" + "="*70 + "\n")
            
        except Exception as e:
            print(f"\n❌ Error generating health report: {e}\n")


# ============================================================================
# Utility Functions for Testing
# ============================================================================

def create_diagnostics_client(token: Optional[str] = None) -> ServiceDiagnostics:
    """Factory function to create a diagnostics client"""
    return ServiceDiagnostics(auth_token=token)


def test_all_services(diagnostics: ServiceDiagnostics) -> bool:
    """
    Test all services and return True if all are online
    
    Usage in your tests:
        diagnostics = create_diagnostics_client()
        if test_all_services(diagnostics):
            print("All services are up!")
    """
    services_count = diagnostics.get_services_count()
    print(f"✅ Services: {services_count['up']}/{services_count['total']} online")
    return services_count['down'] == 0


def test_database_connection(diagnostics: ServiceDiagnostics) -> bool:
    """
    Test database connection
    
    Usage in your tests:
        if test_database_connection(diagnostics):
            print("Database is connected!")
    """
    try:
        status = diagnostics.get_database_status()
        db_status = status.get("database", {})
        is_connected = db_status.get("connection_status") == "connected"
        
        if is_connected:
            response_time = db_status.get("response_time_ms", "N/A")
            print(f"✅ Database connected ({response_time}ms)")
        else:
            error = db_status.get("error", "Unknown error")
            print(f"❌ Database disconnected: {error}")
        
        return is_connected
    except Exception as e:
        print(f"❌ Error checking database: {e}")
        return False


def test_inter_service_communication(diagnostics: ServiceDiagnostics) -> bool:
    """
    Test that services can communicate with each other
    All services should be online for proper inter-service communication
    
    Usage in your tests:
        if test_inter_service_communication(diagnostics):
            print("Services can communicate!")
    """
    services_count = diagnostics.get_services_count()
    all_up = services_count['down'] == 0 and services_count['degraded'] == 0
    
    if all_up:
        print(f"✅ All {services_count['total']} services online - communication possible")
    else:
        print(f"⚠️  Some services not responding: {services_count['down']} down, {services_count['degraded']} degraded")
    
    return all_up


# ============================================================================
# Example usage (can be run directly for testing)
# ============================================================================

if __name__ == "__main__":
    print("AM System Diagnostics Client")
    print("="*70)
    
    try:
        # Create diagnostics client
        diagnostics = ServiceDiagnostics(gateway_url="http://localhost:8000")
        
        print("\n1️⃣ Getting system info...")
        info = diagnostics.get_system_info()
        print(f"   System: {info.get('system')} v{info.get('version')}")
        
        print("\n2️⃣ Checking services status...")
        test_all_services(diagnostics)
        
        print("\n3️⃣ Checking database connection...")
        test_database_connection(diagnostics)
        
        print("\n4️⃣ Checking inter-service communication...")
        test_inter_service_communication(diagnostics)
        
        print("\n5️⃣ Printing full health report...")
        diagnostics.print_health_report()
        
        print("\n✅ Diagnostics complete!")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)
