"""
Base Extractor - Abstract base class for memory file data extraction

Provides common functionality for all memory file extractors including
database connection, change detection, and data formatting.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from datetime import datetime
import hashlib
import json

from ...database.service import DatabaseService


class BaseExtractor(ABC):
    """
    Abstract base class for memory file data extractors.
    
    Provides common functionality for database extraction, change detection,
    and data formatting for memory file generation.
    """
    
    def __init__(self, db_service: DatabaseService):
        """Initialize extractor with database service."""
        self.db = db_service
        self.last_extraction_hash = None
        self.last_extraction_time = None
    
    @abstractmethod
    def extract(self, project_id: int) -> Dict[str, Any]:
        """
        Extract data for memory file generation.
        
        Args:
            project_id: Project ID to extract data for
            
        Returns:
            Extracted data dictionary
        """
        pass
    
    @abstractmethod
    def get_source_tables(self) -> list[str]:
        """
        Get list of database tables this extractor uses.
        
        Returns:
            List of table names
        """
        pass
    
    def has_changes(self, project_id: int) -> bool:
        """
        Check if data has changed since last extraction.
        
        Args:
            project_id: Project ID to check
            
        Returns:
            True if data has changed, False otherwise
        """
        try:
            # Extract current data
            current_data = self.extract(project_id)
            
            # Calculate hash of current data
            current_hash = self._calculate_data_hash(current_data)
            
            # Compare with last extraction
            if self.last_extraction_hash is None:
                return True  # First extraction
            
            if current_hash != self.last_extraction_hash:
                return True  # Data has changed
            
            return False  # No changes
            
        except Exception:
            return True  # Assume changes if extraction fails
    
    def update_extraction_cache(self, project_id: int) -> None:
        """
        Update extraction cache with current data.
        
        Args:
            project_id: Project ID to cache
        """
        try:
            data = self.extract(project_id)
            self.last_extraction_hash = self._calculate_data_hash(data)
            self.last_extraction_time = datetime.now()
        except Exception:
            # Don't update cache if extraction fails
            pass
    
    def _calculate_data_hash(self, data: Dict[str, Any]) -> str:
        """
        Calculate hash of extracted data for change detection.
        
        Args:
            data: Data dictionary to hash
            
        Returns:
            MD5 hash of data
        """
        # Convert data to JSON string for hashing
        data_str = json.dumps(data, sort_keys=True, default=str)
        return hashlib.md5(data_str.encode()).hexdigest()
    
    def _format_timestamp(self, timestamp: Optional[datetime]) -> str:
        """
        Format timestamp for memory file output.
        
        Args:
            timestamp: Timestamp to format
            
        Returns:
            Formatted timestamp string
        """
        if timestamp is None:
            return "Never"
        return timestamp.strftime("%Y-%m-%d %H:%M:%S")
    
    def _format_duration(self, start_time: datetime, end_time: datetime) -> str:
        """
        Format duration between timestamps.
        
        Args:
            start_time: Start timestamp
            end_time: End timestamp
            
        Returns:
            Formatted duration string
        """
        duration = end_time - start_time
        total_seconds = duration.total_seconds()
        
        if total_seconds < 60:
            return f"{total_seconds:.1f}s"
        elif total_seconds < 3600:
            minutes = total_seconds / 60
            return f"{minutes:.1f}m"
        else:
            hours = total_seconds / 3600
            return f"{hours:.1f}h"
    
    def _safe_get(self, data: Dict[str, Any], key: str, default: Any = None) -> Any:
        """
        Safely get value from dictionary with default.
        
        Args:
            data: Dictionary to get value from
            key: Key to get
            default: Default value if key not found
            
        Returns:
            Value or default
        """
        return data.get(key, default)
    
    def _format_list(self, items: list, max_items: int = 10) -> str:
        """
        Format list for display with truncation.
        
        Args:
            items: List to format
            max_items: Maximum items to show
            
        Returns:
            Formatted list string
        """
        if not items:
            return "None"
        
        if len(items) <= max_items:
            return ", ".join(str(item) for item in items)
        else:
            shown = items[:max_items]
            return f"{', '.join(str(item) for item in shown)} (+{len(items) - max_items} more)"
    
    def _format_count(self, count: int) -> str:
        """
        Format count with proper pluralization.
        
        Args:
            count: Count to format
            
        Returns:
            Formatted count string
        """
        if count == 1:
            return "1 item"
        else:
            return f"{count} items"
    
    def get_extraction_info(self) -> Dict[str, Any]:
        """
        Get information about last extraction.
        
        Returns:
            Extraction information
        """
        return {
            'last_extraction_time': self.last_extraction_time,
            'last_extraction_hash': self.last_extraction_hash,
            'source_tables': self.get_source_tables(),
            'extractor_class': self.__class__.__name__
        }
