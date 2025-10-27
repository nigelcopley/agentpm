"""
Claude Code Memory Tool Integration

Manages Claude Code memory tool for APM (Agent Project Manager) integration including
memory storage, retrieval, and management.

Based on: https://docs.claude.com/en/docs/agents-and-tools/tool-use/memory-tool
"""

from pathlib import Path
from typing import List, Dict, Any, Optional, Union
import json
import hashlib
from datetime import datetime, timedelta

from agentpm.core.database.service import DatabaseService
from ..models import MemoryToolDefinition, MemoryToolType, ClaudeCodeComponentType


class ClaudeCodeMemoryToolManager:
    """
    Manages Claude Code memory tool for APM (Agent Project Manager).
    
    Provides memory storage and retrieval capabilities for APM (Agent Project Manager)
    workflows, decisions, and learnings.
    """
    
    def __init__(self, db_service: DatabaseService):
        """
        Initialize memory tool manager.
        
        Args:
            db_service: Database service for accessing APM (Agent Project Manager) data
        """
        self.db = db_service
        self._memory_cache: Dict[str, Dict[str, Any]] = {}
        self._memory_storage: Path = Path(".claude/memory")
        self._memory_index: Dict[str, List[str]] = {}
    
    def create_aipm_memory_configs(
        self,
        output_dir: Path,
        project_id: Optional[int] = None
    ) -> List[MemoryToolDefinition]:
        """
        Create comprehensive APM (Agent Project Manager) memory configurations for Claude Code.
        
        Args:
            output_dir: Directory to write memory configurations
            project_id: Optional project ID for project-specific memory
            
        Returns:
            List of created MemoryToolDefinitions
        """
        memory_configs = []
        
        # Create memory directory
        memory_dir = output_dir / "memory"
        memory_dir.mkdir(parents=True, exist_ok=True)
        
        # Create APM (Agent Project Manager) memory configurations
        memory_configs.extend(self._create_decision_memory_configs(memory_dir))
        memory_configs.extend(self._create_learning_memory_configs(memory_dir))
        memory_configs.extend(self._create_pattern_memory_configs(memory_dir))
        memory_configs.extend(self._create_context_memory_configs(memory_dir))
        memory_configs.extend(self._create_workflow_memory_configs(memory_dir))
        
        # Create project-specific memory configurations if project_id provided
        if project_id:
            memory_configs.extend(self._create_project_memory_configs(memory_dir, project_id))
        
        return memory_configs
    
    def create_decision_memory_configs(self, memory_dir: Path) -> List[MemoryToolDefinition]:
        """Create decision memory configurations."""
        memory_configs = []
        
        # Decision memory configuration
        decision_memory_config = MemoryToolDefinition(
            name="APM (Agent Project Manager) Decision Memory",
            description="Memory for APM (Agent Project Manager) decisions with evidence and business value",
            component_type=ClaudeCodeComponentType.MEMORY_TOOL,
            memory_type=MemoryToolType.PERSISTENT,
            storage_location=".claude/memory/decisions",
            retention_policy={
                "max_age_days": 365,
                "max_entries": 10000,
                "auto_cleanup": True
            },
            indexing_strategy={
                "index_by": ["decision_type", "business_value", "confidence_score", "timestamp"],
                "search_fields": ["content", "evidence", "business_value", "tags"],
                "full_text_search": True
            },
            access_control={
                "read_access": ["all_agents"],
                "write_access": ["decision_agents", "senior_agents"],
                "admin_access": ["system_admin"]
            },
            compression=True,
            encryption=False,
            category="decision",
            keywords=["decision", "evidence", "business-value", "aipm"]
        )
        
        config_file = memory_dir / "decision-memory.json"
        config_content = self._create_decision_memory_config_content(decision_memory_config)
        config_file.write_text(json.dumps(config_content, indent=2))
        memory_configs.append(decision_memory_config)
        
        return memory_configs
    
    def create_learning_memory_configs(self, memory_dir: Path) -> List[MemoryToolDefinition]:
        """Create learning memory configurations."""
        memory_configs = []
        
        # Learning memory configuration
        learning_memory_config = MemoryToolDefinition(
            name="APM (Agent Project Manager) Learning Memory",
            description="Memory for APM (Agent Project Manager) learnings and insights",
            component_type=ClaudeCodeComponentType.MEMORY_TOOL,
            memory_type=MemoryToolType.PERSISTENT,
            storage_location=".claude/memory/learnings",
            retention_policy={
                "max_age_days": 730,
                "max_entries": 50000,
                "auto_cleanup": True
            },
            indexing_strategy={
                "index_by": ["learning_type", "category", "confidence_score", "timestamp"],
                "search_fields": ["content", "insights", "applications", "tags"],
                "full_text_search": True
            },
            access_control={
                "read_access": ["all_agents"],
                "write_access": ["learning_agents", "senior_agents"],
                "admin_access": ["system_admin"]
            },
            compression=True,
            encryption=False,
            category="learning",
            keywords=["learning", "insight", "pattern", "aipm"]
        )
        
        config_file = memory_dir / "learning-memory.json"
        config_content = self._create_learning_memory_config_content(learning_memory_config)
        config_file.write_text(json.dumps(config_content, indent=2))
        memory_configs.append(learning_memory_config)
        
        return memory_configs
    
    def create_pattern_memory_configs(self, memory_dir: Path) -> List[MemoryToolDefinition]:
        """Create pattern memory configurations."""
        memory_configs = []
        
        # Pattern memory configuration
        pattern_memory_config = MemoryToolDefinition(
            name="APM (Agent Project Manager) Pattern Memory",
            description="Memory for APM (Agent Project Manager) patterns and reusable solutions",
            component_type=ClaudeCodeComponentType.MEMORY_TOOL,
            memory_type=MemoryToolType.PERSISTENT,
            storage_location=".claude/memory/patterns",
            retention_policy={
                "max_age_days": 1095,  # 3 years
                "max_entries": 20000,
                "auto_cleanup": False  # Patterns are valuable, don't auto-cleanup
            },
            indexing_strategy={
                "index_by": ["pattern_type", "category", "usage_count", "effectiveness_score"],
                "search_fields": ["name", "description", "when_to_use", "examples", "tags"],
                "full_text_search": True
            },
            access_control={
                "read_access": ["all_agents"],
                "write_access": ["pattern_agents", "senior_agents"],
                "admin_access": ["system_admin"]
            },
            compression=True,
            encryption=False,
            category="pattern",
            keywords=["pattern", "solution", "reusable", "aipm"]
        )
        
        config_file = memory_dir / "pattern-memory.json"
        config_content = self._create_pattern_memory_config_content(pattern_memory_config)
        config_file.write_text(json.dumps(config_content, indent=2))
        memory_configs.append(pattern_memory_config)
        
        return memory_configs
    
    def create_context_memory_configs(self, memory_dir: Path) -> List[MemoryToolDefinition]:
        """Create context memory configurations."""
        memory_configs = []
        
        # Context memory configuration
        context_memory_config = MemoryToolDefinition(
            name="APM (Agent Project Manager) Context Memory",
            description="Memory for APM (Agent Project Manager) context and project state",
            component_type=ClaudeCodeComponentType.MEMORY_TOOL,
            memory_type=MemoryToolType.SESSION,
            storage_location=".claude/memory/context",
            retention_policy={
                "max_age_days": 30,
                "max_entries": 1000,
                "auto_cleanup": True
            },
            indexing_strategy={
                "index_by": ["context_type", "project_id", "work_item_id", "timestamp"],
                "search_fields": ["context_content", "quality_score", "tags"],
                "full_text_search": True
            },
            access_control={
                "read_access": ["all_agents"],
                "write_access": ["context_agents", "senior_agents"],
                "admin_access": ["system_admin"]
            },
            compression=True,
            encryption=False,
            category="context",
            keywords=["context", "project", "state", "aipm"]
        )
        
        config_file = memory_dir / "context-memory.json"
        config_content = self._create_context_memory_config_content(context_memory_config)
        config_file.write_text(json.dumps(config_content, indent=2))
        memory_configs.append(context_memory_config)
        
        return memory_configs
    
    def create_workflow_memory_configs(self, memory_dir: Path) -> List[MemoryToolDefinition]:
        """Create workflow memory configurations."""
        memory_configs = []
        
        # Workflow memory configuration
        workflow_memory_config = MemoryToolDefinition(
            name="APM (Agent Project Manager) Workflow Memory",
            description="Memory for APM (Agent Project Manager) workflow execution and results",
            component_type=ClaudeCodeComponentType.MEMORY_TOOL,
            memory_type=MemoryToolType.PERSISTENT,
            storage_location=".claude/memory/workflows",
            retention_policy={
                "max_age_days": 180,
                "max_entries": 5000,
                "auto_cleanup": True
            },
            indexing_strategy={
                "index_by": ["workflow_type", "status", "completion_time", "quality_score"],
                "search_fields": ["workflow_name", "results", "learnings", "tags"],
                "full_text_search": True
            },
            access_control={
                "read_access": ["all_agents"],
                "write_access": ["workflow_agents", "senior_agents"],
                "admin_access": ["system_admin"]
            },
            compression=True,
            encryption=False,
            category="workflow",
            keywords=["workflow", "execution", "results", "aipm"]
        )
        
        config_file = memory_dir / "workflow-memory.json"
        config_content = self._create_workflow_memory_config_content(workflow_memory_config)
        config_file.write_text(json.dumps(config_content, indent=2))
        memory_configs.append(workflow_memory_config)
        
        return memory_configs
    
    def create_project_memory_configs(self, memory_dir: Path, project_id: int) -> List[MemoryToolDefinition]:
        """Create project-specific memory configurations."""
        memory_configs = []
        
        # Project memory configuration
        project_memory_config = MemoryToolDefinition(
            name=f"APM (Agent Project Manager) Project {project_id} Memory",
            description=f"Memory for project {project_id} specific data",
            component_type=ClaudeCodeComponentType.MEMORY_TOOL,
            memory_type=MemoryToolType.PERSISTENT,
            storage_location=f".claude/memory/projects/{project_id}",
            retention_policy={
                "max_age_days": 365,
                "max_entries": 10000,
                "auto_cleanup": True
            },
            indexing_strategy={
                "index_by": ["data_type", "work_item_id", "timestamp"],
                "search_fields": ["content", "metadata", "tags"],
                "full_text_search": True
            },
            access_control={
                "read_access": [f"project_{project_id}_agents"],
                "write_access": [f"project_{project_id}_agents", "senior_agents"],
                "admin_access": ["system_admin"]
            },
            compression=True,
            encryption=False,
            category="project",
            keywords=[f"project-{project_id}", "aipm"]
        )
        
        config_file = memory_dir / f"project-{project_id}-memory.json"
        config_content = self._create_project_memory_config_content(project_memory_config, project_id)
        config_file.write_text(json.dumps(config_content, indent=2))
        memory_configs.append(project_memory_config)
        
        return memory_configs
    
    def store_memory(
        self,
        memory_key: str,
        memory_data: Dict[str, Any],
        memory_type: MemoryToolType = MemoryToolType.PERSISTENT,
        category: str = "general"
    ) -> bool:
        """
        Store memory data.
        
        Args:
            memory_key: Unique key for the memory
            memory_data: Data to store
            memory_type: Type of memory (persistent or session)
            category: Category of the memory
            
        Returns:
            True if memory stored successfully, False otherwise
        """
        try:
            # Create memory entry
            memory_entry = {
                "key": memory_key,
                "data": memory_data,
                "type": memory_type.value,
                "category": category,
                "timestamp": datetime.now().isoformat(),
                "hash": hashlib.md5(json.dumps(memory_data, sort_keys=True).encode()).hexdigest()
            }
            
            # Store in cache
            self._memory_cache[memory_key] = memory_entry
            
            # Store in file system if persistent
            if memory_type == MemoryToolType.PERSISTENT:
                self._store_persistent_memory(memory_entry)
            
            # Update index
            self._update_memory_index(memory_entry)
            
            return True
            
        except Exception as e:
            print(f"Error storing memory {memory_key}: {e}")
            return False
    
    def retrieve_memory(self, memory_key: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve memory data by key.
        
        Args:
            memory_key: Key of the memory to retrieve
            
        Returns:
            Memory data if found, None otherwise
        """
        try:
            # Check cache first
            if memory_key in self._memory_cache:
                return self._memory_cache[memory_key]["data"]
            
            # Check persistent storage
            memory_entry = self._retrieve_persistent_memory(memory_key)
            if memory_entry:
                # Cache the retrieved memory
                self._memory_cache[memory_key] = memory_entry
                return memory_entry["data"]
            
            return None
            
        except Exception as e:
            print(f"Error retrieving memory {memory_key}: {e}")
            return None
    
    def search_memory(
        self,
        query: str,
        category: Optional[str] = None,
        memory_type: Optional[MemoryToolType] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Search memory by query.
        
        Args:
            query: Search query
            category: Optional category filter
            memory_type: Optional memory type filter
            limit: Maximum number of results
            
        Returns:
            List of matching memory entries
        """
        try:
            results = []
            
            # Search in cache
            for memory_key, memory_entry in self._memory_cache.items():
                if self._matches_search_criteria(memory_entry, query, category, memory_type):
                    results.append(memory_entry)
            
            # Search in persistent storage
            persistent_results = self._search_persistent_memory(query, category, memory_type, limit)
            results.extend(persistent_results)
            
            # Sort by relevance and timestamp
            results.sort(key=lambda x: (x.get("relevance_score", 0), x["timestamp"]), reverse=True)
            
            return results[:limit]
            
        except Exception as e:
            print(f"Error searching memory: {e}")
            return []
    
    def delete_memory(self, memory_key: str) -> bool:
        """
        Delete memory by key.
        
        Args:
            memory_key: Key of the memory to delete
            
        Returns:
            True if memory deleted successfully, False otherwise
        """
        try:
            # Remove from cache
            if memory_key in self._memory_cache:
                del self._memory_cache[memory_key]
            
            # Remove from persistent storage
            self._delete_persistent_memory(memory_key)
            
            # Update index
            self._remove_from_memory_index(memory_key)
            
            return True
            
        except Exception as e:
            print(f"Error deleting memory {memory_key}: {e}")
            return False
    
    def cleanup_old_memory(self, max_age_days: int = 30) -> int:
        """
        Cleanup old memory entries.
        
        Args:
            max_age_days: Maximum age in days for memory entries
            
        Returns:
            Number of memory entries cleaned up
        """
        try:
            cleaned_count = 0
            cutoff_time = datetime.now() - timedelta(days=max_age_days)
            
            # Cleanup cache
            keys_to_remove = []
            for memory_key, memory_entry in self._memory_cache.items():
                memory_time = datetime.fromisoformat(memory_entry["timestamp"])
                if memory_time < cutoff_time:
                    keys_to_remove.append(memory_key)
            
            for key in keys_to_remove:
                del self._memory_cache[key]
                cleaned_count += 1
            
            # Cleanup persistent storage
            persistent_cleaned = self._cleanup_persistent_memory(cutoff_time)
            cleaned_count += persistent_cleaned
            
            return cleaned_count
            
        except Exception as e:
            print(f"Error cleaning up memory: {e}")
            return 0
    
    def get_memory_stats(self) -> Dict[str, Any]:
        """
        Get memory statistics.
        
        Returns:
            Dictionary with memory statistics
        """
        try:
            cache_count = len(self._memory_cache)
            persistent_count = self._get_persistent_memory_count()
            
            return {
                "cache_entries": cache_count,
                "persistent_entries": persistent_count,
                "total_entries": cache_count + persistent_count,
                "memory_usage": self._get_memory_usage(),
                "index_size": len(self._memory_index)
            }
            
        except Exception as e:
            print(f"Error getting memory stats: {e}")
            return {}
    
    def _store_persistent_memory(self, memory_entry: Dict[str, Any]) -> None:
        """Store memory in persistent storage."""
        try:
            memory_dir = self._memory_storage / memory_entry["category"]
            memory_dir.mkdir(parents=True, exist_ok=True)
            
            memory_file = memory_dir / f"{memory_entry['key']}.json"
            memory_file.write_text(json.dumps(memory_entry, indent=2))
            
        except Exception as e:
            print(f"Error storing persistent memory: {e}")
    
    def _retrieve_persistent_memory(self, memory_key: str) -> Optional[Dict[str, Any]]:
        """Retrieve memory from persistent storage."""
        try:
            for category_dir in self._memory_storage.iterdir():
                if category_dir.is_dir():
                    memory_file = category_dir / f"{memory_key}.json"
                    if memory_file.exists():
                        return json.loads(memory_file.read_text())
            
            return None
            
        except Exception as e:
            print(f"Error retrieving persistent memory: {e}")
            return None
    
    def _search_persistent_memory(
        self,
        query: str,
        category: Optional[str] = None,
        memory_type: Optional[MemoryToolType] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Search memory in persistent storage."""
        try:
            results = []
            
            # Search in specific category if provided
            if category:
                category_dir = self._memory_storage / category
                if category_dir.exists():
                    results.extend(self._search_category_directory(category_dir, query, memory_type))
            else:
                # Search all categories
                for category_dir in self._memory_storage.iterdir():
                    if category_dir.is_dir():
                        results.extend(self._search_category_directory(category_dir, query, memory_type))
            
            return results[:limit]
            
        except Exception as e:
            print(f"Error searching persistent memory: {e}")
            return []
    
    def _search_category_directory(
        self,
        category_dir: Path,
        query: str,
        memory_type: Optional[MemoryToolType] = None
    ) -> List[Dict[str, Any]]:
        """Search memory in a specific category directory."""
        results = []
        
        try:
            for memory_file in category_dir.glob("*.json"):
                memory_entry = json.loads(memory_file.read_text())
                
                if self._matches_search_criteria(memory_entry, query, None, memory_type):
                    results.append(memory_entry)
            
        except Exception as e:
            print(f"Error searching category directory {category_dir}: {e}")
        
        return results
    
    def _delete_persistent_memory(self, memory_key: str) -> None:
        """Delete memory from persistent storage."""
        try:
            for category_dir in self._memory_storage.iterdir():
                if category_dir.is_dir():
                    memory_file = category_dir / f"{memory_key}.json"
                    if memory_file.exists():
                        memory_file.unlink()
                        break
            
        except Exception as e:
            print(f"Error deleting persistent memory: {e}")
    
    def _cleanup_persistent_memory(self, cutoff_time: datetime) -> int:
        """Cleanup old memory from persistent storage."""
        cleaned_count = 0
        
        try:
            for category_dir in self._memory_storage.iterdir():
                if category_dir.is_dir():
                    for memory_file in category_dir.glob("*.json"):
                        memory_entry = json.loads(memory_file.read_text())
                        memory_time = datetime.fromisoformat(memory_entry["timestamp"])
                        
                        if memory_time < cutoff_time:
                            memory_file.unlink()
                            cleaned_count += 1
            
        except Exception as e:
            print(f"Error cleaning up persistent memory: {e}")
        
        return cleaned_count
    
    def _get_persistent_memory_count(self) -> int:
        """Get count of persistent memory entries."""
        count = 0
        
        try:
            for category_dir in self._memory_storage.iterdir():
                if category_dir.is_dir():
                    count += len(list(category_dir.glob("*.json")))
            
        except Exception as e:
            print(f"Error getting persistent memory count: {e}")
        
        return count
    
    def _get_memory_usage(self) -> Dict[str, Any]:
        """Get memory usage statistics."""
        try:
            total_size = 0
            category_sizes = {}
            
            for category_dir in self._memory_storage.iterdir():
                if category_dir.is_dir():
                    category_size = sum(f.stat().st_size for f in category_dir.glob("*.json"))
                    category_sizes[category_dir.name] = category_size
                    total_size += category_size
            
            return {
                "total_size_bytes": total_size,
                "category_sizes": category_sizes
            }
            
        except Exception as e:
            print(f"Error getting memory usage: {e}")
            return {}
    
    def _matches_search_criteria(
        self,
        memory_entry: Dict[str, Any],
        query: str,
        category: Optional[str] = None,
        memory_type: Optional[MemoryToolType] = None
    ) -> bool:
        """Check if memory entry matches search criteria."""
        try:
            # Check category filter
            if category and memory_entry.get("category") != category:
                return False
            
            # Check memory type filter
            if memory_type and memory_entry.get("type") != memory_type.value:
                return False
            
            # Check query match
            if query:
                query_lower = query.lower()
                memory_data = memory_entry.get("data", {})
                
                # Search in memory data
                for key, value in memory_data.items():
                    if isinstance(value, str) and query_lower in value.lower():
                        return True
                
                # Search in memory key
                if query_lower in memory_entry.get("key", "").lower():
                    return True
            
            return True
            
        except Exception as e:
            print(f"Error matching search criteria: {e}")
            return False
    
    def _update_memory_index(self, memory_entry: Dict[str, Any]) -> None:
        """Update memory index."""
        try:
            memory_key = memory_entry["key"]
            category = memory_entry.get("category", "general")
            
            if category not in self._memory_index:
                self._memory_index[category] = []
            
            if memory_key not in self._memory_index[category]:
                self._memory_index[category].append(memory_key)
            
        except Exception as e:
            print(f"Error updating memory index: {e}")
    
    def _remove_from_memory_index(self, memory_key: str) -> None:
        """Remove memory key from index."""
        try:
            for category_keys in self._memory_index.values():
                if memory_key in category_keys:
                    category_keys.remove(memory_key)
                    break
            
        except Exception as e:
            print(f"Error removing from memory index: {e}")
    
    # Memory configuration content creation methods
    def _create_decision_memory_config_content(self, config: MemoryToolDefinition) -> Dict[str, Any]:
        """Create decision memory configuration content."""
        return {
            "name": config.name,
            "description": config.description,
            "type": config.memory_type.value,
            "storage_location": config.storage_location,
            "retention_policy": config.retention_policy,
            "indexing_strategy": config.indexing_strategy,
            "access_control": config.access_control,
            "compression": config.compression,
            "encryption": config.encryption,
            "category": config.category,
            "keywords": config.keywords,
            "memory_schema": {
                "decision_type": "string",
                "content": "string",
                "evidence": "string",
                "business_value": "string",
                "confidence_score": "float",
                "timestamp": "datetime",
                "tags": "array"
            }
        }
    
    def _create_learning_memory_config_content(self, config: MemoryToolDefinition) -> Dict[str, Any]:
        """Create learning memory configuration content."""
        return {
            "name": config.name,
            "description": config.description,
            "type": config.memory_type.value,
            "storage_location": config.storage_location,
            "retention_policy": config.retention_policy,
            "indexing_strategy": config.indexing_strategy,
            "access_control": config.access_control,
            "compression": config.compression,
            "encryption": config.encryption,
            "category": config.category,
            "keywords": config.keywords,
            "memory_schema": {
                "learning_type": "string",
                "content": "string",
                "insights": "string",
                "applications": "array",
                "confidence_score": "float",
                "timestamp": "datetime",
                "tags": "array"
            }
        }
    
    def _create_pattern_memory_config_content(self, config: MemoryToolDefinition) -> Dict[str, Any]:
        """Create pattern memory configuration content."""
        return {
            "name": config.name,
            "description": config.description,
            "type": config.memory_type.value,
            "storage_location": config.storage_location,
            "retention_policy": config.retention_policy,
            "indexing_strategy": config.indexing_strategy,
            "access_control": config.access_control,
            "compression": config.compression,
            "encryption": config.encryption,
            "category": config.category,
            "keywords": config.keywords,
            "memory_schema": {
                "pattern_type": "string",
                "name": "string",
                "description": "string",
                "when_to_use": "string",
                "examples": "array",
                "usage_count": "integer",
                "effectiveness_score": "float",
                "timestamp": "datetime",
                "tags": "array"
            }
        }
    
    def _create_context_memory_config_content(self, config: MemoryToolDefinition) -> Dict[str, Any]:
        """Create context memory configuration content."""
        return {
            "name": config.name,
            "description": config.description,
            "type": config.memory_type.value,
            "storage_location": config.storage_location,
            "retention_policy": config.retention_policy,
            "indexing_strategy": config.indexing_strategy,
            "access_control": config.access_control,
            "compression": config.compression,
            "encryption": config.encryption,
            "category": config.category,
            "keywords": config.keywords,
            "memory_schema": {
                "context_type": "string",
                "project_id": "integer",
                "work_item_id": "integer",
                "context_content": "string",
                "quality_score": "float",
                "timestamp": "datetime",
                "tags": "array"
            }
        }
    
    def _create_workflow_memory_config_content(self, config: MemoryToolDefinition) -> Dict[str, Any]:
        """Create workflow memory configuration content."""
        return {
            "name": config.name,
            "description": config.description,
            "type": config.memory_type.value,
            "storage_location": config.storage_location,
            "retention_policy": config.retention_policy,
            "indexing_strategy": config.indexing_strategy,
            "access_control": config.access_control,
            "compression": config.compression,
            "encryption": config.encryption,
            "category": config.category,
            "keywords": config.keywords,
            "memory_schema": {
                "workflow_type": "string",
                "workflow_name": "string",
                "status": "string",
                "results": "string",
                "learnings": "array",
                "completion_time": "datetime",
                "quality_score": "float",
                "timestamp": "datetime",
                "tags": "array"
            }
        }
    
    def _create_project_memory_config_content(self, config: MemoryToolDefinition, project_id: int) -> Dict[str, Any]:
        """Create project memory configuration content."""
        return {
            "name": config.name,
            "description": config.description,
            "type": config.memory_type.value,
            "storage_location": config.storage_location,
            "retention_policy": config.retention_policy,
            "indexing_strategy": config.indexing_strategy,
            "access_control": config.access_control,
            "compression": config.compression,
            "encryption": config.encryption,
            "category": config.category,
            "keywords": config.keywords,
            "memory_schema": {
                "data_type": "string",
                "project_id": project_id,
                "work_item_id": "integer",
                "content": "string",
                "metadata": "object",
                "timestamp": "datetime",
                "tags": "array"
            }
        }
