"""
Memory Service - Database-Driven Memory File Generation

Manages the generation and maintenance of persistent memory files in the .claude directory
that automatically sync with APM (Agent Project Manager) database content.

Service Pattern:
    - This file: Main service coordinator
    - extractors/: Database extraction logic
    - generators/: File generation logic
    - templates/: Memory file templates

Usage:
    from agentpm.core.memory import MemoryService
    
    service = MemoryService(db_service)
    result = service.generate_all_files()
    result = service.update_changed_files()
"""

from typing import Dict, List, Optional, Any
from pathlib import Path
from datetime import datetime
import hashlib
import json

from ..database.service import DatabaseService
from .extractors.rules_extractor import RulesExtractor
from .extractors.principles_extractor import PrinciplesExtractor
from .extractors.workflow_extractor import WorkflowExtractor
from .extractors.agents_extractor import AgentsExtractor
from .extractors.context_extractor import ContextExtractor
from .extractors.project_extractor import ProjectExtractor
from .extractors.ideas_extractor import IdeasExtractor
from .generators.file_generator import FileGenerator
from .generators.template_renderer import TemplateRenderer


class MemoryService:
    """
    Main service coordinator for memory file generation.
    
    Orchestrates database extraction, template rendering, and file generation
    for all 7 memory files in the .claude directory.
    """
    
    def __init__(self, db_service: DatabaseService):
        """Initialize memory service with database connection."""
        self.db = db_service
        
        # Initialize extractors
        self.extractors = {
            'rules': RulesExtractor(db_service),
            'principles': PrinciplesExtractor(db_service),
            'workflow': WorkflowExtractor(db_service),
            'agents': AgentsExtractor(db_service),
            'context': ContextExtractor(db_service),
            'project': ProjectExtractor(db_service),
            'ideas': IdeasExtractor(db_service),
        }
        
        # Initialize generators
        self.template_renderer = TemplateRenderer()
        self.file_generator = FileGenerator()
        
        # Memory file configuration
        self.memory_files = {
            'rules': 'RULES.md',
            'principles': 'PRINCIPLES.md',
            'workflow': 'WORKFLOW.md',
            'agents': 'AGENTS.md',
            'context': 'CONTEXT.md',
            'project': 'PROJECT.md',
            'ideas': 'IDEAS.md',
        }
        
        # .claude directory path
        self.claude_dir = Path('.claude')
        self.claude_dir.mkdir(exist_ok=True)
    
    def generate_all_files(self, project_id: int) -> Dict[str, Any]:
        """
        Generate all 7 memory files from current database state.
        
        Args:
            project_id: Project ID to generate files for
            
        Returns:
            ServiceResult with generation statistics
        """
        try:
            results = {}
            start_time = datetime.now()
            
            for file_type, filename in self.memory_files.items():
                result = self._generate_single_file(file_type, filename, project_id)
                results[file_type] = result
            
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            return {
                'success': True,
                'files_generated': len(results),
                'duration_seconds': duration,
                'results': results,
                'timestamp': end_time.isoformat()
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def update_changed_files(self, project_id: int) -> Dict[str, Any]:
        """
        Update only memory files that have changed since last generation.
        
        Args:
            project_id: Project ID to update files for
            
        Returns:
            ServiceResult with update statistics
        """
        try:
            changed_files = self._detect_changed_files(project_id)
            results = {}
            start_time = datetime.now()
            
            for file_type in changed_files:
                filename = self.memory_files[file_type]
                result = self._generate_single_file(file_type, filename, project_id)
                results[file_type] = result
            
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            return {
                'success': True,
                'files_updated': len(changed_files),
                'duration_seconds': duration,
                'results': results,
                'timestamp': end_time.isoformat()
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def generate_specific_file(self, file_type: str, project_id: int) -> Dict[str, Any]:
        """
        Generate a specific memory file.
        
        Args:
            file_type: Type of memory file to generate
            project_id: Project ID to generate file for
            
        Returns:
            ServiceResult with generation result
        """
        if file_type not in self.memory_files:
            return {
                'success': False,
                'error': f"Unknown file type: {file_type}. Valid types: {list(self.memory_files.keys())}"
            }
        
        try:
            filename = self.memory_files[file_type]
            result = self._generate_single_file(file_type, filename, project_id)
            
            return {
                'success': True,
                'file_type': file_type,
                'filename': filename,
                'result': result,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def validate_files(self, project_id: int) -> Dict[str, Any]:
        """
        Validate that all memory files are current and complete.
        
        Args:
            project_id: Project ID to validate files for
            
        Returns:
            ServiceResult with validation results
        """
        try:
            validation_results = {}
            
            for file_type, filename in self.memory_files.items():
                filepath = self.claude_dir / filename
                
                if not filepath.exists():
                    validation_results[file_type] = {
                        'valid': False,
                        'error': 'File does not exist'
                    }
                    continue
                
                # Check file staleness
                file_mtime = datetime.fromtimestamp(filepath.stat().st_mtime)
                age_hours = (datetime.now() - file_mtime).total_seconds() / 3600
                
                # Check file content integrity
                content = filepath.read_text(encoding='utf-8')
                checksum = hashlib.md5(content.encode()).hexdigest()
                
                validation_results[file_type] = {
                    'valid': True,
                    'age_hours': age_hours,
                    'checksum': checksum,
                    'size_bytes': len(content),
                    'last_modified': file_mtime.isoformat()
                }
            
            return {
                'success': True,
                'validation_results': validation_results,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def get_file_status(self) -> Dict[str, Any]:
        """
        Get status of all memory files.
        
        Returns:
            ServiceResult with file status information
        """
        try:
            status = {}
            
            for file_type, filename in self.memory_files.items():
                filepath = self.claude_dir / filename
                
                if filepath.exists():
                    stat = filepath.stat()
                    status[file_type] = {
                        'exists': True,
                        'size_bytes': stat.st_size,
                        'last_modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                        'age_hours': (datetime.now() - datetime.fromtimestamp(stat.st_mtime)).total_seconds() / 3600
                    }
                else:
                    status[file_type] = {
                        'exists': False,
                        'size_bytes': 0,
                        'last_modified': None,
                        'age_hours': None
                    }
            
            return {
                'success': True,
                'file_status': status,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def _generate_single_file(self, file_type: str, filename: str, project_id: int) -> Dict[str, Any]:
        """
        Generate a single memory file.
        
        Args:
            file_type: Type of memory file
            filename: Output filename
            project_id: Project ID
            
        Returns:
            Generation result
        """
        try:
            # Extract data from database
            extractor = self.extractors[file_type]
            data = extractor.extract(project_id)
            
            # Render template
            content = self.template_renderer.render(file_type, data)
            
            # Generate file
            filepath = self.claude_dir / filename
            result = self.file_generator.write_file(filepath, content)
            
            return {
                'success': True,
                'filename': filename,
                'size_bytes': result['size_bytes'],
                'checksum': result['checksum'],
                'timestamp': result['timestamp']
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'filename': filename
            }
    
    def _detect_changed_files(self, project_id: int) -> List[str]:
        """
        Detect which memory files need updates based on database changes.
        
        Args:
            project_id: Project ID to check
            
        Returns:
            List of file types that need updates
        """
        changed_files = []
        
        for file_type, extractor in self.extractors.items():
            if extractor.has_changes(project_id):
                changed_files.append(file_type)
        
        return changed_files
    
    def get_system_info(self) -> Dict[str, Any]:
        """
        Get system information and configuration.
        
        Returns:
            System information
        """
        return {
            'memory_files': self.memory_files,
            'claude_directory': str(self.claude_dir),
            'extractors': list(self.extractors.keys()),
            'version': '1.0.0',
            'timestamp': datetime.now().isoformat()
        }
