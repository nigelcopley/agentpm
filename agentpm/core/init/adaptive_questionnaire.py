"""
Adaptive Questionnaire Engine for Enhanced Initialization System - WI-147

This module implements an intelligent questionnaire system that adapts questions
based on detected technologies, project complexity, and architectural patterns.
It builds upon the existing QuestionnaireService to provide context-aware
question generation and smart defaults.

Key Features:
- Dynamic question generation based on detection results
- Technology-specific question sets
- Complexity-based question adaptation
- Smart defaults with confidence scoring
- Progressive disclosure of questions
- Context-aware question ordering

Usage:
    from agentpm.core.init.adaptive_questionnaire import AdaptiveQuestionnaireEngine
    from agentpm.core.detection.models import DetectionResult
    
    engine = AdaptiveQuestionnaireEngine(detection_result, complexity_metrics)
    questions = engine.generate_questions()
    answers = engine.run_questionnaire(questions)
"""

from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import box
import questionary
from questionary import Style, Choice

from agentpm.core.detection.models import DetectionResult, TechnologyMatch
from agentpm.core.database.enums import ApplicationProjectType


class QuestionType(Enum):
    """Types of questions in the adaptive questionnaire"""
    BASIC = "basic"
    TECHNOLOGY_SPECIFIC = "technology_specific"
    ARCHITECTURE_SPECIFIC = "architecture_specific"
    COMPLEXITY_SPECIFIC = "complexity_specific"
    ENTERPRISE_SPECIFIC = "enterprise_specific"


class ComplexityLevel(Enum):
    """Project complexity levels"""
    SIMPLE = "simple"
    MODERATE = "moderate"
    COMPLEX = "complex"
    ENTERPRISE = "enterprise"


@dataclass
class Question:
    """Represents a single question in the adaptive questionnaire"""
    id: str
    text: str
    question_type: QuestionType
    choices: List[Choice]
    default_value: Any
    required: bool = True
    conditional_on: Optional[str] = None
    confidence_threshold: float = 0.0
    description: Optional[str] = None


@dataclass
class QuestionSet:
    """Represents a set of related questions"""
    name: str
    questions: List[Question]
    priority: int
    required_for_complexity: List[ComplexityLevel]


