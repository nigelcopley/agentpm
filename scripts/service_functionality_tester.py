#!/usr/bin/env python3
"""
Service Functionality Tester

Tests critical services to understand their current functionality
before Phase 2 consolidation. Focuses on the most connected services
identified in the dependency analysis.
"""

import sys
import json
import traceback
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
import sqlite3
import tempfile
import importlib.util

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "aipm-cli"))

class ServiceTester:
    """Test framework for AIPM services"""

    def __init__(self):
        self.test_results: Dict[str, Dict[str, Any]] = {}
        self.test_db_path: Optional[Path] = None
        self.setup_test_environment()

    def setup_test_environment(self):
        """Set up a temporary test environment"""
        # Create temporary test database
        temp_dir = Path(tempfile.mkdtemp())
        self.test_db_path = temp_dir / "test_pm.sqlite"

        # Initialize basic database structure if needed
        try:
            from aipm_cli.migrations.file_migration_manager import get_migration_manager
            manager = get_migration_manager(self.test_db_path)
            result = manager.migrate()
            print(f"✅ Test database initialized with {result['total_applied']} migrations")
        except Exception as e:
            print(f"⚠️ Could not initialize test database: {e}")

    def import_service_safely(self, module_path: str) -> Tuple[Any, Optional[str]]:
        """Safely import a service module"""
        try:
            module = __import__(module_path, fromlist=[''])
            return module, None
        except Exception as e:
            return None, str(e)

    def test_database_models(self) -> Dict[str, Any]:
        """Test the database models service"""
        result = {
            'service_name': 'database.models',
            'status': 'unknown',
            'classes_found': [],
            'functions_found': [],
            'test_results': {}
        }

        try:
            # Import models
            models_module, error = self.import_service_safely('aipm_cli.services.database.models')
            if error:
                result['status'] = 'import_failed'
                result['error'] = error
                return result

            # Check for key classes
            key_classes = [
                'Project', 'Task', 'Agent', 'Objective', 'Command', 'Event',
                'Question', 'Answer', 'ContextBundle', 'UnifiedContext'
            ]

            found_classes = []
            for class_name in key_classes:
                if hasattr(models_module, class_name):
                    found_classes.append(class_name)
                    cls = getattr(models_module, class_name)

                    # Test basic instantiation
                    try:
                        if class_name == 'Project':
                            instance = cls(
                                name="Test Project",
                                description="Test Description",
                                project_path="/test/path"
                            )
                            result['test_results'][f'{class_name}_instantiation'] = 'success'
                        elif class_name == 'Task':
                            instance = cls(
                                title="Test Task",
                                description="Test Description",
                                project_id=1
                            )
                            result['test_results'][f'{class_name}_instantiation'] = 'success'
                        # Add more class-specific tests-BAK as needed

                    except Exception as e:
                        result['test_results'][f'{class_name}_instantiation'] = f'failed: {str(e)}'

            result['classes_found'] = found_classes
            result['status'] = 'success' if found_classes else 'no_classes'

        except Exception as e:
            result['status'] = 'failed'
            result['error'] = str(e)
            result['traceback'] = traceback.format_exc()

        return result

    def test_database_router(self) -> Dict[str, Any]:
        """Test the database router service"""
        result = {
            'service_name': 'database_router',
            'status': 'unknown',
            'test_results': {}
        }

        try:
            router_module, error = self.import_service_safely('aipm_cli.services.database_router')
            if error:
                result['status'] = 'import_failed'
                result['error'] = error
                return result

            # Check for key functions/classes
            key_components = ['DatabaseRouter', 'get_database_service', 'route_query']
            found_components = []

            for component in key_components:
                if hasattr(router_module, component):
                    found_components.append(component)

            result['components_found'] = found_components

            # Test database router initialization if available
            if hasattr(router_module, 'DatabaseRouter'):
                try:
                    router_class = getattr(router_module, 'DatabaseRouter')
                    router_instance = router_class(str(self.test_db_path))
                    result['test_results']['router_initialization'] = 'success'
                except Exception as e:
                    result['test_results']['router_initialization'] = f'failed: {str(e)}'

            result['status'] = 'success' if found_components else 'no_components'

        except Exception as e:
            result['status'] = 'failed'
            result['error'] = str(e)
            result['traceback'] = traceback.format_exc()

        return result

    def test_context_services(self) -> Dict[str, Any]:
        """Test context-related services"""
        result = {
            'service_name': 'context_services',
            'status': 'unknown',
            'services_tested': {},
            'test_results': {}
        }

        context_services = [
            'aipm_cli.services.context.service',
            'aipm_cli.services.context_scorecard',
            'aipm_cli.services.context_confidence'
        ]

        for service_path in context_services:
            service_name = service_path.split('.')[-1]
            service_result = {
                'import_status': 'unknown',
                'classes_found': [],
                'functions_found': []
            }

            try:
                service_module, error = self.import_service_safely(service_path)
                if error:
                    service_result['import_status'] = 'failed'
                    service_result['error'] = error
                else:
                    service_result['import_status'] = 'success'

                    # Get module contents
                    for attr_name in dir(service_module):
                        attr = getattr(service_module, attr_name)
                        if isinstance(attr, type) and not attr_name.startswith('_'):
                            service_result['classes_found'].append(attr_name)
                        elif callable(attr) and not attr_name.startswith('_'):
                            service_result['functions_found'].append(attr_name)

            except Exception as e:
                service_result['import_status'] = 'failed'
                service_result['error'] = str(e)

            result['services_tested'][service_name] = service_result

        # Determine overall status
        successful_imports = sum(1 for s in result['services_tested'].values()
                               if s['import_status'] == 'success')
        total_services = len(result['services_tested'])

        if successful_imports == total_services:
            result['status'] = 'success'
        elif successful_imports > 0:
            result['status'] = 'partial_success'
        else:
            result['status'] = 'failed'

        result['success_rate'] = f"{successful_imports}/{total_services}"

        return result

    def test_business_services(self) -> Dict[str, Any]:
        """Test business logic services"""
        result = {
            'service_name': 'business_services',
            'status': 'unknown',
            'services_tested': {},
            'test_results': {}
        }

        business_services = [
            'aipm_cli.services.business.project_analysis_service',
            'aipm_cli.services.business.context_management_service',
            'aipm_cli.services.business.objective_management_service',
            'aipm_cli.services.business.task_management_service'
        ]

        for service_path in business_services:
            service_name = service_path.split('.')[-1]
            service_result = {
                'import_status': 'unknown',
                'main_classes': [],
                'key_methods': []
            }

            try:
                service_module, error = self.import_service_safely(service_path)
                if error:
                    service_result['import_status'] = 'failed'
                    service_result['error'] = error
                else:
                    service_result['import_status'] = 'success'

                    # Look for service classes (typically end with 'Service')
                    for attr_name in dir(service_module):
                        attr = getattr(service_module, attr_name)
                        if isinstance(attr, type) and attr_name.endswith('Service'):
                            service_result['main_classes'].append(attr_name)

                            # Get methods from service class
                            methods = [m for m in dir(attr) if not m.startswith('_') and callable(getattr(attr, m))]
                            service_result['key_methods'].extend(methods[:5])  # First 5 methods

            except Exception as e:
                service_result['import_status'] = 'failed'
                service_result['error'] = str(e)

            result['services_tested'][service_name] = service_result

        # Calculate success rate
        successful_imports = sum(1 for s in result['services_tested'].values()
                               if s['import_status'] == 'success')
        total_services = len(result['services_tested'])

        result['status'] = 'success' if successful_imports == total_services else 'partial_success'
        result['success_rate'] = f"{successful_imports}/{total_services}"

        return result

    def test_intelligence_services(self) -> Dict[str, Any]:
        """Test intelligence and detection services"""
        result = {
            'service_name': 'intelligence_services',
            'status': 'unknown',
            'services_tested': {},
            'detection_capabilities': {}
        }

        intelligence_services = [
            'aipm_cli.services.ecosystem_intelligence',
            'aipm_cli.services.objective_intelligence.service',
            'aipm_cli.services.agent_intelligence.service',
            'aipm_cli.services.questionnaire_detection'
        ]

        for service_path in intelligence_services:
            service_name = service_path.split('.')[-1]
            service_result = {
                'import_status': 'unknown',
                'detector_classes': [],
                'intelligence_methods': []
            }

            try:
                service_module, error = self.import_service_safely(service_path)
                if error:
                    service_result['import_status'] = 'failed'
                    service_result['error'] = error
                else:
                    service_result['import_status'] = 'success'

                    # Look for detector/intelligence classes
                    for attr_name in dir(service_module):
                        attr = getattr(service_module, attr_name)
                        if isinstance(attr, type):
                            if 'detector' in attr_name.lower() or 'intelligence' in attr_name.lower():
                                service_result['detector_classes'].append(attr_name)

                                # Get key methods
                                methods = [m for m in dir(attr)
                                         if not m.startswith('_') and callable(getattr(attr, m))]
                                service_result['intelligence_methods'].extend(methods[:3])

            except Exception as e:
                service_result['import_status'] = 'failed'
                service_result['error'] = str(e)

            result['services_tested'][service_name] = service_result

        # Calculate success rate
        successful_imports = sum(1 for s in result['services_tested'].values()
                               if s['import_status'] == 'success')
        total_services = len(result['services_tested'])

        result['status'] = 'success' if successful_imports == total_services else 'partial_success'
        result['success_rate'] = f"{successful_imports}/{total_services}"

        return result

    def run_comprehensive_test(self) -> Dict[str, Any]:
        """Run all service tests-BAK"""
        print("🧪 AIPM Service Functionality Testing")
        print("=" * 50)

        all_results = {
            'test_timestamp': '2024-09-24',
            'test_environment': {
                'test_db_path': str(self.test_db_path) if self.test_db_path else None,
                'python_path': sys.path[0]
            },
            'service_tests': {}
        }

        # Test critical services identified in dependency analysis
        test_functions = [
            ('database_models', self.test_database_models),
            ('database_router', self.test_database_router),
            ('context_services', self.test_context_services),
            ('business_services', self.test_business_services),
            ('intelligence_services', self.test_intelligence_services)
        ]

        for test_name, test_function in test_functions:
            print(f"\n🔍 Testing {test_name}...")
            try:
                result = test_function()
                all_results['service_tests'][test_name] = result

                status_emoji = {
                    'success': '✅',
                    'partial_success': '⚠️',
                    'failed': '❌',
                    'import_failed': '🚫'
                }.get(result['status'], '❓')

                print(f"   {status_emoji} {result['status']}")

                # Show key findings
                if 'classes_found' in result:
                    print(f"   📦 Classes: {len(result['classes_found'])}")
                if 'success_rate' in result:
                    print(f"   📊 Success rate: {result['success_rate']}")

            except Exception as e:
                print(f"   💥 Test failed: {e}")
                all_results['service_tests'][test_name] = {
                    'status': 'test_failed',
                    'error': str(e),
                    'traceback': traceback.format_exc()
                }

        return all_results

    def generate_test_report(self, results: Dict[str, Any]) -> str:
        """Generate a comprehensive test report"""
        report = f"""# Service Functionality Test Report
Generated: {results['test_timestamp']}

## 🎯 Testing Overview
This report analyzes the current functionality of critical services before Phase 2 consolidation.
Testing focused on the most connected services identified in the dependency analysis.

## 📊 Test Results Summary

"""

        # Calculate overall statistics
        total_services = len(results['service_tests'])
        successful_tests = sum(1 for test in results['service_tests'].values()
                             if test['status'] in ['success', 'partial_success'])

        report += f"""**Overall Test Success Rate**: {successful_tests}/{total_services} ({(successful_tests/total_services*100):.1f}%)

"""

        # Detailed results for each service group
        for test_name, test_result in results['service_tests'].items():
            status_emoji = {
                'success': '✅',
                'partial_success': '⚠️',
                'failed': '❌',
                'import_failed': '🚫',
                'test_failed': '💥'
            }.get(test_result['status'], '❓')

            report += f"""### {test_name.replace('_', ' ').title()} {status_emoji}
**Status**: {test_result['status']}

"""

            # Add specific details based on test type
            if 'classes_found' in test_result:
                report += f"**Classes Found**: {', '.join(test_result['classes_found'])}\n\n"

            if 'success_rate' in test_result:
                report += f"**Success Rate**: {test_result['success_rate']}\n\n"

            if 'services_tested' in test_result:
                report += "**Individual Services**:\n"
                for service_name, service_data in test_result['services_tested'].items():
                    service_status = '✅' if service_data['import_status'] == 'success' else '❌'
                    report += f"- `{service_name}`: {service_status} {service_data['import_status']}\n"
                report += "\n"

            if 'error' in test_result:
                report += f"**Error**: `{test_result['error']}`\n\n"

        report += f"""
## 🚨 Critical Findings for Phase 2

### High Priority Items:
1. **Database Models** - Most critical component (18 dependents)
2. **Database Router** - Key infrastructure component (5 dependents)
3. **Context Services** - Core intelligence functionality

### Recommendations:
1. **Test successful services first** during consolidation
2. **Fix import issues** before moving files
3. **Maintain service interfaces** during refactoring
4. **Create integration tests-BAK** for business services
5. **Validate intelligence services** after consolidation

### Risk Assessment:
- **Low Risk**: Services with successful imports and clear interfaces
- **Medium Risk**: Services with partial success or missing components
- **High Risk**: Services with import failures or critical dependencies

## 🔄 Next Steps:
1. Fix any import issues identified in this report
2. Run integration tests-BAK for critical service interactions
3. Create service interface contracts before consolidation
4. Implement gradual migration strategy based on risk levels
"""

        return report


def main():
    """Run service functionality tests-BAK"""
    tester = ServiceTester()

    # Run comprehensive tests-BAK
    results = tester.run_comprehensive_test()

    # Generate and save report
    report = tester.generate_test_report(results)

    # Save files
    project_root = Path(__file__).parent.parent

    # Save detailed JSON results
    json_path = project_root / "docs" / "todo" / "service-test-results.json"
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, default=str)

    # Save readable report
    report_path = project_root / "docs" / "todo" / "service-functionality-report.md"
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)

    print(f"\n📊 Results saved:")
    print(f"   - JSON data: {json_path}")
    print(f"   - Report: {report_path}")
    print(f"\n🎯 Service functionality testing complete!")


if __name__ == "__main__":
    main()