"""
System Health Integration Tests
Comprehensive test suite for AM system diagnostics
Tests all services, database, and inter-service communication

Run with: pytest test_system_health.py -v
Or directly: python test_system_health.py
"""

import sys
import time
from pathlib import Path

# Add utils to path for importing service_diagnostics
sys.path.insert(0, str(Path(__file__).parent.parent / "utils"))

from service_diagnostics import (
    ServiceDiagnostics,
    create_diagnostics_client,
    test_all_services,
    test_database_connection,
    test_inter_service_communication
)

import pytest


class TestSystemDiagnostics:
    """Test suite for system diagnostics using pytest"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup diagnostics client before each test"""
        self.diagnostics = create_diagnostics_client()
        self.timeout_seconds = 30
    
    def test_api_gateway_responds(self):
        """Test that API Gateway is responding"""
        info = self.diagnostics.get_system_info()
        assert info is not None
        assert "system" in info
        print("✅ API Gateway responding")
    
    def test_all_services_status(self):
        """Test that we can get status of all services"""
        status = self.diagnostics.get_services_status()
        assert "services" in status
        assert "total_services" in status
        assert "services_up" in status
        print(f"✅ Services status: {status['services_up']}/{status['total_services']} online")
    
    def test_services_are_online(self):
        """Test that all critical services are online"""
        status = self.diagnostics.get_services_status()
        services_down = status.get("services_down", 1)
        assert services_down == 0, f"{services_down} services are offline"
        print(f"✅ All services online: {status['services_up']}/{status['total_services']}")
    
    def test_database_connection(self):
        """Test database connectivity"""
        status = self.diagnostics.get_database_status()
        db = status.get("database", {})
        connection_status = db.get("connection_status")
        assert connection_status == "connected", f"Database not connected: {connection_status}"
        print(f"✅ Database connected ({db.get('response_time_ms')}ms)")
    
    def test_python_scripts_available(self):
        """Test that Python test scripts are available"""
        status = self.diagnostics.get_python_scripts_status()
        available = status.get("available_scripts", 0)
        assert available > 0, "No Python test scripts found"
        print(f"✅ Python scripts available: {available}/{status['total_scripts']}")
    
    def test_full_diagnostics(self):
        """Test complete diagnostics run"""
        result = self.diagnostics.run_full_diagnostics()
        assert "diagnostics" in result
        assert "check_completed_in_seconds" in result
        
        diagnostics = result["diagnostics"]
        assert diagnostics["overall_status"] in ["healthy", "degraded", "unhealthy"]
        
        duration = result["check_completed_in_seconds"]
        print(f"✅ Diagnostics completed in {duration:.3f} seconds")
    
    def test_inter_service_communication(self):
        """Test that services can communicate"""
        services_count = self.diagnostics.get_services_count()
        assert services_count['down'] == 0, f"{services_count['down']} services cannot communicate"
        print(f"✅ All services can communicate: {services_count['up']}/{services_count['total']}")
    
    def test_service_response_times(self):
        """Test that services respond within reasonable time"""
        status = self.diagnostics.get_services_status()
        
        for service in status.get("services", []):
            response_time = service.get("response_time_ms", 0)
            service_name = service.get("service_name")
            
            assert response_time < 5000, f"{service_name} response time {response_time}ms > 5 seconds"
            print(f"✅ {service_name}: {response_time}ms")
    
    def test_health_summary(self):
        """Test complete health summary"""
        health = self.diagnostics.get_system_health()
        
        assert health["overall_status"] in ["healthy", "degraded", "unhealthy"]
        assert health["services_up"] > 0
        assert len(health["services"]) > 0
        assert "database" in health
        
        print(f"\n✅ System Status: {health['overall_status'].upper()}")
        print(f"   Services: {health['services_up']}/{health['total_services']} online")
        print(f"   Database: {health['database']['connection_status']}")


