"""
Smart Agent Selection

Intelligently selects which agents to generate based on project context.

Pattern: Rule-based selection using detected frameworks and project characteristics
"""

from typing import List, Dict, Any, Set


class AgentSelector:
    """
    Intelligently selects agents based on project analysis.

    Instead of generating all 15 base agents, selects only relevant ones
    based on detected languages, frameworks, project type, etc.
    """

    # Universal agents every project needs
    UNIVERSAL_AGENTS = {
        'specifier',   # Requirements definition
        'reviewer',    # Code review
        'planner',     # Task breakdown
    }

    def select_agents(self, project_context: Dict[str, Any]) -> List[Dict[str, str]]:
        """
        Select relevant agents based on project context.

        Args:
            project_context: Project metadata (tech_stack, frameworks, etc.)

        Returns:
            List of agent specs: [{'type': 'implementer', 'name': 'python-backend-implementer', 'focus': '...'}]
        """
        selected = []

        # Extract context
        tech_stack = project_context.get('tech_stack', [])
        frameworks = project_context.get('frameworks', [])
        languages = self._detect_languages(tech_stack + frameworks)
        detected_frameworks = self._detect_frameworks(tech_stack + frameworks)

        # 1. Universal agents (always include)
        for agent_type in self.UNIVERSAL_AGENTS:
            selected.append({
                'type': agent_type,
                'name': agent_type,
                'specialization': 'Universal - applies to all projects',
                'focus': self._get_universal_focus(agent_type)
            })

        # 2. Language-specific agents
        if 'python' in languages:
            selected.extend([
                {
                    'type': 'implementer',
                    'name': 'python-implementer',
                    'specialization': 'Python code implementation',
                    'focus': 'Python patterns, type hints, Pydantic models, pytest'
                },
                {
                    'type': 'tester',
                    'name': 'python-tester',
                    'specialization': 'Python testing with pytest',
                    'focus': 'pytest fixtures, coverage, unit and integration tests'
                },
                {
                    'type': 'debugger',
                    'name': 'python-debugger',
                    'specialization': 'Python debugging and error analysis',
                    'focus': 'Stack traces, pdb, error patterns'
                }
            ])

        if 'javascript' in languages or 'typescript' in languages:
            lang = 'typescript' if 'typescript' in languages else 'javascript'
            selected.extend([
                {
                    'type': 'implementer',
                    'name': f'{lang}-implementer',
                    'specialization': f'{lang.title()} implementation',
                    'focus': f'{lang.title()} patterns, async/await, error handling'
                },
                {
                    'type': 'tester',
                    'name': f'{lang}-tester',
                    'specialization': f'{lang.title()} testing',
                    'focus': 'Jest/Vitest, component testing, mocking'
                }
            ])

        # 3. Framework-specific agents
        if 'django' in detected_frameworks:
            selected.extend([
                {
                    'type': 'implementer',
                    'name': 'django-backend-implementer',
                    'specialization': 'Django backend development',
                    'focus': 'Django models, views, serializers, ORM, migrations'
                },
                {
                    'type': 'integrator',
                    'name': 'django-api-integrator',
                    'specialization': 'Django REST API development',
                    'focus': 'DRF viewsets, serializers, permissions, API design'
                },
                {
                    'type': 'tester',
                    'name': 'django-tester',
                    'specialization': 'Django testing specialist',
                    'focus': 'Django TestCase, fixtures, database testing'
                }
            ])

        if 'react' in detected_frameworks:
            selected.extend([
                {
                    'type': 'implementer',
                    'name': 'react-frontend-implementer',
                    'specialization': 'React component development',
                    'focus': 'React hooks, components, state management, routing'
                },
                {
                    'type': 'tester',
                    'name': 'react-tester',
                    'specialization': 'React component testing',
                    'focus': 'React Testing Library, Jest, component tests'
                }
            ])

        if 'flask' in detected_frameworks:
            selected.append({
                'type': 'implementer',
                'name': 'flask-api-implementer',
                'specialization': 'Flask API development',
                'focus': 'Flask routes, blueprints, request handling, API design'
            })

        if 'fastapi' in detected_frameworks:
            selected.append({
                'type': 'implementer',
                'name': 'fastapi-implementer',
                'specialization': 'FastAPI development',
                'focus': 'FastAPI routes, Pydantic models, async endpoints, OpenAPI'
            })

        # 4. Project-type specific agents
        project_type = project_context.get('app_type', '').lower()

        if 'web' in project_type or 'api' in project_type:
            selected.append({
                'type': 'documenter',
                'name': 'api-documenter',
                'specialization': 'API documentation specialist',
                'focus': 'OpenAPI/Swagger docs, endpoint documentation, examples'
            })

        if 'mobile' in project_type:
            selected.append({
                'type': 'tester',
                'name': 'mobile-tester',
                'specialization': 'Mobile app testing',
                'focus': 'Device testing, responsive design, mobile-specific bugs'
            })

        # 5. Infrastructure agents (if CI/CD detected)
        if self._has_cicd(project_context):
            selected.extend([
                {
                    'type': 'automator',
                    'name': 'cicd-automator',
                    'specialization': 'CI/CD pipeline management',
                    'focus': 'GitHub Actions, automated testing, deployment'
                },
                {
                    'type': 'deployer',
                    'name': 'deployment-specialist',
                    'specialization': 'Application deployment',
                    'focus': 'Docker, cloud deployment, environment config'
                }
            ])

        # Remove duplicates (keep first occurrence)
        seen = set()
        unique_selected = []
        for agent in selected:
            if agent['name'] not in seen:
                seen.add(agent['name'])
                unique_selected.append(agent)

        return unique_selected

    def _detect_languages(self, tech_items: List[str]) -> Set[str]:
        """Detect programming languages from tech stack"""
        languages = set()
        tech_lower = [t.lower() for t in tech_items]

        if any('python' in t for t in tech_lower):
            languages.add('python')
        if any('javascript' in t or 'js' in t for t in tech_lower):
            languages.add('javascript')
        if any('typescript' in t or 'ts' in t for t in tech_lower):
            languages.add('typescript')
        if any('go' in t or 'golang' in t for t in tech_lower):
            languages.add('go')
        if any('rust' in t for t in tech_lower):
            languages.add('rust')
        if any('java' in t for t in tech_lower):
            languages.add('java')

        return languages

    def _detect_frameworks(self, tech_items: List[str]) -> Set[str]:
        """Detect frameworks from tech stack"""
        frameworks = set()
        tech_lower = [t.lower() for t in tech_items]

        if any('django' in t for t in tech_lower):
            frameworks.add('django')
        if any('flask' in t for t in tech_lower):
            frameworks.add('flask')
        if any('fastapi' in t for t in tech_lower):
            frameworks.add('fastapi')
        if any('react' in t for t in tech_lower):
            frameworks.add('react')
        if any('vue' in t for t in tech_lower):
            frameworks.add('vue')
        if any('angular' in t for t in tech_lower):
            frameworks.add('angular')
        if any('next' in t for t in tech_lower):
            frameworks.add('nextjs')

        return frameworks

    def _has_cicd(self, project_context: Dict[str, Any]) -> bool:
        """Check if project has CI/CD setup"""
        tech_stack = project_context.get('tech_stack', [])
        tech_lower = [t.lower() for t in tech_stack]

        cicd_indicators = ['github actions', 'gitlab ci', 'jenkins', 'circleci', '.github/workflows']
        return any(indicator in ' '.join(tech_lower) for indicator in cicd_indicators)

    def _get_universal_focus(self, agent_type: str) -> str:
        """Get focus description for universal agents"""
        focuses = {
            'specifier': 'Requirements gathering, acceptance criteria, user stories',
            'reviewer': 'Code quality, pattern compliance, best practices',
            'planner': 'Task decomposition, effort estimation, dependency mapping'
        }
        return focuses.get(agent_type, 'General project support')