class AdaptiveQuestionnaireEngine:
    """Enhanced questionnaire engine with adaptive question generation"""
    
    def __init__(
        self,
        detection_result: Optional[DetectionResult] = None,
        complexity_metrics: Optional[Dict[str, Any]] = None,
        console: Optional[Console] = None
    ):
        """Initialize the adaptive questionnaire engine
        
        Args:
            detection_result: Technology detection results
            complexity_metrics: Project complexity analysis
            console: Rich console for output
        """
        self.detection_result = detection_result
        self.complexity_metrics = complexity_metrics or {}
        self.console = console or Console()
        self.answers: Dict[str, Any] = {}
        self.complexity_level = self._assess_complexity_level()
        
        # Questionary styling
        self.style = Style([
            ('highlighted', 'bg:cyan fg:black bold'),
            ('pointer', 'fg:cyan bold'),
            ('answer', 'fg:green bold'),
            ('detected', 'fg:yellow bold'),
        ])
    
    def _assess_complexity_level(self) -> ComplexityLevel:
        """Assess project complexity level based on detection and metrics"""
        if not self.complexity_metrics:
            return ComplexityLevel.SIMPLE
        
        # Calculate complexity score
        tech_count = len(self.detection_result.matches) if self.detection_result else 0
        file_count = self.complexity_metrics.get('total_files', 0)
        dependency_count = self.complexity_metrics.get('total_dependencies', 0)
        
        # Simple scoring algorithm
        complexity_score = (
            (tech_count * 0.3) +
            (min(file_count / 100, 1.0) * 0.3) +
            (min(dependency_count / 50, 1.0) * 0.4)
        )
        
        if complexity_score < 0.3:
            return ComplexityLevel.SIMPLE
        elif complexity_score < 0.6:
            return ComplexityLevel.MODERATE
        elif complexity_score < 0.8:
            return ComplexityLevel.COMPLEX
        else:
            return ComplexityLevel.ENTERPRISE
    
    def generate_questions(self) -> List[Question]:
        """Generate adaptive questions based on project context"""
        questions = []
        
        # Always include basic questions
        questions.extend(self._get_basic_questions())
        
        # Add technology-specific questions
        if self.detection_result and self.detection_result.matches:
            questions.extend(self._get_technology_specific_questions())
        
        # Add architecture-specific questions
        if self.complexity_level in [ComplexityLevel.COMPLEX, ComplexityLevel.ENTERPRISE]:
            questions.extend(self._get_architecture_specific_questions())
        
        # Add complexity-specific questions
        if self.complexity_level in [ComplexityLevel.MODERATE, ComplexityLevel.COMPLEX, ComplexityLevel.ENTERPRISE]:
            questions.extend(self._get_complexity_specific_questions())
        
        # Add enterprise-specific questions
        if self.complexity_level == ComplexityLevel.ENTERPRISE:
            questions.extend(self._get_enterprise_specific_questions())
        
        # Sort questions by priority and dependencies
        return self._sort_questions(questions)
    
    def _get_basic_questions(self) -> List[Question]:
        """Get basic questions that apply to all projects"""
        return [
            Question(
                id="project_type",
                text="What type of project is this?",
                question_type=QuestionType.BASIC,
                choices=self._get_project_type_choices(),
                default_value=self._get_smart_default_project_type(),
                description="Determines the overall project structure and requirements"
            ),
            Question(
                id="primary_language",
                text="What is the primary programming language?",
                question_type=QuestionType.BASIC,
                choices=self._get_language_choices(),
                default_value=self._get_smart_default_language(),
                description="Primary language for development and tooling"
            ),
            Question(
                id="development_stage",
                text="What is the current development stage?",
                question_type=QuestionType.BASIC,
                choices=self._get_development_stage_choices(),
                default_value="mvp",
                description="Current maturity level of the project"
            ),
            Question(
                id="team_size",
                text="What is the team size?",
                question_type=QuestionType.BASIC,
                choices=self._get_team_size_choices(),
                default_value=self._get_smart_default_team_size(),
                description="Team composition affects process and tooling choices"
            )
        ]
    
    def _get_technology_specific_questions(self) -> List[Question]:
        """Get questions specific to detected technologies"""
        questions = []
        
        if not self.detection_result:
            return questions
        
        # Backend framework questions
        backend_techs = self._get_detected_backend_technologies()
        if backend_techs:
            questions.append(Question(
                id="backend_framework",
                text="Which backend framework are you using?",
                question_type=QuestionType.TECHNOLOGY_SPECIFIC,
                choices=self._get_backend_framework_choices(backend_techs),
                default_value=self._get_smart_default_backend(),
                description="Backend framework for API and business logic"
            ))
        
        # Frontend framework questions
        frontend_techs = self._get_detected_frontend_technologies()
        if frontend_techs:
            questions.append(Question(
                id="frontend_framework",
                text="Which frontend framework are you using?",
                question_type=QuestionType.TECHNOLOGY_SPECIFIC,
                choices=self._get_frontend_framework_choices(frontend_techs),
                default_value=self._get_smart_default_frontend(),
                description="Frontend framework for user interface"
            ))
        
        # Database questions
        db_techs = self._get_detected_database_technologies()
        if db_techs:
            questions.append(Question(
                id="database",
                text="Which database are you using?",
                question_type=QuestionType.TECHNOLOGY_SPECIFIC,
                choices=self._get_database_choices(db_techs),
                default_value=self._get_smart_default_database(),
                description="Primary database for data storage"
            ))
        
        # Testing framework questions
        test_techs = self._get_detected_testing_technologies()
        if test_techs:
            questions.append(Question(
                id="testing_framework",
                text="Which testing framework are you using?",
                question_type=QuestionType.TECHNOLOGY_SPECIFIC,
                choices=self._get_testing_framework_choices(test_techs),
                default_value=self._get_smart_default_testing(),
                description="Testing framework for quality assurance"
            ))
        
        return questions
    
    def _get_architecture_specific_questions(self) -> List[Question]:
        """Get questions specific to architectural patterns"""
        return [
            Question(
                id="architecture_style",
                text="What architecture style does the project follow?",
                question_type=QuestionType.ARCHITECTURE_SPECIFIC,
                choices=self._get_architecture_style_choices(),
                default_value=self._get_smart_default_architecture(),
                description="Architectural pattern for system design"
            ),
            Question(
                id="deployment_strategy",
                text="What deployment strategy do you use?",
                question_type=QuestionType.ARCHITECTURE_SPECIFIC,
                choices=self._get_deployment_strategy_choices(),
                default_value=self._get_smart_default_deployment(),
                description="How the application is deployed and managed"
            ),
            Question(
                id="scalability_requirements",
                text="What are your scalability requirements?",
                question_type=QuestionType.ARCHITECTURE_SPECIFIC,
                choices=self._get_scalability_choices(),
                default_value="moderate",
                description="Expected load and scaling needs"
            )
        ]
    
    def _get_complexity_specific_questions(self) -> List[Question]:
        """Get questions for moderate to complex projects"""
        return [
            Question(
                id="development_approach",
                text="What development approach do you follow?",
                question_type=QuestionType.COMPLEXITY_SPECIFIC,
                choices=self._get_development_approach_choices(),
                default_value="agile",
                description="Development methodology and practices"
            ),
            Question(
                id="code_review_required",
                text="Is code review required before merging?",
                question_type=QuestionType.COMPLEXITY_SPECIFIC,
                choices=self._get_yes_no_choices(),
                default_value=True,
                description="Code review process for quality assurance"
            ),
            Question(
                id="test_coverage_target",
                text="What is the target test coverage percentage?",
                question_type=QuestionType.COMPLEXITY_SPECIFIC,
                choices=self._get_test_coverage_choices(),
                default_value=self._get_smart_default_test_coverage(),
                description="Minimum acceptable test coverage"
            ),
            Question(
                id="time_boxing_hours",
                text="What is the maximum hours for implementation tasks?",
                question_type=QuestionType.COMPLEXITY_SPECIFIC,
                choices=self._get_time_boxing_choices(),
                default_value=self._get_smart_default_time_boxing(),
                description="Maximum time for individual implementation tasks"
            )
        ]
    
    def _get_enterprise_specific_questions(self) -> List[Question]:
        """Get questions for enterprise-level projects"""
        return [
            Question(
                id="compliance_requirements",
                text="What compliance requirements do you have?",
                question_type=QuestionType.ENTERPRISE_SPECIFIC,
                choices=self._get_compliance_choices(),
                default_value=[],
                description="Regulatory and compliance requirements"
            ),
            Question(
                id="security_requirements",
                text="What security requirements do you have?",
                question_type=QuestionType.ENTERPRISE_SPECIFIC,
                choices=self._get_security_choices(),
                default_value="standard",
                description="Security standards and requirements"
            ),
            Question(
                id="monitoring_requirements",
                text="What monitoring and observability do you need?",
                question_type=QuestionType.ENTERPRISE_SPECIFIC,
                choices=self._get_monitoring_choices(),
                default_value="basic",
                description="Application monitoring and observability"
            ),
            Question(
                id="disaster_recovery",
                text="What disaster recovery requirements do you have?",
                question_type=QuestionType.ENTERPRISE_SPECIFIC,
                choices=self._get_disaster_recovery_choices(),
                default_value="basic",
                description="Backup and disaster recovery planning"
            )
        ]
    
    def run_questionnaire(self, questions: List[Question]) -> Dict[str, Any]:
        """Run the adaptive questionnaire with generated questions"""
        self.console.print(self._get_welcome_panel())
        
        total_questions = len(questions)
        self.console.print(f"\n[cyan]Running adaptive questionnaire with {total_questions} questions[/cyan]")
        self.console.print(f"[dim]Complexity level: {self.complexity_level.value}[/dim]\n")
        
        for i, question in enumerate(questions, 1):
            self._ask_question(question, i, total_questions)
        
        # Show summary and confirm
        if self._confirm_answers():
            self.console.print("\n[green]✓ Configuration complete![/green]")
            return self.answers
        else:
            # Restart questionnaire
            self.console.print("\n[yellow]Restarting questionnaire...[/yellow]")
            self.answers = {}
            return self.run_questionnaire(questions)
    
    def _ask_question(self, question: Question, question_num: int, total_questions: int) -> None:
        """Ask a single question with adaptive behavior"""
        if question.id in self.answers:
            return  # Skip if already answered
        
        # Show question header
        self.console.print(f"\n[bold]Question {question_num} of {total_questions}: {question.text}[/bold]")
        if question.description:
            self.console.print(f"[dim]{question.description}[/dim]")
        
        # Check if we should skip this question
        if self._should_skip_question(question):
            self._auto_fill_question(question)
            return
        
        # Ask the question
        if isinstance(question.choices[0], Choice):
            # Multiple choice question
            choice = questionary.select(
                f"Choose {question.id.replace('_', ' ')}:",
                choices=question.choices,
                default=question.default_value,
                style=self.style,
                qmark="→",
            ).ask()
            self.answers[question.id] = choice
        else:
            # Text input question
            answer = questionary.text(
                f"Enter {question.id.replace('_', ' ')}:",
                default=str(question.default_value),
                style=self.style,
                qmark="→",
            ).ask()
            self.answers[question.id] = answer
    
    def _should_skip_question(self, question: Question) -> bool:
        """Determine if a question should be skipped based on context"""
        # Skip if we have high confidence detection for technology questions
        if question.question_type == QuestionType.TECHNOLOGY_SPECIFIC:
            if question.id == "backend_framework":
                detected = self._get_smart_default_backend()
                confidence = self._get_detection_confidence(detected) if detected else 0.0
                if confidence > 0.8:
                    self.answers[question.id] = detected
                    return True
        
        return False
    
    def _auto_fill_question(self, question: Question) -> None:
        """Auto-fill a question with detected value"""
        detected_value = self.answers.get(question.id)
        if detected_value:
            confidence = self._get_detection_confidence(detected_value)
            self.console.print(f"✓ [dim]{question.text}: {detected_value} (detected: {confidence:.0%} confidence)[/dim]")
    
    def _get_welcome_panel(self) -> Panel:
        """Get welcome panel with adaptive information"""
        complexity_info = f"Complexity Level: {self.complexity_level.value.title()}"
        tech_info = f"Technologies Detected: {len(self.detection_result.matches) if self.detection_result else 0}"
        
        welcome_text = f"""
[bold cyan]APM (Agent Project Manager) Adaptive Configuration[/bold cyan]

This questionnaire adapts to your project's complexity and detected technologies
to provide the most relevant configuration options.

[bold]Project Analysis:[/bold]
• {complexity_info}
• {tech_info}
• Questions will be tailored to your specific context

[yellow]Instructions:[/yellow]
• Questions adapt based on detected technologies
• High-confidence detections are auto-filled
• Review and confirm your answers at the end
"""
        return Panel(welcome_text, box=box.DOUBLE, border_style="cyan")
    
    def _confirm_answers(self) -> bool:
        """Display answers summary and confirm with user"""
        table = Table(
            title="Adaptive Configuration Summary",
            show_header=True,
            header_style="bold cyan",
            box=box.ROUNDED
        )
        table.add_column("Question", style="cyan", width=30)
        table.add_column("Answer", style="yellow")
        table.add_column("Type", style="dim")
        
        for question_id, answer in self.answers.items():
            question_type = "Auto-detected" if self._was_auto_detected(question_id) else "Manual"
            table.add_row(
                question_id.replace('_', ' ').title(),
                str(answer),
                question_type
            )
        
        self.console.print("\n")
        self.console.print(table)
        self.console.print("\n")
        
        return questionary.confirm(
            "[bold]Are these answers correct?[/bold]",
            default=True,
            style=self.style
        ).ask()
    
    def _was_auto_detected(self, question_id: str) -> bool:
        """Check if a question was auto-detected"""
        if not self.detection_result:
            return False
        
        # Check if this question has a high-confidence detection
        if question_id == "backend_framework":
            detected = self._get_smart_default_backend()
            return detected and self._get_detection_confidence(detected) > 0.8
        elif question_id == "frontend_framework":
            detected = self._get_smart_default_frontend()
            return detected and self._get_detection_confidence(detected) > 0.8
        elif question_id == "database":
            detected = self._get_smart_default_database()
            return detected and self._get_detection_confidence(detected) > 0.8
        
        return False
    
    # Smart default methods
    def _get_smart_default_project_type(self) -> str:
        """Get smart default project type from detection"""
        if not self.detection_result:
            return "web_app"
        
        # Map detected technologies to project types
        detection_to_type = {
            'django': 'web_app',
            'flask': 'web_app',
            'fastapi': 'api',
            'click': 'cli',
            'react': 'web_app',
            'vue': 'web_app',
            'angular': 'web_app'
        }
        
        for tech, match in self.detection_result.matches.items():
            if match.confidence > 0.6 and tech in detection_to_type:
                return detection_to_type[tech]
        
        return "web_app"
    
    def _get_smart_default_language(self) -> str:
        """Get smart default language from detection"""
        if not self.detection_result:
            return "python"
        
        # Get primary language from detection
        primary_lang = self.detection_result.get_primary_language()
        return primary_lang if primary_lang else "python"
    
    def _get_smart_default_team_size(self) -> str:
        """Get smart default team size based on complexity"""
        if self.complexity_level == ComplexityLevel.SIMPLE:
            return "solo"
        elif self.complexity_level == ComplexityLevel.MODERATE:
            return "small"
        elif self.complexity_level == ComplexityLevel.COMPLEX:
            return "medium"
        else:
            return "large"
    
    def _get_smart_default_backend(self) -> Optional[str]:
        """Get smart default backend from detection"""
        if not self.detection_result:
            return None
        
        backend_techs = ['django', 'flask', 'fastapi', 'express', 'spring', 'rails']
        for tech in backend_techs:
            if tech in self.detection_result.matches:
                match = self.detection_result.matches[tech]
                if match.confidence > 0.6:
                    return tech
        
        return None
    
    def _get_smart_default_frontend(self) -> Optional[str]:
        """Get smart default frontend from detection"""
        if not self.detection_result:
            return None
        
        frontend_techs = ['react', 'vue', 'angular', 'svelte']
        for tech in frontend_techs:
            if tech in self.detection_result.matches:
                match = self.detection_result.matches[tech]
                if match.confidence > 0.6:
                    return tech
        
        return None
    
    def _get_smart_default_database(self) -> Optional[str]:
        """Get smart default database from detection"""
        if not self.detection_result:
            return None
        
        db_techs = ['postgresql', 'mysql', 'sqlite', 'mongodb', 'redis']
        for tech in db_techs:
            if tech in self.detection_result.matches:
                match = self.detection_result.matches[tech]
                if match.confidence > 0.6:
                    return tech
        
        return None
    
    def _get_smart_default_testing(self) -> Optional[str]:
        """Get smart default testing framework from detection"""
        if not self.detection_result:
            return None
        
        test_techs = ['pytest', 'jest', 'mocha', 'junit', 'rspec']
        for tech in test_techs:
            if tech in self.detection_result.matches:
                match = self.detection_result.matches[tech]
                if match.confidence > 0.6:
                    return tech
        
        return None
    
    def _get_smart_default_architecture(self) -> str:
        """Get smart default architecture based on complexity"""
        if self.complexity_level == ComplexityLevel.SIMPLE:
            return "monolith"
        elif self.complexity_level == ComplexityLevel.MODERATE:
            return "modular_monolith"
        elif self.complexity_level == ComplexityLevel.COMPLEX:
            return "microservices"
        else:
            return "microservices"
    
    def _get_smart_default_deployment(self) -> str:
        """Get smart default deployment strategy"""
        if self.complexity_level in [ComplexityLevel.SIMPLE, ComplexityLevel.MODERATE]:
            return "manual"
        else:
            return "ci_cd"
    
    def _get_smart_default_test_coverage(self) -> int:
        """Get smart default test coverage based on complexity"""
        if self.complexity_level == ComplexityLevel.SIMPLE:
            return 70
        elif self.complexity_level == ComplexityLevel.MODERATE:
            return 80
        elif self.complexity_level == ComplexityLevel.COMPLEX:
            return 90
        else:
            return 95
    
    def _get_smart_default_time_boxing(self) -> float:
        """Get smart default time boxing based on complexity"""
        if self.complexity_level == ComplexityLevel.SIMPLE:
            return 8.0
        elif self.complexity_level == ComplexityLevel.MODERATE:
            return 6.0
        elif self.complexity_level == ComplexityLevel.COMPLEX:
            return 4.0
        else:
            return 3.0
    
    def _get_detection_confidence(self, technology: str) -> float:
        """Get confidence score for detected technology"""
        if not self.detection_result or not technology:
            return 0.0
        
        match = self.detection_result.matches.get(technology)
        return match.confidence if match else 0.0
    
    # Helper methods for getting detected technologies
    def _get_detected_backend_technologies(self) -> List[str]:
        """Get list of detected backend technologies"""
        if not self.detection_result:
            return []
        
        backend_techs = ['django', 'flask', 'fastapi', 'express', 'spring', 'rails']
        return [tech for tech in backend_techs if tech in self.detection_result.matches]
    
    def _get_detected_frontend_technologies(self) -> List[str]:
        """Get list of detected frontend technologies"""
        if not self.detection_result:
            return []
        
        frontend_techs = ['react', 'vue', 'angular', 'svelte']
        return [tech for tech in frontend_techs if tech in self.detection_result.matches]
    
    def _get_detected_database_technologies(self) -> List[str]:
        """Get list of detected database technologies"""
        if not self.detection_result:
            return []
        
        db_techs = ['postgresql', 'mysql', 'sqlite', 'mongodb', 'redis']
        return [tech for tech in db_techs if tech in self.detection_result.matches]
    
    def _get_detected_testing_technologies(self) -> List[str]:
        """Get list of detected testing technologies"""
        if not self.detection_result:
            return []
        
        test_techs = ['pytest', 'jest', 'mocha', 'junit', 'rspec']
        return [tech for tech in test_techs if tech in self.detection_result.matches]
    
    # Choice generation methods
    def _get_project_type_choices(self) -> List[Choice]:
        """Get project type choices with detection indicators"""
        choices = []
        for project_type in ApplicationProjectType:
            # Check if this project type matches detected technologies
            detected_indicator = ""
            if self.detection_result:
                # Add detection confidence for relevant project types
                pass  # Implementation would check detection confidence
            
            choices.append(Choice(
                f"{project_type.get_display_name(project_type.value)} - {project_type.get_description(project_type.value)}{detected_indicator}",
                value=project_type.value
            ))
        return choices
    
    def _get_language_choices(self) -> List[Choice]:
        """Get language choices with detection indicators"""
        languages = ["python", "javascript", "typescript", "go", "rust", "java", "other"]
        choices = []
        
        for lang in languages:
            detected_indicator = ""
            if self.detection_result and lang in self.detection_result.matches:
                confidence = self.detection_result.matches[lang].confidence
                detected_indicator = f" [✓ Detected: {confidence:.0%} confidence]"
            
            choices.append(Choice(f"{lang}{detected_indicator}", value=lang))
        
        return choices
    
    def _get_development_stage_choices(self) -> List[Choice]:
        """Get development stage choices"""
        stages = [
            ("prototype", "Early prototype or proof of concept"),
            ("mvp", "Minimum viable product"),
            ("production", "Production-ready application"),
            ("enterprise", "Enterprise-scale application")
        ]
        
        return [Choice(f"{name} - {desc}", value=name) for name, desc in stages]
    
    def _get_team_size_choices(self) -> List[Choice]:
        """Get team size choices"""
        sizes = [
            ("solo", "Solo developer"),
            ("small", "Small team (2-5 developers)"),
            ("medium", "Medium team (6-15 developers)"),
            ("large", "Large team (16+ developers)")
        ]
        
        return [Choice(f"{name} - {desc}", value=name) for name, desc in sizes]
    
    def _get_backend_framework_choices(self, detected_techs: List[str]) -> List[Choice]:
        """Get backend framework choices with detection indicators"""
        frameworks = {
            'django': 'Django - Full-featured Python web framework',
            'flask': 'Flask - Lightweight Python web framework',
            'fastapi': 'FastAPI - Modern Python API framework',
            'express': 'Express - Minimal Node.js web framework',
            'spring': 'Spring - Enterprise Java framework',
            'rails': 'Rails - Full-stack Ruby web framework'
        }
        
        choices = []
        for tech, description in frameworks.items():
            detected_indicator = ""
            if tech in detected_techs:
                confidence = self._get_detection_confidence(tech)
                detected_indicator = f" [✓ Detected: {confidence:.0%} confidence]"
            
            choices.append(Choice(f"{description}{detected_indicator}", value=tech))
        
        return choices
    
    def _get_frontend_framework_choices(self, detected_techs: List[str]) -> List[Choice]:
        """Get frontend framework choices with detection indicators"""
        frameworks = {
            'react': 'React - JavaScript library for building user interfaces',
            'vue': 'Vue.js - Progressive JavaScript framework',
            'angular': 'Angular - Platform for building mobile and desktop apps',
            'svelte': 'Svelte - Component framework with no virtual DOM'
        }
        
        choices = []
        for tech, description in frameworks.items():
            detected_indicator = ""
            if tech in detected_techs:
                confidence = self._get_detection_confidence(tech)
                detected_indicator = f" [✓ Detected: {confidence:.0%} confidence]"
            
            choices.append(Choice(f"{description}{detected_indicator}", value=tech))
        
        return choices
    
    def _get_database_choices(self, detected_techs: List[str]) -> List[Choice]:
        """Get database choices with detection indicators"""
        databases = {
            'postgresql': 'PostgreSQL - Advanced open-source relational database',
            'mysql': 'MySQL - Popular open-source relational database',
            'sqlite': 'SQLite - Lightweight embedded database',
            'mongodb': 'MongoDB - Document-oriented NoSQL database',
            'redis': 'Redis - In-memory data structure store'
        }
        
        choices = []
        for tech, description in databases.items():
            detected_indicator = ""
            if tech in detected_techs:
                confidence = self._get_detection_confidence(tech)
                detected_indicator = f" [✓ Detected: {confidence:.0%} confidence]"
            
            choices.append(Choice(f"{description}{detected_indicator}", value=tech))
        
        return choices
    
    def _get_testing_framework_choices(self, detected_techs: List[str]) -> List[Choice]:
        """Get testing framework choices with detection indicators"""
        frameworks = {
            'pytest': 'pytest - Python testing framework',
            'jest': 'Jest - JavaScript testing framework',
            'mocha': 'Mocha - JavaScript test framework',
            'junit': 'JUnit - Java testing framework',
            'rspec': 'RSpec - Ruby testing framework'
        }
        
        choices = []
        for tech, description in frameworks.items():
            detected_indicator = ""
            if tech in detected_techs:
                confidence = self._get_detection_confidence(tech)
                detected_indicator = f" [✓ Detected: {confidence:.0%} confidence]"
            
            choices.append(Choice(f"{description}{detected_indicator}", value=tech))
        
        return choices
    
    def _get_architecture_style_choices(self) -> List[Choice]:
        """Get architecture style choices"""
        styles = [
            ("monolith", "Monolith - Single deployable application"),
            ("modular_monolith", "Modular Monolith - One deployable with internal modules"),
            ("microservices", "Microservices - Distributed service architecture"),
            ("serverless", "Serverless - Function-based architecture"),
            ("event_driven", "Event-Driven - Asynchronous event-based architecture")
        ]
        
        return [Choice(f"{name} - {desc}", value=name) for name, desc in styles]
    
    def _get_deployment_strategy_choices(self) -> List[Choice]:
        """Get deployment strategy choices"""
        strategies = [
            ("manual", "Manual - Manual deployment process"),
            ("ci_cd", "CI/CD - Automated continuous integration and deployment"),
            ("gitops", "GitOps - Git-based operational workflows"),
            ("serverless", "Serverless - Function-based deployment")
        ]
        
        return [Choice(f"{name} - {desc}", value=name) for name, desc in strategies]
    
    def _get_scalability_choices(self) -> List[Choice]:
        """Get scalability requirement choices"""
        levels = [
            ("low", "Low - Single server, minimal scaling needs"),
            ("moderate", "Moderate - Multi-server, some scaling requirements"),
            ("high", "High - Distributed system, significant scaling needs"),
            ("enterprise", "Enterprise - Global scale, maximum performance")
        ]
        
        return [Choice(f"{name} - {desc}", value=name) for name, desc in levels]
    
    def _get_development_approach_choices(self) -> List[Choice]:
        """Get development approach choices"""
        approaches = [
            ("agile", "Agile - Iterative development with customer collaboration"),
            ("scrum", "Scrum - Agile framework with sprints and roles"),
            ("kanban", "Kanban - Visual workflow management"),
            ("tdd", "TDD - Test-Driven Development"),
            ("bdd", "BDD - Behaviour-Driven Development"),
            ("waterfall", "Waterfall - Sequential development phases")
        ]
        
        return [Choice(f"{name} - {desc}", value=name) for name, desc in approaches]
    
    def _get_yes_no_choices(self) -> List[Choice]:
        """Get yes/no choices"""
        return [
            Choice("Yes", value=True),
            Choice("No", value=False)
        ]
    
    def _get_test_coverage_choices(self) -> List[Choice]:
        """Get test coverage choices"""
        coverages = [
            ("60", "60% - Basic coverage"),
            ("70", "70% - Good coverage"),
            ("80", "80% - High coverage"),
            ("90", "90% - Very high coverage"),
            ("95", "95% - Excellent coverage")
        ]
        
        return [Choice(f"{name} - {desc}", value=int(name)) for name, desc in coverages]
    
    def _get_time_boxing_choices(self) -> List[Choice]:
        """Get time boxing choices"""
        times = [
            ("2.0", "2 hours - Very focused tasks"),
            ("3.0", "3 hours - Focused tasks"),
            ("4.0", "4 hours - Standard tasks"),
            ("6.0", "6 hours - Longer tasks"),
            ("8.0", "8 hours - Full day tasks")
        ]
        
        return [Choice(f"{name} - {desc}", value=float(name)) for name, desc in times]
    
    def _get_compliance_choices(self) -> List[Choice]:
        """Get compliance requirement choices"""
        compliances = [
            ("gdpr", "GDPR - General Data Protection Regulation"),
            ("hipaa", "HIPAA - Health Insurance Portability and Accountability Act"),
            ("sox", "SOX - Sarbanes-Oxley Act"),
            ("pci_dss", "PCI DSS - Payment Card Industry Data Security Standard"),
            ("iso27001", "ISO 27001 - Information Security Management"),
            ("none", "None - No specific compliance requirements")
        ]
        
        return [Choice(f"{name} - {desc}", value=name) for name, desc in compliances]
    
    def _get_security_choices(self) -> List[Choice]:
        """Get security requirement choices"""
        levels = [
            ("basic", "Basic - Standard security practices"),
            ("enhanced", "Enhanced - Additional security measures"),
            ("high", "High - Comprehensive security requirements"),
            ("enterprise", "Enterprise - Maximum security standards")
        ]
        
        return [Choice(f"{name} - {desc}", value=name) for name, desc in levels]
    
    def _get_monitoring_choices(self) -> List[Choice]:
        """Get monitoring requirement choices"""
        levels = [
            ("basic", "Basic - Simple logging and error tracking"),
            ("standard", "Standard - Application performance monitoring"),
            ("advanced", "Advanced - Comprehensive observability"),
            ("enterprise", "Enterprise - Full observability and alerting")
        ]
        
        return [Choice(f"{name} - {desc}", value=name) for name, desc in levels]
    
    def _get_disaster_recovery_choices(self) -> List[Choice]:
        """Get disaster recovery requirement choices"""
        levels = [
            ("basic", "Basic - Simple backup strategy"),
            ("standard", "Standard - Regular backups with recovery procedures"),
            ("advanced", "Advanced - Multi-region backup and failover"),
            ("enterprise", "Enterprise - Comprehensive disaster recovery plan")
        ]
        
        return [Choice(f"{name} - {desc}", value=name) for name, desc in levels]
    
    def _sort_questions(self, questions: List[Question]) -> List[Question]:
        """Sort questions by priority and dependencies"""
        # Sort by question type priority
        type_priority = {
            QuestionType.BASIC: 1,
            QuestionType.TECHNOLOGY_SPECIFIC: 2,
            QuestionType.ARCHITECTURE_SPECIFIC: 3,
            QuestionType.COMPLEXITY_SPECIFIC: 4,
            QuestionType.ENTERPRISE_SPECIFIC: 5
        }
        
        return sorted(questions, key=lambda q: type_priority.get(q.question_type, 999))