class TestServiceHealth:
    """Test individual service health"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup diagnostics client"""
        self.diagnostics = create_diagnostics_client()
    
    def test_api_gateway_online(self):
        """Test API Gateway is online"""
        status = self.diagnostics.get_services_status()
        gateway = next((s for s in status["services"] if "Gateway" in s.get("service_name", "")), None)
        assert gateway is not None
        assert gateway["status"] == "online"
        print("✅ API Gateway online")
    
    def test_user_management_online(self):
        """Test User Management service is online"""
        status = self.diagnostics.get_services_status()
        service = next((s for s in status["services"] if "User" in s.get("service_name", "")), None)
        assert service is not None
        assert service["status"] == "online"
        print("✅ User Management service online")
    
    def test_auth_tokens_online(self):
        """Test Auth Tokens service is online"""
        status = self.diagnostics.get_services_status()
        service = next((s for s in status["services"] if "Auth" in s.get("service_name", "")), None)
        assert service is not None
        assert service["status"] == "online"
        print("✅ Auth Tokens service online")


class TestDatabaseHealth:
    """Test database specific health"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup diagnostics client"""
        self.diagnostics = create_diagnostics_client()
    
    def test_database_connected(self):
        """Test database is connected"""
        status = self.diagnostics.get_database_status()
        db = status["database"]
        assert db["connection_status"] == "connected"
        print("✅ Database connected")
    
    def test_database_response_time(self):
        """Test database responds quickly"""
        status = self.diagnostics.get_database_status()
        db = status["database"]
        response_time = db.get("response_time_ms", 0)
        
        assert response_time < 1000, f"Database response time {response_time}ms > 1 second"
        print(f"✅ Database response time: {response_time}ms")
    
    def test_database_has_tables(self):
        """Test database has expected tables"""
        status = self.diagnostics.get_database_status()
        db = status["database"]
        table_count = db.get("table_count")
        
        assert table_count is not None
        assert table_count > 0, "Database has no tables"
        print(f"✅ Database has {table_count} tables")


# ============================================================================
# Non-pytest entry point for direct execution
# ============================================================================

def print_colored(text: str, color: str = "white"):
    """Print colored text (ANSI colors)"""
    colors = {
        "green": "\033[92m",
        "red": "\033[91m",
        "yellow": "\033[93m",
        "blue": "\033[94m",
        "reset": "\033[0m"
    }
    print(f"{colors.get(color, '')}{text}{colors['reset']}")


def main():
    """Run all tests without pytest"""
    print_colored("\n" + "="*70, "blue")
    print_colored("AM SYSTEM HEALTH TEST SUITE", "blue")
    print_colored("="*70 + "\n", "blue")
    
    diagnostics = create_diagnostics_client()
    
    passed = 0
    failed = 0
    
    tests = [
        ("API Gateway Response", lambda: diagnostics.get_system_info() is not None),
        ("Services Online", lambda: test_all_services(diagnostics)),
        ("Database Connection", lambda: test_database_connection(diagnostics)),
        ("Inter-Service Communication", lambda: test_inter_service_communication(diagnostics)),
    ]
    
    for test_name, test_func in tests:
        try:
            print(f"\nRunning: {test_name}...", end=" ")
            result = test_func()
            if result:
                print_colored("✅ PASS", "green")
                passed += 1
            else:
                print_colored("❌ FAIL", "red")
                failed += 1
        except Exception as e:
            print_colored(f"❌ ERROR: {e}", "red")
            failed += 1
    
    # Print full report
    print("\n" + "="*70)
    diagnostics.print_health_report()
    
    # Summary
    total = passed + failed
    print_colored(f"\n{'='*70}", "blue")
    print_colored(f"RESULTS: {passed}/{total} tests passed", "green" if failed == 0 else "yellow")
    print_colored(f"{'='*70}\n", "blue")
    
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    # Check if running with pytest
    if "pytest" in sys.modules:
        pytest.main([__file__, "-v"])
    else:
        sys.exit(main())
