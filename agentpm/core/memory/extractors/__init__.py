"""
Memory Extractors - Database Data Extraction

Extractors pull data from APM (Agent Project Manager) database tables and format it for memory file generation.
Each extractor handles a specific memory file type and its associated database tables.

Extractors:
    - RulesExtractor: rules table + rules_catalog.yaml
    - PrinciplesExtractor: development_principles.py enum
    - WorkflowExtractor: workflow service + phase validators
    - AgentsExtractor: agents table + agent definitions
    - ContextExtractor: contexts table + context service
    - ProjectExtractor: projects table + project service
    - IdeasExtractor: ideas table + ideas service
"""

from .base_extractor import BaseExtractor
from .rules_extractor import RulesExtractor
from .principles_extractor import PrinciplesExtractor
from .workflow_extractor import WorkflowExtractor
from .agents_extractor import AgentsExtractor
from .context_extractor import ContextExtractor
from .project_extractor import ProjectExtractor
from .ideas_extractor import IdeasExtractor

__all__ = [
    'BaseExtractor',
    'RulesExtractor',
    'PrinciplesExtractor',
    'WorkflowExtractor',
    'AgentsExtractor',
    'ContextExtractor',
    'ProjectExtractor',
    'IdeasExtractor',
]
