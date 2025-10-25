"""TypeScript Plugin - Superset of JavaScript with type safety"""
from pathlib import Path
from typing import Dict, Any
import json, re
from ...base.plugin_interface import BasePlugin
from ...base.types import PluginCategory

class TypeScriptPlugin(BasePlugin):
    @property
    def plugin_id(self) -> str:
        return "lang:typescript"
    
    @property
    def enriches(self) -> str:
        return "typescript"
    
    @property
    def category(self) -> PluginCategory:
        return PluginCategory.LANGUAGE
    
    def detect(self, project_path: Path) -> float:
        confidence = 0.0
        try:
            if (project_path / "tsconfig.json").exists():
                confidence += 0.30
        except: pass
        
        try:
            ts_files = list(project_path.glob("**/*.ts")) + list(project_path.glob("**/*.tsx"))
            count = len(ts_files)
            if count >= 50: confidence += 0.40
            elif count >= 20: confidence += 0.35
            elif count >= 10: confidence += 0.30
            else: confidence += 0.20 if count > 0 else 0.0
        except: pass
        
        try:
            if (project_path / "src").exists():
                confidence += 0.10
            package_json = project_path / "package.json"
            if package_json.exists() and "typescript" in package_json.read_text():
                confidence += 0.20
        except: pass
        
        return min(confidence, 1.0)
    
    def extract_project_facts(self, project_path: Path) -> Dict[str, Any]:
        facts = {'language': 'TypeScript'}
        try:
            tsconfig = json.loads((project_path / "tsconfig.json").read_text())
            facts['typescript_version'] = tsconfig.get('compilerOptions', {}).get('target', 'Unknown')
            facts['strict_mode'] = tsconfig.get('compilerOptions', {}).get('strict', False)
        except: pass
        return facts
    
    def generate_code_amalgamations(self, project_path: Path) -> Dict[str, str]:
        amalgamations = {}
        # Interfaces and types
        types_content = []
        for ts_file in list(project_path.glob("**/types/**/*.ts")) + list(project_path.glob("**/*.types.ts")):
            try:
                content = ts_file.read_text()
                types_content.append(f"# {ts_file.relative_to(project_path)}\n{content}\n")
            except: continue
        amalgamations['types'] = "\n".join(types_content[:20])
        return amalgamations
