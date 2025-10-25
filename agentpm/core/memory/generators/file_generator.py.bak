"""
File Generator - Memory file writing and metadata management

Handles the creation of memory files in the .claude directory with
proper formatting, metadata, and integrity checks.
"""

from typing import Dict, Any
from pathlib import Path
from datetime import datetime
import hashlib


class FileGenerator:
    """
    Generator for memory files.
    
    Handles file writing, metadata management, and integrity checks
    for memory files in the .claude directory.
    """
    
    def __init__(self):
        """Initialize file generator."""
        self.claude_dir = Path('.claude')
        self.claude_dir.mkdir(exist_ok=True)
    
    def write_file(self, filepath: Path, content: str) -> Dict[str, Any]:
        """
        Write memory file with metadata and integrity checks.
        
        Args:
            filepath: Path to write file to
            content: File content to write
            
        Returns:
            Generation result dictionary
        """
        try:
            # Ensure .claude directory exists
            filepath.parent.mkdir(parents=True, exist_ok=True)
            
            # Add metadata to content
            content_with_metadata = self._add_metadata(content, filepath.name)
            
            # Write file
            filepath.write_text(content_with_metadata, encoding='utf-8')
            
            # Calculate file statistics
            stat = filepath.stat()
            checksum = self._calculate_checksum(content_with_metadata)
            
            return {
                'success': True,
                'filepath': str(filepath),
                'size_bytes': len(content_with_metadata.encode('utf-8')),
                'checksum': checksum,
                'timestamp': datetime.now().isoformat(),
                'last_modified': datetime.fromtimestamp(stat.st_mtime).isoformat()
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'filepath': str(filepath),
                'size_bytes': 0,
                'checksum': None,
                'timestamp': datetime.now().isoformat()
            }
    
    def read_file(self, filepath: Path) -> Dict[str, Any]:
        """
        Read memory file with metadata extraction.
        
        Args:
            filepath: Path to read file from
            
        Returns:
            File content and metadata
        """
        try:
            if not filepath.exists():
                return {
                    'success': False,
                    'error': 'File does not exist',
                    'filepath': str(filepath)
                }
            
            content = filepath.read_text(encoding='utf-8')
            stat = filepath.stat()
            checksum = self._calculate_checksum(content)
            
            # Extract metadata from content
            metadata = self._extract_metadata(content)
            
            return {
                'success': True,
                'filepath': str(filepath),
                'content': content,
                'size_bytes': stat.st_size,
                'checksum': checksum,
                'last_modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                'metadata': metadata
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'filepath': str(filepath)
            }
    
    def validate_file(self, filepath: Path) -> Dict[str, Any]:
        """
        Validate memory file integrity and format.
        
        Args:
            filepath: Path to validate file
            
        Returns:
            Validation result
        """
        try:
            if not filepath.exists():
                return {
                    'valid': False,
                    'error': 'File does not exist',
                    'filepath': str(filepath)
                }
            
            # Read file
            read_result = self.read_file(filepath)
            if not read_result['success']:
                return {
                    'valid': False,
                    'error': read_result['error'],
                    'filepath': str(filepath)
                }
            
            content = read_result['content']
            
            # Check file format
            format_valid = self._validate_format(content)
            
            # Check metadata
            metadata_valid = self._validate_metadata(content)
            
            # Check age
            age_hours = self._calculate_age_hours(read_result['last_modified'])
            age_valid = age_hours < 24  # Consider stale after 24 hours
            
            return {
                'valid': format_valid and metadata_valid,
                'filepath': str(filepath),
                'format_valid': format_valid,
                'metadata_valid': metadata_valid,
                'age_valid': age_valid,
                'age_hours': age_hours,
                'size_bytes': read_result['size_bytes'],
                'checksum': read_result['checksum'],
                'last_modified': read_result['last_modified']
            }
            
        except Exception as e:
            return {
                'valid': False,
                'error': str(e),
                'filepath': str(filepath)
            }
    
    def backup_file(self, filepath: Path) -> Dict[str, Any]:
        """
        Create backup of existing memory file.
        
        Args:
            filepath: Path to backup file
            
        Returns:
            Backup result
        """
        try:
            if not filepath.exists():
                return {
                    'success': False,
                    'error': 'File does not exist to backup',
                    'filepath': str(filepath)
                }
            
            # Create backup filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = filepath.with_suffix(f'.{timestamp}.bak')
            
            # Copy file
            import shutil
            shutil.copy2(filepath, backup_path)
            
            return {
                'success': True,
                'original_path': str(filepath),
                'backup_path': str(backup_path),
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'filepath': str(filepath)
            }
    
    def _add_metadata(self, content: str, filename: str) -> str:
        """
        Add metadata footer to content.
        
        Args:
            content: Original content
            filename: Filename for metadata
            
        Returns:
            Content with metadata footer
        """
        timestamp = datetime.now().isoformat()
        checksum = self._calculate_checksum(content)
        
        metadata = f"""

---

## Last Updated
- **Date**: {timestamp}
- **Source**: APM (Agent Project Manager) Database
- **Version**: 1.0
- **Checksum**: {checksum}
- **Generated by**: Claude Memory System

## Related Files
- [RULES.md](./RULES.md) - Governance rules enforcement
- [PRINCIPLES.md](./PRINCIPLES.md) - Development principles pyramid
- [WORKFLOW.md](./WORKFLOW.md) - Workflow and quality gates
- [AGENTS.md](./AGENTS.md) - Agent system and capabilities
- [CONTEXT.md](./CONTEXT.md) - Context assembly system
- [PROJECT.md](./PROJECT.md) - Project context and information
- [IDEAS.md](./IDEAS.md) - Multi-agent analysis pipeline
"""
        
        return content + metadata
    
    def _extract_metadata(self, content: str) -> Dict[str, Any]:
        """
        Extract metadata from file content.
        
        Args:
            content: File content
            
        Returns:
            Extracted metadata
        """
        metadata = {}
        
        try:
            # Look for metadata section
            if "## Last Updated" in content:
                lines = content.split('\n')
                in_metadata = False
                
                for line in lines:
                    if line.strip() == "## Last Updated":
                        in_metadata = True
                        continue
                    
                    if in_metadata:
                        if line.startswith('## '):
                            break  # End of metadata section
                        
                        if ':' in line:
                            key, value = line.split(':', 1)
                            key = key.strip().replace('**', '').replace('-', '')
                            value = value.strip()
                            metadata[key] = value
            
        except Exception:
            pass  # Return empty metadata if extraction fails
        
        return metadata
    
    def _validate_format(self, content: str) -> bool:
        """
        Validate file format.
        
        Args:
            content: File content
            
        Returns:
            True if format is valid
        """
        # Check for required sections
        required_sections = ['# ', '## Overview', '## Last Updated']
        
        for section in required_sections:
            if section not in content:
                return False
        
        return True
    
    def _validate_metadata(self, content: str) -> bool:
        """
        Validate metadata presence.
        
        Args:
            content: File content
            
        Returns:
            True if metadata is valid
        """
        metadata = self._extract_metadata(content)
        
        required_fields = ['Date', 'Source', 'Version', 'Checksum']
        
        for field in required_fields:
            if field not in metadata:
                return False
        
        return True
    
    def _calculate_checksum(self, content: str) -> str:
        """
        Calculate MD5 checksum of content.
        
        Args:
            content: Content to checksum
            
        Returns:
            MD5 checksum
        """
        return hashlib.md5(content.encode('utf-8')).hexdigest()
    
    def _calculate_age_hours(self, last_modified: str) -> float:
        """
        Calculate age of file in hours.
        
        Args:
            last_modified: Last modified timestamp
            
        Returns:
            Age in hours
        """
        try:
            last_modified_dt = datetime.fromisoformat(last_modified.replace('Z', '+00:00'))
            now = datetime.now(last_modified_dt.tzinfo)
            age = now - last_modified_dt
            return age.total_seconds() / 3600
        except Exception:
            return 999  # Return high age if parsing fails
