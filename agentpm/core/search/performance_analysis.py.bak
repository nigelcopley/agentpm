"""
Search Performance Analysis

Analyzes current search implementation performance and identifies bottlenecks
for FTS5 migration planning.
"""

import time
import sqlite3
from typing import Dict, List, Any, Tuple
from datetime import datetime
import statistics
from dataclasses import dataclass

from ..database.service import DatabaseService
from ..database.enums import EntityType
from .service import SearchService
from .models import SearchQuery, SearchScope


@dataclass
class SearchBenchmark:
    """Search performance benchmark result."""
    query: str
    entity_type: str
    execution_time_ms: float
    result_count: int
    avg_relevance: float
    search_method: str


class SearchPerformanceAnalyzer:
    """Analyzes search performance across different entity types and queries."""
    
    def __init__(self, db_service: DatabaseService):
        self.db_service = db_service
        self.search_service = SearchService(db_service)
        self.benchmarks: List[SearchBenchmark] = []
    
    def analyze_current_search_performance(self) -> Dict[str, Any]:
        """
        Analyze current search implementation performance.
        
        Returns:
            Performance analysis report
        """
        print("🔍 Analyzing current search performance...")
        
        # Test queries of varying complexity
        test_queries = [
            "oauth",           # Simple term
            "authentication",  # Common term
            "database schema", # Multi-word
            "user management system", # Complex phrase
            "api endpoint validation", # Technical phrase
            "project configuration", # Business term
        ]
        
        # Test different entity scopes (only available ones)
        entity_scopes = [
            SearchScope.ALL,
            SearchScope.WORK_ITEMS,
            SearchScope.TASKS,
            SearchScope.IDEAS,
        ]
        
        # Run benchmarks
        for query in test_queries:
            for scope in entity_scopes:
                self._benchmark_search(query, scope, "current_like")
        
        # Analyze results
        return self._generate_performance_report()
    
    def _benchmark_search(self, query: str, scope: SearchScope, method: str) -> None:
        """Run a single search benchmark."""
        try:
            start_time = time.time()
            
            search_query = SearchQuery(
                query=query,
                scope=scope,
                limit=50
            )
            
            results = self.search_service.search(search_query)
            
            execution_time_ms = (time.time() - start_time) * 1000
            
            avg_relevance = (
                sum(r.relevance_score for r in results.results) / len(results.results)
                if results.results else 0.0
            )
            
            benchmark = SearchBenchmark(
                query=query,
                entity_type=scope.value,
                execution_time_ms=execution_time_ms,
                result_count=len(results.results),
                avg_relevance=avg_relevance,
                search_method=method
            )
            
            self.benchmarks.append(benchmark)
            
            print(f"  ✓ {query} ({scope.value}): {execution_time_ms:.1f}ms, {len(results.results)} results")
            
        except Exception as e:
            print(f"  ✗ {query} ({scope.value}): Error - {e}")
    
    def _generate_performance_report(self) -> Dict[str, Any]:
        """Generate comprehensive performance report."""
        if not self.benchmarks:
            return {"error": "No benchmarks collected"}
        
        # Group by entity type
        by_entity = {}
        for benchmark in self.benchmarks:
            entity = benchmark.entity_type
            if entity not in by_entity:
                by_entity[entity] = []
            by_entity[entity].append(benchmark)
        
        # Calculate statistics
        all_times = [b.execution_time_ms for b in self.benchmarks]
        all_relevance = [b.avg_relevance for b in self.benchmarks]
        all_results = [b.result_count for b in self.benchmarks]
        
        report = {
            "summary": {
                "total_benchmarks": len(self.benchmarks),
                "avg_execution_time_ms": statistics.mean(all_times),
                "median_execution_time_ms": statistics.median(all_times),
                "max_execution_time_ms": max(all_times),
                "min_execution_time_ms": min(all_times),
                "avg_relevance_score": statistics.mean(all_relevance),
                "avg_result_count": statistics.mean(all_results),
            },
            "by_entity_type": {},
            "performance_issues": [],
            "recommendations": []
        }
        
        # Analyze by entity type
        for entity, benchmarks in by_entity.items():
            times = [b.execution_time_ms for b in benchmarks]
            relevance = [b.avg_relevance for b in benchmarks]
            
            report["by_entity_type"][entity] = {
                "benchmark_count": len(benchmarks),
                "avg_execution_time_ms": statistics.mean(times),
                "max_execution_time_ms": max(times),
                "avg_relevance_score": statistics.mean(relevance),
                "avg_result_count": statistics.mean([b.result_count for b in benchmarks])
            }
        
        # Identify performance issues
        slow_threshold = 1000  # 1 second
        low_relevance_threshold = 0.3
        
        for benchmark in self.benchmarks:
            if benchmark.execution_time_ms > slow_threshold:
                report["performance_issues"].append({
                    "type": "slow_query",
                    "query": benchmark.query,
                    "entity_type": benchmark.entity_type,
                    "execution_time_ms": benchmark.execution_time_ms,
                    "threshold": slow_threshold
                })
            
            if benchmark.avg_relevance < low_relevance_threshold:
                report["performance_issues"].append({
                    "type": "low_relevance",
                    "query": benchmark.query,
                    "entity_type": benchmark.entity_type,
                    "avg_relevance": benchmark.avg_relevance,
                    "threshold": low_relevance_threshold
                })
        
        # Generate recommendations
        if report["summary"]["avg_execution_time_ms"] > 500:
            report["recommendations"].append({
                "priority": "high",
                "issue": "Slow search performance",
                "recommendation": "Implement FTS5 for faster full-text search",
                "expected_improvement": "10-100x faster queries"
            })
        
        if report["summary"]["avg_relevance_score"] < 0.5:
            report["recommendations"].append({
                "priority": "medium",
                "issue": "Poor relevance scoring",
                "recommendation": "Use FTS5 ranking algorithms",
                "expected_improvement": "Better result ranking and relevance"
            })
        
        if len(report["performance_issues"]) > 5:
            report["recommendations"].append({
                "priority": "high",
                "issue": "Multiple performance issues detected",
                "recommendation": "Comprehensive search system overhaul with FTS5",
                "expected_improvement": "Significant performance and relevance improvements"
            })
        
        return report
    
    def analyze_database_structure(self) -> Dict[str, Any]:
        """Analyze current database structure for search optimization."""
        print("📊 Analyzing database structure...")
        
        analysis = {
            "tables": {},
            "indexes": {},
            "search_optimization_opportunities": []
        }
        
        with self.db_service.connect() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Get table information
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]
            
            for table in tables:
                # Get table schema
                cursor.execute(f"PRAGMA table_info({table})")
                columns = cursor.fetchall()
                
                # Get row count
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                row_count = cursor.fetchone()[0]
                
                # Get table size
                cursor.execute(f"SELECT COUNT(*) FROM pragma_table_info('{table}')")
                column_count = cursor.fetchone()[0]
                
                analysis["tables"][table] = {
                    "row_count": row_count,
                    "column_count": column_count,
                    "columns": [{"name": col[1], "type": col[2]} for col in columns]
                }
                
                # Check for searchable text columns
                text_columns = [
                    col[1] for col in columns 
                    if col[2].upper() in ['TEXT', 'VARCHAR', 'CHAR']
                ]
                
                if text_columns and row_count > 100:
                    analysis["search_optimization_opportunities"].append({
                        "table": table,
                        "text_columns": text_columns,
                        "row_count": row_count,
                        "recommendation": f"Create FTS5 virtual table for {table}",
                        "priority": "high" if row_count > 1000 else "medium"
                    })
            
            # Get index information
            cursor.execute("SELECT name, sql FROM sqlite_master WHERE type='index'")
            indexes = cursor.fetchall()
            
            for index_name, index_sql in indexes:
                analysis["indexes"][index_name] = {
                    "sql": index_sql
                }
        
        return analysis
    
    def generate_baseline_report(self) -> Dict[str, Any]:
        """Generate comprehensive baseline performance report."""
        print("📈 Generating baseline performance report...")
        
        performance_report = self.analyze_current_search_performance()
        structure_report = self.analyze_database_structure()
        
        baseline_report = {
            "timestamp": datetime.now().isoformat(),
            "analysis_type": "search_performance_baseline",
            "performance": performance_report,
            "database_structure": structure_report,
            "fts5_migration_readiness": self._assess_fts5_readiness(performance_report, structure_report)
        }
        
        return baseline_report
    
    def _assess_fts5_readiness(self, performance: Dict[str, Any], structure: Dict[str, Any]) -> Dict[str, Any]:
        """Assess readiness for FTS5 migration."""
        readiness = {
            "overall_score": 0,
            "factors": {},
            "recommendations": []
        }
        
        # Factor 1: Performance issues
        performance_score = 0
        if performance.get("summary", {}).get("avg_execution_time_ms", 0) > 500:
            performance_score += 40
        if len(performance.get("performance_issues", [])) > 3:
            performance_score += 30
        if performance.get("summary", {}).get("avg_relevance_score", 0) < 0.5:
            performance_score += 30
        
        readiness["factors"]["performance_issues"] = {
            "score": performance_score,
            "max_score": 100,
            "description": "Current search performance problems"
        }
        
        # Factor 2: Database structure
        structure_score = 0
        searchable_tables = len(structure.get("search_optimization_opportunities", []))
        if searchable_tables > 5:
            structure_score += 50
        elif searchable_tables > 2:
            structure_score += 30
        
        readiness["factors"]["database_structure"] = {
            "score": structure_score,
            "max_score": 50,
            "description": "Database structure suitability for FTS5"
        }
        
        # Factor 3: Search complexity
        complexity_score = 0
        if performance.get("summary", {}).get("total_benchmarks", 0) > 20:
            complexity_score += 25
        if len(performance.get("by_entity_type", {})) > 3:
            complexity_score += 25
        
        readiness["factors"]["search_complexity"] = {
            "score": complexity_score,
            "max_score": 50,
            "description": "Search system complexity"
        }
        
        # Calculate overall score
        total_score = performance_score + structure_score + complexity_score
        max_total = 200
        readiness["overall_score"] = (total_score / max_total) * 100
        
        # Generate recommendations
        if readiness["overall_score"] > 70:
            readiness["recommendations"].append({
                "priority": "high",
                "action": "Proceed with FTS5 migration",
                "reason": "Strong indicators for search system improvement"
            })
        elif readiness["overall_score"] > 40:
            readiness["recommendations"].append({
                "priority": "medium",
                "action": "Plan FTS5 migration with careful testing",
                "reason": "Moderate benefits expected"
            })
        else:
            readiness["recommendations"].append({
                "priority": "low",
                "action": "Consider incremental improvements first",
                "reason": "Limited immediate benefits from FTS5 migration"
            })
        
        return readiness


def run_performance_analysis(db_service: DatabaseService) -> Dict[str, Any]:
    """Run complete search performance analysis."""
    analyzer = SearchPerformanceAnalyzer(db_service)
    return analyzer.generate_baseline_report()


if __name__ == "__main__":
    # Example usage
    from ..database.service import DatabaseService
    
    db_service = DatabaseService("/path/to/database.db")
    report = run_performance_analysis(db_service)
    
    print("📊 Search Performance Analysis Report")
    print("=" * 50)
    print(f"Overall FTS5 Readiness Score: {report['fts5_migration_readiness']['overall_score']:.1f}%")
    print(f"Average Search Time: {report['performance']['summary']['avg_execution_time_ms']:.1f}ms")
    print(f"Average Relevance Score: {report['performance']['summary']['avg_relevance_score']:.3f}")
    print(f"Performance Issues Found: {len(report['performance']['performance_issues'])}")
    print(f"Searchable Tables: {len(report['database_structure']['search_optimization_opportunities'])}")
