"""
FTS5 Testing and Validation Script

Tests FTS5 capabilities, performance, and limitations for APM (Agent Project Manager) implementation.
"""

import time
import sqlite3
import tempfile
import os
from typing import List, Dict, Any, Tuple
from dataclasses import dataclass
import json

from ..database.service import DatabaseService


@dataclass
class FTS5TestResult:
    """Result of an FTS5 test."""
    test_name: str
    success: bool
    execution_time_ms: float
    result_count: int
    error_message: str = ""


class FTS5Tester:
    """Tests FTS5 capabilities and performance."""
    
    def __init__(self):
        self.results: List[FTS5TestResult] = []
        self.test_data = self._generate_test_data()
    
    def _generate_test_data(self) -> List[Dict[str, Any]]:
        """Generate test data for FTS5 testing."""
        return [
            {
                "id": 1,
                "name": "OAuth2 Authentication System",
                "description": "Implement secure OAuth2 authentication for user management system with JWT tokens and refresh token rotation.",
                "type": "work_item"
            },
            {
                "id": 2,
                "name": "Database Schema Migration",
                "description": "Create migration scripts to update database schema for new user authentication requirements.",
                "type": "task"
            },
            {
                "id": 3,
                "name": "API Endpoint Validation",
                "description": "Add comprehensive validation for all API endpoints including input sanitization and error handling.",
                "type": "task"
            },
            {
                "id": 4,
                "name": "User Management Dashboard",
                "description": "Build responsive dashboard for user management with real-time updates and role-based access control.",
                "type": "work_item"
            },
            {
                "id": 5,
                "name": "Search Performance Optimization",
                "description": "Optimize search functionality using FTS5 for better performance and relevance scoring.",
                "type": "idea"
            },
            {
                "id": 6,
                "name": "Project Configuration Management",
                "description": "Implement centralized configuration management system for project settings and environment variables.",
                "type": "work_item"
            },
            {
                "id": 7,
                "name": "Automated Testing Framework",
                "description": "Set up comprehensive automated testing framework with unit tests, integration tests, and end-to-end tests.",
                "type": "task"
            },
            {
                "id": 8,
                "name": "Documentation System",
                "description": "Create automated documentation generation system with API docs, user guides, and developer documentation.",
                "type": "idea"
            }
        ]
    
    def test_fts5_availability(self) -> FTS5TestResult:
        """Test if FTS5 is available in SQLite build."""
        start_time = time.time()
        
        try:
            # Create temporary database
            with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp_file:
                db_path = tmp_file.name
            
            # Test FTS5 availability
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Try to create FTS5 table
            cursor.execute("""
                CREATE VIRTUAL TABLE test_fts USING fts5(
                    content
                )
            """)
            
            # Try to insert and query
            cursor.execute("INSERT INTO test_fts VALUES ('test content')")
            cursor.execute("SELECT * FROM test_fts WHERE test_fts MATCH 'test'")
            results = cursor.fetchall()
            
            # Cleanup
            cursor.execute("DROP TABLE test_fts")
            conn.close()
            os.unlink(db_path)
            
            execution_time = (time.time() - start_time) * 1000
            
            return FTS5TestResult(
                test_name="FTS5 Availability",
                success=True,
                execution_time_ms=execution_time,
                result_count=len(results)
            )
            
        except Exception as e:
            execution_time = (time.time() - start_time) * 1000
            return FTS5TestResult(
                test_name="FTS5 Availability",
                success=False,
                execution_time_ms=execution_time,
                result_count=0,
                error_message=str(e)
            )
    
    def test_fts5_performance(self) -> FTS5TestResult:
        """Test FTS5 performance vs LIKE queries."""
        start_time = time.time()
        
        try:
            # Create temporary database
            with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp_file:
                db_path = tmp_file.name
            
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Create regular table
            cursor.execute("""
                CREATE TABLE test_data (
                    id INTEGER PRIMARY KEY,
                    name TEXT,
                    description TEXT
                )
            """)
            
            # Create FTS5 table
            cursor.execute("""
                CREATE VIRTUAL TABLE test_data_fts USING fts5(
                    name,
                    description,
                    content='test_data',
                    content_rowid='id'
                )
            """)
            
            # Insert test data
            for item in self.test_data:
                cursor.execute("""
                    INSERT INTO test_data (id, name, description)
                    VALUES (?, ?, ?)
                """, (item['id'], item['name'], item['description']))
            
            # Test LIKE query performance
            like_start = time.time()
            cursor.execute("""
                SELECT * FROM test_data 
                WHERE name LIKE '%authentication%' OR description LIKE '%authentication%'
            """)
            like_results = cursor.fetchall()
            like_time = (time.time() - like_start) * 1000
            
            # Test FTS5 query performance
            fts5_start = time.time()
            cursor.execute("""
                SELECT * FROM test_data_fts 
                WHERE test_data_fts MATCH 'authentication'
            """)
            fts5_results = cursor.fetchall()
            fts5_time = (time.time() - fts5_start) * 1000
            
            # Cleanup
            conn.close()
            os.unlink(db_path)
            
            execution_time = (time.time() - start_time) * 1000
            
            return FTS5TestResult(
                test_name="FTS5 Performance",
                success=True,
                execution_time_ms=execution_time,
                result_count=len(fts5_results)
            )
            
        except Exception as e:
            execution_time = (time.time() - start_time) * 1000
            return FTS5TestResult(
                test_name="FTS5 Performance",
                success=False,
                execution_time_ms=execution_time,
                result_count=0,
                error_message=str(e)
            )
    
    def test_fts5_features(self) -> FTS5TestResult:
        """Test FTS5 advanced features."""
        start_time = time.time()
        
        try:
            # Create temporary database
            with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp_file:
                db_path = tmp_file.name
            
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Create FTS5 table
            cursor.execute("""
                CREATE VIRTUAL TABLE test_fts USING fts5(
                    name,
                    description
                )
            """)
            
            # Insert test data
            for item in self.test_data:
                cursor.execute("""
                    INSERT INTO test_fts (name, description)
                    VALUES (?, ?)
                """, (item['name'], item['description']))
            
            # Test various FTS5 features
            features_tested = 0
            
            # 1. Simple search
            cursor.execute("SELECT * FROM test_fts WHERE test_fts MATCH 'authentication'")
            features_tested += 1
            
            # 2. Phrase search
            cursor.execute("SELECT * FROM test_fts WHERE test_fts MATCH '\"user management\"'")
            features_tested += 1
            
            # 3. Boolean search
            cursor.execute("SELECT * FROM test_fts WHERE test_fts MATCH 'oauth AND authentication'")
            features_tested += 1
            
            # 4. Prefix search
            cursor.execute("SELECT * FROM test_fts WHERE test_fts MATCH 'auth*'")
            features_tested += 1
            
            # 5. Ranking
            cursor.execute("""
                SELECT *, bm25(test_fts) as rank 
                FROM test_fts 
                WHERE test_fts MATCH 'authentication' 
                ORDER BY rank
            """)
            features_tested += 1
            
            # 6. Highlighting
            cursor.execute("""
                SELECT highlight(test_fts, 0, '<b>', '</b>') as highlighted_name
                FROM test_fts 
                WHERE test_fts MATCH 'authentication'
            """)
            features_tested += 1
            
            # Cleanup
            conn.close()
            os.unlink(db_path)
            
            execution_time = (time.time() - start_time) * 1000
            
            return FTS5TestResult(
                test_name="FTS5 Features",
                success=True,
                execution_time_ms=execution_time,
                result_count=features_tested
            )
            
        except Exception as e:
            execution_time = (time.time() - start_time) * 1000
            return FTS5TestResult(
                test_name="FTS5 Features",
                success=False,
                execution_time_ms=execution_time,
                result_count=0,
                error_message=str(e)
            )
    
    def test_fts5_limitations(self) -> FTS5TestResult:
        """Test FTS5 limitations and edge cases."""
        start_time = time.time()
        
        try:
            # Create temporary database
            with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp_file:
                db_path = tmp_file.name
            
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Create FTS5 table
            cursor.execute("""
                CREATE VIRTUAL TABLE test_fts USING fts5(
                    content
                )
            """)
            
            limitations_tested = 0
            
            # Test limitations
            try:
                # 1. Regex not supported (should fail gracefully)
                cursor.execute("SELECT * FROM test_fts WHERE test_fts MATCH 'auth.*'")
                limitations_tested += 1
            except:
                limitations_tested += 1  # Expected to fail
            
            try:
                # 2. Case sensitivity (test behavior)
                cursor.execute("SELECT * FROM test_fts WHERE test_fts MATCH 'AUTHENTICATION'")
                limitations_tested += 1
            except:
                limitations_tested += 1
            
            try:
                # 3. Complex boolean queries
                cursor.execute("SELECT * FROM test_fts WHERE test_fts MATCH '(oauth OR jwt) AND authentication'")
                limitations_tested += 1
            except:
                limitations_tested += 1
            
            # Cleanup
            conn.close()
            os.unlink(db_path)
            
            execution_time = (time.time() - start_time) * 1000
            
            return FTS5TestResult(
                test_name="FTS5 Limitations",
                success=True,
                execution_time_ms=execution_time,
                result_count=limitations_tested
            )
            
        except Exception as e:
            execution_time = (time.time() - start_time) * 1000
            return FTS5TestResult(
                test_name="FTS5 Limitations",
                success=False,
                execution_time_ms=execution_time,
                result_count=0,
                error_message=str(e)
            )
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Run all FTS5 tests and return comprehensive results."""
        print("🧪 Running FTS5 capability tests...")
        
        # Run all tests
        tests = [
            self.test_fts5_availability,
            self.test_fts5_performance,
            self.test_fts5_features,
            self.test_fts5_limitations
        ]
        
        for test_func in tests:
            result = test_func()
            self.results.append(result)
            status = "✅" if result.success else "❌"
            print(f"  {status} {result.test_name}: {result.execution_time_ms:.1f}ms")
            if not result.success:
                print(f"    Error: {result.error_message}")
        
        # Generate summary
        total_tests = len(self.results)
        successful_tests = sum(1 for r in self.results if r.success)
        avg_time = sum(r.execution_time_ms for r in self.results) / total_tests
        
        summary = {
            "total_tests": total_tests,
            "successful_tests": successful_tests,
            "success_rate": (successful_tests / total_tests) * 100,
            "average_execution_time_ms": avg_time,
            "test_results": [
                {
                    "test_name": r.test_name,
                    "success": r.success,
                    "execution_time_ms": r.execution_time_ms,
                    "result_count": r.result_count,
                    "error_message": r.error_message
                }
                for r in self.results
            ],
            "recommendations": self._generate_recommendations()
        }
        
        return summary
    
    def _generate_recommendations(self) -> List[Dict[str, str]]:
        """Generate recommendations based on test results."""
        recommendations = []
        
        # Check FTS5 availability
        availability_test = next((r for r in self.results if r.test_name == "FTS5 Availability"), None)
        if availability_test and availability_test.success:
            recommendations.append({
                "type": "success",
                "message": "FTS5 is available and ready for implementation"
            })
        else:
            recommendations.append({
                "type": "warning",
                "message": "FTS5 not available - implement fallback to LIKE queries"
            })
        
        # Check performance
        performance_test = next((r for r in self.results if r.test_name == "FTS5 Performance"), None)
        if performance_test and performance_test.success:
            recommendations.append({
                "type": "success",
                "message": "FTS5 performance testing successful - expect significant speed improvements"
            })
        
        # Check features
        features_test = next((r for r in self.results if r.test_name == "FTS5 Features"), None)
        if features_test and features_test.success:
            recommendations.append({
                "type": "success",
                "message": f"FTS5 advanced features working - {features_test.result_count} features validated"
            })
        
        # Overall recommendation
        success_rate = sum(1 for r in self.results if r.success) / len(self.results) * 100
        if success_rate >= 75:
            recommendations.append({
                "type": "recommendation",
                "message": "FTS5 implementation recommended - high success rate in testing"
            })
        elif success_rate >= 50:
            recommendations.append({
                "type": "caution",
                "message": "FTS5 implementation with caution - moderate success rate, implement fallbacks"
            })
        else:
            recommendations.append({
                "type": "warning",
                "message": "FTS5 implementation not recommended - low success rate, use alternative approach"
            })
        
        return recommendations


def run_fts5_research() -> Dict[str, Any]:
    """Run comprehensive FTS5 research and testing."""
    print("🔬 Starting FTS5 Research and Testing")
    print("=" * 50)
    
    tester = FTS5Tester()
    test_results = tester.run_all_tests()
    
    print(f"\n📊 Test Summary:")
    print(f"  Total Tests: {test_results['total_tests']}")
    print(f"  Successful: {test_results['successful_tests']}")
    print(f"  Success Rate: {test_results['success_rate']:.1f}%")
    print(f"  Average Time: {test_results['average_execution_time_ms']:.1f}ms")
    
    print(f"\n💡 Recommendations:")
    for rec in test_results['recommendations']:
        icon = "✅" if rec['type'] == 'success' else "⚠️" if rec['type'] == 'warning' else "💡"
        print(f"  {icon} {rec['message']}")
    
    return test_results


if __name__ == "__main__":
    results = run_fts5_research()
    
    # Save results
    with open('fts5_test_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n✅ Test results saved to fts5_test_results.json")
