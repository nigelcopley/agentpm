"""Interactive questionnaire service for APM (Agent Project Manager) rules configuration.

Provides an interactive CLI workflow for gathering project context through
18 structured questions covering development philosophy, technical stack,
team composition, and project constraints.

WI-51 Enhancement: Smart questionnaire with detection-based defaults.

Usage:
    from agentpm.core.rules.questionnaire import QuestionnaireService
    from agentpm.core.detection.models import DetectionResult

    service = QuestionnaireService(detection_result=detection_result)
    answers = service.run()  # Interactive mode with smart defaults
    answers = service.run(use_defaults=True)  # Skip with defaults
    answers = service.run(resume_from=partial_answers)  # Resume from saved state
"""

from typing import Any, Dict, List, Optional
from rich.console import Console
from rich.prompt import Prompt, Confirm, IntPrompt, FloatPrompt
from rich.panel import Panel
from rich.table import Table
from rich import box
import questionary
from questionary import Style

from agentpm.core.database.enums import ApplicationProjectType


class QuestionnaireService:
    """Interactive questionnaire for APM (Agent Project Manager) rules configuration.

    Implements 18-question workflow with:
    - Conditional logic (Q4-Q6 only for web/API projects)
    - Smart defaults based on previous answers AND detection (WI-51)
    - Rich CLI formatting with panels and tables
    - Arrow-key navigation with questionary (WI-51)
    - Answer validation for each question type
    - Summary confirmation with restart ability
    - Default mode and resume capability
    - Detection-based skip logic (WI-51)
    """

    # Question choices - Expanded comprehensive options
    PROJECT_TYPES = ["web_app", "api", "cli", "library", "desktop_app", "mobile_app"]
    LANGUAGES = ["python", "javascript", "typescript", "go", "rust", "java", "other"]
    DEV_STAGES = ["prototype", "mvp", "production", "enterprise"]
    
    # Comprehensive backend frameworks by language
    BACKEND_FRAMEWORKS = [
        # Python
        "django", "flask", "fastapi", "tornado", "bottle", "pyramid", "sanic", "quart",
        # Node.js/JavaScript
        "express", "koa", "hapi", "nest", "sails", "loopback", "adonis", "feathers",
        # Go
        "gin", "echo", "fiber", "chi", "gorilla", "beego", "iris", "revel",
        # Java
        "spring", "spring_boot", "quarkus", "micronaut", "vertx", "play", "dropwizard", "spark",
        # Rust
        "actix", "warp", "axum", "rocket", "tide", "poem", "salvo", "thruster",
        # C#/.NET
        "aspnet", "aspnet_core", "blazor", "service_stack", "nancy", "orleans",
        # PHP
        "laravel", "symfony", "codeigniter", "cakephp", "phalcon", "slim",
        # Ruby
        "rails", "sinatra", "hanami", "grape", "padrino", "cuba",
        # Other
        "other", "none"
    ]
    
    # Comprehensive frontend frameworks and build tools
    FRONTEND_FRAMEWORKS = [
        # React Ecosystem
        "react", "next", "gatsby", "remix", "react_native", "expo",
        # Vue Ecosystem
        "vue", "nuxt", "quasar", "vue_native",
        # Angular Ecosystem
        "angular", "ionic", "nativescript",
        # Svelte Ecosystem
        "svelte", "sveltekit", "sapper",
        # Other Modern Frameworks
        "solid", "lit", "alpine", "stimulus", "htmx", "astro", "qwik",
        # Build Tools & Meta-frameworks
        "vite", "webpack", "rollup", "parcel", "esbuild", "swc", "turbo",
        # Static Site Generators
        "eleventy", "hugo", "jekyll", "gridsome", "docusaurus",
        # Other
        "other", "none"
    ]
    
    # Comprehensive database options
    DATABASES = [
        # Relational Databases
        "postgresql", "mysql", "mariadb", "sqlite", "oracle", "sql_server", "db2", "cockroachdb",
        # NoSQL Document Stores
        "mongodb", "couchdb", "couchbase", "dynamodb", "firestore", "cosmosdb",
        # NoSQL Key-Value Stores
        "redis", "memcached", "riak", "hazelcast", "aerospike",
        # NoSQL Column Stores
        "cassandra", "hbase", "scylladb", "clickhouse",
        # NoSQL Graph Databases
        "neo4j", "arangodb", "amazon_neptune", "orientdb",
        # Time Series Databases
        "influxdb", "timescaledb", "prometheus", "opentsdb", "questdb",
        # Search Engines
        "elasticsearch", "solr", "opensearch", "meilisearch", "typesense",
        # Cloud Database Services
        "aws_rds", "aws_aurora", "google_cloud_sql", "azure_sql", "planetscale", "supabase",
        # Other
        "other", "none"
    ]
    
    # Comprehensive development approaches and methodologies
    DEV_APPROACHES = [
        # Testing Approaches
        "tdd", "bdd", "atdd", "mdd", "sbe", "property_based_testing",
        # Architecture Approaches
        "ddd", "hexagonal", "clean_architecture", "onion", "microservices", "serverless",
        # Process Methodologies
        "agile", "scrum", "kanban", "xp", "crystal", "fdd", "dsdm", "safe",
        # Traditional Approaches
        "waterfall", "spiral", "v_model", "iterative", "prototype",
        # Modern Practices
        "devops", "gitops", "shift_left", "continuous_delivery", "infrastructure_as_code",
        # Quality Approaches
        "code_review", "pair_programming", "mob_programming", "code_standards", "static_analysis",
        # Other
        "other"
    ]
    # Comprehensive architectural patterns
    ARCHITECTURE_STYLES = [
        # Core Patterns
        "monolith",
        "modular_monolith", 
        "layered_n_tier",
        "hexagonal_ports_adapters",
        "clean_onion",
        "microservices",
        "service_oriented_soa",
        "event_driven",
        "serverless_faas",
        "microkernel_plugin",
        "pipe_and_filter",
        "blackboard",
        "client_server",
        "peer_to_peer",
        "component_based",
        "space_based_grid",
        "cloud_native_12factor",
        
        # Hybrid Patterns
        "modular_monolith_hexagonal",
        "layered_clean_onion", 
        "microservices_event_driven",
        "microkernel_plugin_cloud_native",
        "microservices_serverless",
        "modular_monolith_cqrs_event_sourcing",
        "microservices_space_based_grid",
        "component_based_layered",
        
        # Other
        "other"
    ]
    DEPLOYMENT_STRATEGIES = ["manual", "ci_cd", "gitops", "other"]

    # WI-51: Detection → Technology Mapping
    DETECTION_TO_PROJECT_TYPE = {
        'django': 'web_app',
        'flask': 'web_app',
        'fastapi': 'api',
        'click': 'cli',
        'argparse': 'cli',
        'typer': 'cli',
        'tkinter': 'desktop_app',
        'pyqt': 'desktop_app',
    }

    DETECTION_TO_BACKEND = {
        'django': 'django',
        'flask': 'flask',
        'fastapi': 'fastapi',
        'express': 'express',
        'spring': 'spring',
    }

    DETECTION_TO_FRONTEND = {
        'react': 'react',
        'vue': 'vue',
        'angular': 'angular',
        'svelte': 'svelte',
    }

    DETECTION_TO_DATABASE = {
        'postgresql': 'postgresql',
        'mysql': 'mysql',
        'sqlite': 'sqlite',
        'mongodb': 'mongodb',
    }

    # Questionary styling
    QUESTIONARY_STYLE = Style([
        ('highlighted', 'bg:cyan fg:black bold'),
        ('pointer', 'fg:cyan bold'),
        ('answer', 'fg:green bold'),
    ])

    def __init__(
        self,
        console: Optional[Console] = None,
        detection_result: Optional[Any] = None  # WI-51: DetectionResult
    ):
        """Initialize questionnaire service.

        Args:
            console: Optional Rich Console instance (creates new if None)
            detection_result: Optional DetectionResult for smart defaults (WI-51)
        """
        self.console = console or Console()
        self.detection_result = detection_result
        self.answers: Dict[str, Any] = {}
        self.questions_skipped = 0  # WI-51: Track skipped questions

    # WI-51: Detection Helper Methods
    def _get_smart_default_project_type(self) -> str:
        """Infer project type from detected technologies."""
        if not self.detection_result:
            return "web_app"

        for tech in self.detection_result.get_detected_technologies(min_confidence=0.5):
            if tech in self.DETECTION_TO_PROJECT_TYPE:
                return self.DETECTION_TO_PROJECT_TYPE[tech]

        return "web_app"

    def _get_smart_default_language(self) -> str:
        """Get primary language from detection."""
        if not self.detection_result:
            return "python"

        primary = self.detection_result.get_primary_language()
        return primary if primary else "python"

    def _get_smart_default_backend(self) -> Optional[str]:
        """Get detected backend framework."""
        if not self.detection_result:
            return None

        for tech in self.detection_result.get_detected_technologies(min_confidence=0.5):
            if tech in self.DETECTION_TO_BACKEND:
                return self.DETECTION_TO_BACKEND[tech]

        return None

    def _get_smart_default_frontend(self) -> Optional[str]:
        """Get detected frontend framework."""
        if not self.detection_result:
            return None

        for tech in self.detection_result.get_detected_technologies(min_confidence=0.5):
            if tech in self.DETECTION_TO_FRONTEND:
                return self.DETECTION_TO_FRONTEND[tech]

        return None

    def _get_smart_default_database(self) -> Optional[str]:
        """Get detected database."""
        if not self.detection_result:
            return None

        for tech in self.detection_result.get_detected_technologies(min_confidence=0.5):
            if tech in self.DETECTION_TO_DATABASE:
                return self.DETECTION_TO_DATABASE[tech]

        return None

    def _get_detection_confidence(self, technology: str) -> float:
        """Get confidence score for detected technology."""
        if not self.detection_result or not technology:
            return 0.0

        match = self.detection_result.matches.get(technology)
        return match.confidence if match else 0.0

    def _should_skip_backend_framework(self) -> bool:
        """Q4: Should we skip backend framework question?"""
        project_type = self.answers.get('project_type', 'web_app')
        if project_type not in ['web_app', 'api']:
            return True

        # Check if backend detected with high confidence
        detected_backend = self._get_smart_default_backend()
        if detected_backend and self._get_detection_confidence(detected_backend) > 0.8:
            self.answers['backend_framework'] = detected_backend
            self.questions_skipped += 1
            return True

        return False

    def _should_skip_frontend_framework(self) -> bool:
        """Q5: Should we skip frontend framework question?"""
        project_type = self.answers.get('project_type', 'web_app')
        if project_type != 'web_app':
            self.answers['frontend_framework'] = 'none'
            self.questions_skipped += 1
            return True

        # Check if frontend detected with high confidence
        detected_frontend = self._get_smart_default_frontend()
        if detected_frontend and self._get_detection_confidence(detected_frontend) > 0.8:
            self.answers['frontend_framework'] = detected_frontend
            self.questions_skipped += 1
            return True

        return False

    def _should_skip_database(self) -> bool:
        """Q6: Should we skip database question?"""
        # Check if database detected with high confidence
        detected_db = self._get_smart_default_database()
        if detected_db and self._get_detection_confidence(detected_db) > 0.8:
            self.answers['database'] = detected_db
            self.questions_skipped += 1
            return True

        return False

    def run(
        self,
        use_defaults: bool = False,
        resume_from: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Run interactive questionnaire workflow.

        Args:
            use_defaults: If True, skip all questions and use defaults
            resume_from: Optional partial answers to resume from

        Returns:
            Complete answers dictionary
        """
        # Use defaults mode
        if use_defaults:
            self.console.print("\n[yellow]Using default answers for all questions[/yellow]")
            return self._get_all_defaults()

        # Resume mode
        if resume_from:
            self.answers = resume_from.copy()
            self.console.print(
                f"\n[cyan]Resuming from {len(self.answers)} previous answers[/cyan]"
            )

        # Show welcome panel
        self._show_welcome()

        # Ask all questions
        self._ask_q1_project_type()
        self._ask_q2_primary_language()
        self._ask_q3_development_stage()

        # Conditional questions for web/API projects (WI-51: with smart skip logic)
        if not self._should_skip_backend_framework():
            self._ask_q4_backend_framework()
        else:
            # Show auto-filled value
            backend = self.answers.get('backend_framework')
            if backend:
                confidence = self._get_detection_confidence(backend)
                self.console.print(
                    f"\n✓ [dim]Backend Framework: {backend} "
                    f"(detected: {confidence:.0%} confidence)[/dim]"
                )

        if not self._should_skip_frontend_framework():
            self._ask_q5_frontend_framework()
        else:
            # Show auto-filled value
            frontend = self.answers.get('frontend_framework')
            if frontend and frontend != 'none':
                confidence = self._get_detection_confidence(frontend)
                self.console.print(
                    f"\n✓ [dim]Frontend Framework: {frontend} "
                    f"(detected: {confidence:.0%} confidence)[/dim]"
                )

        if not self._should_skip_database():
            self._ask_q6_database()
        else:
            # Show auto-filled value
            database = self.answers.get('database')
            if database:
                confidence = self._get_detection_confidence(database)
                self.console.print(
                    f"\n✓ [dim]Database: {database} "
                    f"(detected: {confidence:.0%} confidence)[/dim]"
                )

        self._ask_q7_test_coverage()
        self._ask_q8_code_review()
        self._ask_q9_time_boxing()
        self._ask_q10_development_approach()
        self._ask_q11_architecture_style()
        self._ask_q12_deployment_strategy()
        self._ask_q13_team_size_detail()
        self._ask_q14_project_purpose()
        self._ask_q15_target_users()
        self._ask_q16_timeline()
        self._ask_q17_constraints()
        self._ask_q18_tech_rationale()

        # Confirm answers
        while True:
            if self._confirm_answers():
                self.console.print("\n[green]✓ Configuration complete![/green]")
                return self.answers
            else:
                # Restart questionnaire
                self.console.print("\n[yellow]Restarting questionnaire...[/yellow]")
                self.answers = {}
                return self.run(use_defaults=use_defaults)

    def _show_welcome(self) -> None:
        """Display welcome panel with instructions."""
        welcome_text = """
[bold cyan]APM (Agent Project Manager) Interactive Configuration[/bold cyan]

This questionnaire will gather context about your project to generate
customized development rules and guidelines.

[yellow]Instructions:[/yellow]
• Answer 18 questions about your project
• Press Enter to accept default values (shown in [cyan]brackets[/cyan])
• Conditional questions (4-6) only appear for web/API projects
• Review and confirm your answers at the end
"""
        self.console.print(Panel(welcome_text, box=box.DOUBLE, border_style="cyan"))

    def _ask_q1_project_type(self) -> None:
        """Q1: What type of project is this? (WI-51: arrow navigation + smart default)"""
        if "project_type" in self.answers:
            return

        self.console.print("\n[bold]Question 1 of 18: Project Type[/bold]")

        # WI-51: Get smart default from detection
        smart_default = self._get_smart_default_project_type()

        # Build comprehensive choices with descriptions using ApplicationProjectType
        choices = []
        
        # Web Applications
        choices.extend([
            questionary.Choice(
                f"{ApplicationProjectType.get_display_name(ApplicationProjectType.WEB_APP_FULLSTACK.value)} - {ApplicationProjectType.get_description(ApplicationProjectType.WEB_APP_FULLSTACK.value)}", 
                value=ApplicationProjectType.WEB_APP_FULLSTACK.value
            ),
            questionary.Choice(
                f"{ApplicationProjectType.get_display_name(ApplicationProjectType.WEB_APP_FRONTEND.value)} - {ApplicationProjectType.get_description(ApplicationProjectType.WEB_APP_FRONTEND.value)}", 
                value=ApplicationProjectType.WEB_APP_FRONTEND.value
            ),
            questionary.Choice(
                f"{ApplicationProjectType.get_display_name(ApplicationProjectType.WEB_APP_BACKEND.value)} - {ApplicationProjectType.get_description(ApplicationProjectType.WEB_APP_BACKEND.value)}", 
                value=ApplicationProjectType.WEB_APP_BACKEND.value
            ),
        ])
        
        # API Services
        choices.extend([
            questionary.Choice(
                f"{ApplicationProjectType.get_display_name(ApplicationProjectType.API_REST.value)} - {ApplicationProjectType.get_description(ApplicationProjectType.API_REST.value)}", 
                value=ApplicationProjectType.API_REST.value
            ),
            questionary.Choice(
                f"{ApplicationProjectType.get_display_name(ApplicationProjectType.API_GRAPHQL.value)} - {ApplicationProjectType.get_description(ApplicationProjectType.API_GRAPHQL.value)}", 
                value=ApplicationProjectType.API_GRAPHQL.value
            ),
            questionary.Choice(
                f"{ApplicationProjectType.get_display_name(ApplicationProjectType.API_MICROSERVICE.value)} - {ApplicationProjectType.get_description(ApplicationProjectType.API_MICROSERVICE.value)}", 
                value=ApplicationProjectType.API_MICROSERVICE.value
            ),
        ])
        
        # Command Line Tools
        choices.extend([
            questionary.Choice(
                f"{ApplicationProjectType.get_display_name(ApplicationProjectType.CLI_TOOL.value)} - {ApplicationProjectType.get_description(ApplicationProjectType.CLI_TOOL.value)}", 
                value=ApplicationProjectType.CLI_TOOL.value
            ),
            questionary.Choice(
                f"{ApplicationProjectType.get_display_name(ApplicationProjectType.CLI_UTILITY.value)} - {ApplicationProjectType.get_description(ApplicationProjectType.CLI_UTILITY.value)}", 
                value=ApplicationProjectType.CLI_UTILITY.value
            ),
        ])
        
        # Libraries and Packages
        choices.extend([
            questionary.Choice(
                f"{ApplicationProjectType.get_display_name(ApplicationProjectType.LIBRARY_PYTHON.value)} - {ApplicationProjectType.get_description(ApplicationProjectType.LIBRARY_PYTHON.value)}", 
                value=ApplicationProjectType.LIBRARY_PYTHON.value
            ),
            questionary.Choice(
                f"{ApplicationProjectType.get_display_name(ApplicationProjectType.LIBRARY_NODE.value)} - {ApplicationProjectType.get_description(ApplicationProjectType.LIBRARY_NODE.value)}", 
                value=ApplicationProjectType.LIBRARY_NODE.value
            ),
            questionary.Choice(
                f"{ApplicationProjectType.get_display_name(ApplicationProjectType.LIBRARY_RUST.value)} - {ApplicationProjectType.get_description(ApplicationProjectType.LIBRARY_RUST.value)}", 
                value=ApplicationProjectType.LIBRARY_RUST.value
            ),
        ])
        
        # Desktop Applications
        choices.extend([
            questionary.Choice(
                f"{ApplicationProjectType.get_display_name(ApplicationProjectType.DESKTOP_ELECTRON.value)} - {ApplicationProjectType.get_description(ApplicationProjectType.DESKTOP_ELECTRON.value)}", 
                value=ApplicationProjectType.DESKTOP_ELECTRON.value
            ),
            questionary.Choice(
                f"{ApplicationProjectType.get_display_name(ApplicationProjectType.DESKTOP_NATIVE.value)} - {ApplicationProjectType.get_description(ApplicationProjectType.DESKTOP_NATIVE.value)}", 
                value=ApplicationProjectType.DESKTOP_NATIVE.value
            ),
        ])
        
        # Mobile Applications
        choices.extend([
            questionary.Choice(
                f"{ApplicationProjectType.get_display_name(ApplicationProjectType.MOBILE_NATIVE.value)} - {ApplicationProjectType.get_description(ApplicationProjectType.MOBILE_NATIVE.value)}", 
                value=ApplicationProjectType.MOBILE_NATIVE.value
            ),
            questionary.Choice(
                f"{ApplicationProjectType.get_display_name(ApplicationProjectType.MOBILE_CROSS_PLATFORM.value)} - {ApplicationProjectType.get_description(ApplicationProjectType.MOBILE_CROSS_PLATFORM.value)}", 
                value=ApplicationProjectType.MOBILE_CROSS_PLATFORM.value
            ),
        ])
        
        # Data Science and ML
        choices.extend([
            questionary.Choice(
                f"{ApplicationProjectType.get_display_name(ApplicationProjectType.DATA_SCIENCE.value)} - {ApplicationProjectType.get_description(ApplicationProjectType.DATA_SCIENCE.value)}", 
                value=ApplicationProjectType.DATA_SCIENCE.value
            ),
            questionary.Choice(
                f"{ApplicationProjectType.get_display_name(ApplicationProjectType.ML_MODEL.value)} - {ApplicationProjectType.get_description(ApplicationProjectType.ML_MODEL.value)}", 
                value=ApplicationProjectType.ML_MODEL.value
            ),
        ])
        
        # Infrastructure and DevOps
        choices.extend([
            questionary.Choice(
                f"{ApplicationProjectType.get_display_name(ApplicationProjectType.INFRASTRUCTURE.value)} - {ApplicationProjectType.get_description(ApplicationProjectType.INFRASTRUCTURE.value)}", 
                value=ApplicationProjectType.INFRASTRUCTURE.value
            ),
            questionary.Choice(
                f"{ApplicationProjectType.get_display_name(ApplicationProjectType.DEVOPS_TOOL.value)} - {ApplicationProjectType.get_description(ApplicationProjectType.DEVOPS_TOOL.value)}", 
                value=ApplicationProjectType.DEVOPS_TOOL.value
            ),
        ])
        
        # Other
        choices.extend([
            questionary.Choice(
                f"{ApplicationProjectType.get_display_name(ApplicationProjectType.PLUGIN_EXTENSION.value)} - {ApplicationProjectType.get_description(ApplicationProjectType.PLUGIN_EXTENSION.value)}", 
                value=ApplicationProjectType.PLUGIN_EXTENSION.value
            ),
            questionary.Choice(
                f"{ApplicationProjectType.get_display_name(ApplicationProjectType.AUTOMATION_SCRIPT.value)} - {ApplicationProjectType.get_description(ApplicationProjectType.AUTOMATION_SCRIPT.value)}", 
                value=ApplicationProjectType.AUTOMATION_SCRIPT.value
            ),
        ])

        # Find default choice (match value)
        default_idx = next((i for i, c in enumerate(choices) if c.value == smart_default), 0)

        # Use questionary for arrow key navigation
        choice = questionary.select(
            "Choose project type:",
            choices=choices,
            default=choices[default_idx],
            style=self.QUESTIONARY_STYLE,
            qmark="→",
        ).ask()

        self.answers["project_type"] = choice

    def _ask_q2_primary_language(self) -> None:
        """Q2: What is the primary programming language? (WI-51: arrow navigation + smart default)"""
        if "primary_language" in self.answers:
            return

        self.console.print("\n[bold]Question 2 of 18: Primary Language[/bold]")

        # WI-51: Get smart default from detection
        smart_default = self._get_smart_default_language()

        # Check if detected
        detected_language = None
        if self.detection_result and self.detection_result.get_primary_language():
            detected_language = smart_default
            confidence = self._get_detection_confidence(detected_language)

        # Build choices with detection indicator
        choices = []
        for lang in self.LANGUAGES:
            if lang == detected_language and confidence > 0.7:
                label = f"{lang} [✓ Detected: {confidence:.0%} confidence]"
            else:
                label = lang
            choices.append(questionary.Choice(label, value=lang))

        # Find default choice
        default_idx = next((i for i, c in enumerate(choices) if c.value == smart_default), 0)

        # Use questionary for arrow key navigation
        choice = questionary.select(
            "Choose primary language:",
            choices=choices,
            default=choices[default_idx],
            style=self.QUESTIONARY_STYLE,
            qmark="→",
        ).ask()

        self.answers["primary_language"] = choice

    def _ask_q3_development_stage(self) -> None:
        """Q3: What is the current development stage?"""
        if "development_stage" in self.answers:
            return

        self.console.print("\n[bold]Question 3 of 18: Development Stage[/bold]")
        self.console.print("What is the current development stage?")

        choice = Prompt.ask(
            "Choose stage",
            choices=self.DEV_STAGES,
            default="mvp"
        )
        self.answers["development_stage"] = choice

    def _ask_q4_backend_framework(self) -> None:
        """Q4: Which backend framework? (conditional on Q1)"""
        if "backend_framework" in self.answers:
            return

        self.console.print("\n[bold]Question 4 of 18: Backend Framework[/bold]")
        self.console.print("Which backend framework are you using?")

        # Smart default based on language
        language = self.answers.get("primary_language", "python")
        language_defaults = {
            "python": "django",
            "javascript": "express", 
            "typescript": "express",
            "go": "gin",
            "rust": "actix",
            "java": "spring",
            "other": "other"
        }
        default = language_defaults.get(language, "other")

        # Build choices with descriptions
        choices = []
        
        # Python frameworks
        choices.extend([
            questionary.Choice("Django - Full-featured Python web framework with ORM", value="django"),
            questionary.Choice("Flask - Lightweight Python web framework", value="flask"),
            questionary.Choice("FastAPI - Modern Python API framework with automatic docs", value="fastapi"),
            questionary.Choice("Tornado - Python web framework for real-time apps", value="tornado"),
            questionary.Choice("Bottle - Simple Python web framework", value="bottle"),
            questionary.Choice("Pyramid - Flexible Python web framework", value="pyramid"),
            questionary.Choice("Sanic - Async Python web framework", value="sanic"),
            questionary.Choice("Quart - Async Python web framework (Flask-like)", value="quart"),
        ])
        
        # Node.js/JavaScript frameworks
        choices.extend([
            questionary.Choice("Express - Minimal Node.js web framework", value="express"),
            questionary.Choice("Koa - Next-generation Node.js web framework", value="koa"),
            questionary.Choice("Hapi - Rich Node.js web framework", value="hapi"),
            questionary.Choice("NestJS - Progressive Node.js framework (TypeScript)", value="nest"),
            questionary.Choice("Sails - MVC Node.js framework", value="sails"),
            questionary.Choice("LoopBack - API-first Node.js framework", value="loopback"),
            questionary.Choice("AdonisJS - Full-featured Node.js framework", value="adonis"),
            questionary.Choice("Feathers - Real-time Node.js framework", value="feathers"),
        ])
        
        # Go frameworks
        choices.extend([
            questionary.Choice("Gin - Fast Go web framework", value="gin"),
            questionary.Choice("Echo - High-performance Go web framework", value="echo"),
            questionary.Choice("Fiber - Express-inspired Go framework", value="fiber"),
            questionary.Choice("Chi - Lightweight Go HTTP router", value="chi"),
            questionary.Choice("Gorilla - Go web toolkit", value="gorilla"),
            questionary.Choice("Beego - Full-stack Go web framework", value="beego"),
            questionary.Choice("Iris - Fast Go web framework", value="iris"),
            questionary.Choice("Revel - Full-stack Go web framework", value="revel"),
        ])
        
        # Java frameworks
        choices.extend([
            questionary.Choice("Spring Framework - Enterprise Java framework", value="spring"),
            questionary.Choice("Spring Boot - Opinionated Spring framework", value="spring_boot"),
            questionary.Choice("Quarkus - Supersonic Java framework", value="quarkus"),
            questionary.Choice("Micronaut - Modern Java framework", value="micronaut"),
            questionary.Choice("Vert.x - Reactive Java toolkit", value="vertx"),
            questionary.Choice("Play Framework - Web framework for Java/Scala", value="play"),
            questionary.Choice("Dropwizard - Java framework for ops-friendly apps", value="dropwizard"),
            questionary.Choice("Spark - Micro Java web framework", value="spark"),
        ])
        
        # Rust frameworks
        choices.extend([
            questionary.Choice("Actix Web - Powerful Rust web framework", value="actix"),
            questionary.Choice("Warp - Rust web framework", value="warp"),
            questionary.Choice("Axum - Ergonomic Rust web framework", value="axum"),
            questionary.Choice("Rocket - Web framework for Rust", value="rocket"),
            questionary.Choice("Tide - Minimal Rust web framework", value="tide"),
            questionary.Choice("Poem - Full-featured Rust web framework", value="poem"),
            questionary.Choice("Salvo - Rust web framework", value="salvo"),
            questionary.Choice("Thruster - Fast Rust web framework", value="thruster"),
        ])
        
        # C#/.NET frameworks
        choices.extend([
            questionary.Choice("ASP.NET - Microsoft web framework", value="aspnet"),
            questionary.Choice("ASP.NET Core - Cross-platform .NET framework", value="aspnet_core"),
            questionary.Choice("Blazor - .NET web UI framework", value="blazor"),
            questionary.Choice("ServiceStack - .NET web services framework", value="service_stack"),
            questionary.Choice("Nancy - Lightweight .NET web framework", value="nancy"),
            questionary.Choice("Orleans - .NET distributed computing framework", value="orleans"),
        ])
        
        # PHP frameworks
        choices.extend([
            questionary.Choice("Laravel - Elegant PHP web framework", value="laravel"),
            questionary.Choice("Symfony - PHP web application framework", value="symfony"),
            questionary.Choice("CodeIgniter - Lightweight PHP framework", value="codeigniter"),
            questionary.Choice("CakePHP - Rapid PHP development framework", value="cakephp"),
            questionary.Choice("Phalcon - High-performance PHP framework", value="phalcon"),
            questionary.Choice("Slim - PHP micro framework", value="slim"),
        ])
        
        # Ruby frameworks
        choices.extend([
            questionary.Choice("Ruby on Rails - Full-stack Ruby web framework", value="rails"),
            questionary.Choice("Sinatra - Lightweight Ruby web framework", value="sinatra"),
            questionary.Choice("Hanami - Modern Ruby web framework", value="hanami"),
            questionary.Choice("Grape - RESTful API framework for Ruby", value="grape"),
            questionary.Choice("Padrino - Ruby web framework", value="padrino"),
            questionary.Choice("Cuba - Micro Ruby web framework", value="cuba"),
        ])
        
        # Other options
        choices.extend([
            questionary.Choice("Other - Custom or unlisted framework", value="other"),
            questionary.Choice("None - No backend framework", value="none"),
        ])

        # Find default choice
        default_idx = next((i for i, c in enumerate(choices) if c.value == default), 0)

        # Use questionary for arrow key navigation
        choice = questionary.select(
            "Choose backend framework:",
            choices=choices,
            default=choices[default_idx],
            style=self.QUESTIONARY_STYLE,
            qmark="→",
        ).ask()

        self.answers["backend_framework"] = choice

    def _ask_q5_frontend_framework(self) -> None:
        """Q5: Which frontend framework? (conditional on Q1)"""
        if "frontend_framework" in self.answers:
            return

        self.console.print("\n[bold]Question 5 of 18: Frontend Framework[/bold]")
        self.console.print("Which frontend framework are you using?")

        # Default to React for web apps
        project_type = self.answers.get("project_type", "web_app")
        default = "react" if "web" in project_type or "frontend" in project_type else "none"

        # Build choices with descriptions
        choices = []
        
        # React Ecosystem
        choices.extend([
            questionary.Choice("React - JavaScript library for building user interfaces", value="react"),
            questionary.Choice("Next.js - React framework for production", value="next"),
            questionary.Choice("Gatsby - React-based static site generator", value="gatsby"),
            questionary.Choice("Remix - Full-stack React web framework", value="remix"),
            questionary.Choice("React Native - React for mobile app development", value="react_native"),
            questionary.Choice("Expo - React Native development platform", value="expo"),
        ])
        
        # Vue Ecosystem
        choices.extend([
            questionary.Choice("Vue.js - Progressive JavaScript framework", value="vue"),
            questionary.Choice("Nuxt.js - Vue.js framework for production", value="nuxt"),
            questionary.Choice("Quasar - Vue.js framework for all platforms", value="quasar"),
            questionary.Choice("Vue Native - Vue.js for mobile development", value="vue_native"),
        ])
        
        # Angular Ecosystem
        choices.extend([
            questionary.Choice("Angular - Platform for building mobile and desktop apps", value="angular"),
            questionary.Choice("Ionic - Cross-platform mobile app development", value="ionic"),
            questionary.Choice("NativeScript - Cross-platform mobile development", value="nativescript"),
        ])
        
        # Svelte Ecosystem
        choices.extend([
            questionary.Choice("Svelte - Component framework with no virtual DOM", value="svelte"),
            questionary.Choice("SvelteKit - Svelte framework for building apps", value="sveltekit"),
            questionary.Choice("Sapper - Svelte web application framework", value="sapper"),
        ])
        
        # Other Modern Frameworks
        choices.extend([
            questionary.Choice("Solid - Reactive JavaScript library", value="solid"),
            questionary.Choice("Lit - Simple library for building fast web components", value="lit"),
            questionary.Choice("Alpine.js - Lightweight JavaScript framework", value="alpine"),
            questionary.Choice("Stimulus - Modest JavaScript framework", value="stimulus"),
            questionary.Choice("HTMX - HTML attributes for modern web interactions", value="htmx"),
            questionary.Choice("Astro - All-in-one web framework for content", value="astro"),
            questionary.Choice("Qwik - Resumable web framework", value="qwik"),
        ])
        
        # Build Tools & Meta-frameworks
        choices.extend([
            questionary.Choice("Vite - Next generation frontend tooling", value="vite"),
            questionary.Choice("Webpack - Module bundler for JavaScript", value="webpack"),
            questionary.Choice("Rollup - JavaScript module bundler", value="rollup"),
            questionary.Choice("Parcel - Zero configuration web application bundler", value="parcel"),
            questionary.Choice("esbuild - Extremely fast JavaScript bundler", value="esbuild"),
            questionary.Choice("SWC - Fast TypeScript/JavaScript compiler", value="swc"),
            questionary.Choice("Turbo - High-performance bundler", value="turbo"),
        ])
        
        # Static Site Generators
        choices.extend([
            questionary.Choice("Eleventy - Simpler static site generator", value="eleventy"),
            questionary.Choice("Hugo - Fast static site generator", value="hugo"),
            questionary.Choice("Jekyll - Static site generator", value="jekyll"),
            questionary.Choice("Gridsome - Vue.js static site generator", value="gridsome"),
            questionary.Choice("Docusaurus - Documentation site generator", value="docusaurus"),
        ])
        
        # Other options
        choices.extend([
            questionary.Choice("Other - Custom or unlisted framework", value="other"),
            questionary.Choice("None - No frontend framework", value="none"),
        ])

        # Find default choice
        default_idx = next((i for i, c in enumerate(choices) if c.value == default), 0)

        # Use questionary for arrow key navigation
        choice = questionary.select(
            "Choose frontend framework:",
            choices=choices,
            default=choices[default_idx],
            style=self.QUESTIONARY_STYLE,
            qmark="→",
        ).ask()

        self.answers["frontend_framework"] = choice

    def _ask_q6_database(self) -> None:
        """Q6: Which database? (conditional on Q1)"""
        if "database" in self.answers:
            return

        self.console.print("\n[bold]Question 6 of 18: Database[/bold]")
        self.console.print("Which database are you using?")

        # Smart default based on dev stage
        stage = self.answers.get("development_stage", "mvp")
        default = "sqlite" if stage in ["prototype", "mvp"] else "postgresql"

        # Build choices with descriptions
        choices = []
        
        # Relational Databases
        choices.extend([
            questionary.Choice("PostgreSQL - Advanced open-source relational database", value="postgresql"),
            questionary.Choice("MySQL - Popular open-source relational database", value="mysql"),
            questionary.Choice("MariaDB - MySQL-compatible database server", value="mariadb"),
            questionary.Choice("SQLite - Lightweight embedded database", value="sqlite"),
            questionary.Choice("Oracle - Enterprise relational database", value="oracle"),
            questionary.Choice("SQL Server - Microsoft relational database", value="sql_server"),
            questionary.Choice("DB2 - IBM relational database", value="db2"),
            questionary.Choice("CockroachDB - Distributed SQL database", value="cockroachdb"),
        ])
        
        # NoSQL Document Stores
        choices.extend([
            questionary.Choice("MongoDB - Document-oriented NoSQL database", value="mongodb"),
            questionary.Choice("CouchDB - Document-oriented NoSQL database", value="couchdb"),
            questionary.Choice("Couchbase - NoSQL document database", value="couchbase"),
            questionary.Choice("DynamoDB - AWS NoSQL document database", value="dynamodb"),
            questionary.Choice("Firestore - Google Cloud NoSQL document database", value="firestore"),
            questionary.Choice("Cosmos DB - Microsoft NoSQL document database", value="cosmosdb"),
        ])
        
        # NoSQL Key-Value Stores
        choices.extend([
            questionary.Choice("Redis - In-memory data structure store", value="redis"),
            questionary.Choice("Memcached - Distributed memory caching system", value="memcached"),
            questionary.Choice("Riak - Distributed NoSQL database", value="riak"),
            questionary.Choice("Hazelcast - In-memory data grid", value="hazelcast"),
            questionary.Choice("Aerospike - NoSQL database for real-time applications", value="aerospike"),
        ])
        
        # NoSQL Column Stores
        choices.extend([
            questionary.Choice("Cassandra - Distributed NoSQL database", value="cassandra"),
            questionary.Choice("HBase - Distributed column-oriented database", value="hbase"),
            questionary.Choice("ScyllaDB - High-performance NoSQL database", value="scylladb"),
            questionary.Choice("ClickHouse - Column-oriented database for analytics", value="clickhouse"),
        ])
        
        # NoSQL Graph Databases
        choices.extend([
            questionary.Choice("Neo4j - Graph database platform", value="neo4j"),
            questionary.Choice("ArangoDB - Multi-model NoSQL database", value="arangodb"),
            questionary.Choice("Amazon Neptune - Graph database service", value="amazon_neptune"),
            questionary.Choice("OrientDB - Multi-model NoSQL database", value="orientdb"),
        ])
        
        # Time Series Databases
        choices.extend([
            questionary.Choice("InfluxDB - Time series database", value="influxdb"),
            questionary.Choice("TimescaleDB - Time series database for PostgreSQL", value="timescaledb"),
            questionary.Choice("Prometheus - Monitoring and time series database", value="prometheus"),
            questionary.Choice("OpenTSDB - Time series database", value="opentsdb"),
            questionary.Choice("QuestDB - High-performance time series database", value="questdb"),
        ])
        
        # Search Engines
        choices.extend([
            questionary.Choice("Elasticsearch - Distributed search and analytics engine", value="elasticsearch"),
            questionary.Choice("Solr - Open-source search platform", value="solr"),
            questionary.Choice("OpenSearch - Open-source search and analytics suite", value="opensearch"),
            questionary.Choice("Meilisearch - Fast and relevant search engine", value="meilisearch"),
            questionary.Choice("Typesense - Fast typo-tolerant search engine", value="typesense"),
        ])
        
        # Cloud Database Services
        choices.extend([
            questionary.Choice("AWS RDS - Amazon Relational Database Service", value="aws_rds"),
            questionary.Choice("AWS Aurora - MySQL and PostgreSQL-compatible database", value="aws_aurora"),
            questionary.Choice("Google Cloud SQL - Managed relational database", value="google_cloud_sql"),
            questionary.Choice("Azure SQL - Microsoft cloud database service", value="azure_sql"),
            questionary.Choice("PlanetScale - Serverless MySQL platform", value="planetscale"),
            questionary.Choice("Supabase - Open-source Firebase alternative", value="supabase"),
        ])
        
        # Other options
        choices.extend([
            questionary.Choice("Other - Custom or unlisted database", value="other"),
            questionary.Choice("None - No database", value="none"),
        ])

        # Find default choice
        default_idx = next((i for i, c in enumerate(choices) if c.value == default), 0)

        # Use questionary for arrow key navigation
        choice = questionary.select(
            "Choose database:",
            choices=choices,
            default=choices[default_idx],
            style=self.QUESTIONARY_STYLE,
            qmark="→",
        ).ask()

        self.answers["database"] = choice

    def _ask_q7_test_coverage(self) -> None:
        """Q7: What is the minimum acceptable test coverage percentage?"""
        if "test_coverage_min" in self.answers:
            return

        self.console.print("\n[bold]Question 7 of 18: Test Coverage[/bold]")
        self.console.print("What is the minimum acceptable test coverage percentage?")

        # Smart default based on dev stage
        stage = self.answers["development_stage"]
        default = {
            "prototype": 60,
            "mvp": 80,
            "production": 90,
            "enterprise": 95
        }.get(stage, 80)

        coverage = IntPrompt.ask(
            f"Minimum coverage % (0-100)",
            default=default
        )

        # Validate range
        if not 0 <= coverage <= 100:
            self.console.print("[red]Coverage must be between 0 and 100[/red]")
            return self._ask_q7_test_coverage()

        self.answers["test_coverage_min"] = coverage

    def _ask_q8_code_review(self) -> None:
        """Q8: Is code review required before merging?"""
        if "code_review_required" in self.answers:
            return

        self.console.print("\n[bold]Question 8 of 18: Code Review[/bold]")
        self.console.print("Is code review required before merging?")

        # Default True for production/enterprise
        stage = self.answers["development_stage"]
        default = stage in ["production", "enterprise"]

        required = Confirm.ask(
            "Require code review?",
            default=default
        )
        self.answers["code_review_required"] = required

    def _ask_q9_time_boxing(self) -> None:
        """Q9: What is the maximum hours for IMPLEMENTATION tasks?"""
        if "time_boxing_hours" in self.answers:
            return

        self.console.print("\n[bold]Question 9 of 18: Time-Boxing[/bold]")
        self.console.print("What is the maximum hours for IMPLEMENTATION tasks?")

        # Smart default based on dev stage
        stage = self.answers["development_stage"]
        default = {
            "prototype": 8.0,
            "mvp": 6.0,
            "production": 4.0,
            "enterprise": 3.0
        }.get(stage, 4.0)

        hours = FloatPrompt.ask(
            f"Maximum hours",
            default=default
        )

        # Validate range
        if hours <= 0:
            self.console.print("[red]Hours must be positive[/red]")
            return self._ask_q9_time_boxing()

        self.answers["time_boxing_hours"] = hours

    def _ask_q10_development_approach(self) -> None:
        """Q10: What development approach do you follow?"""
        if "development_approach" in self.answers:
            return

        self.console.print("\n[bold]Question 10 of 18: Development Approach[/bold]")
        self.console.print("What development approach do you follow?")

        # Build choices with descriptions
        choices = []
        
        # Testing Approaches
        choices.extend([
            questionary.Choice("TDD - Test-Driven Development (write tests first)", value="tdd"),
            questionary.Choice("BDD - Behaviour-Driven Development (specify behaviour)", value="bdd"),
            questionary.Choice("ATDD - Acceptance Test-Driven Development", value="atdd"),
            questionary.Choice("MDD - Model-Driven Development", value="mdd"),
            questionary.Choice("SBE - Specification by Example", value="sbe"),
            questionary.Choice("Property-Based Testing - Generate test cases automatically", value="property_based_testing"),
        ])
        
        # Architecture Approaches
        choices.extend([
            questionary.Choice("DDD - Domain-Driven Design (focus on business domain)", value="ddd"),
            questionary.Choice("Hexagonal Architecture - Ports and adapters pattern", value="hexagonal"),
            questionary.Choice("Clean Architecture - Dependency inversion principle", value="clean_architecture"),
            questionary.Choice("Onion Architecture - Layered architecture with dependencies inward", value="onion"),
            questionary.Choice("Microservices - Distributed system architecture", value="microservices"),
            questionary.Choice("Serverless - Event-driven, function-based architecture", value="serverless"),
        ])
        
        # Process Methodologies
        choices.extend([
            questionary.Choice("Agile - Iterative development with customer collaboration", value="agile"),
            questionary.Choice("Scrum - Agile framework with sprints and roles", value="scrum"),
            questionary.Choice("Kanban - Visual workflow management", value="kanban"),
            questionary.Choice("XP - Extreme Programming (pair programming, TDD)", value="xp"),
            questionary.Choice("Crystal - Family of agile methodologies", value="crystal"),
            questionary.Choice("FDD - Feature-Driven Development", value="fdd"),
            questionary.Choice("DSDM - Dynamic Systems Development Method", value="dsdm"),
            questionary.Choice("SAFe - Scaled Agile Framework", value="safe"),
        ])
        
        # Traditional Approaches
        choices.extend([
            questionary.Choice("Waterfall - Sequential development phases", value="waterfall"),
            questionary.Choice("Spiral - Risk-driven development model", value="spiral"),
            questionary.Choice("V-Model - Verification and validation model", value="v_model"),
            questionary.Choice("Iterative - Incremental development cycles", value="iterative"),
            questionary.Choice("Prototype - Build and refine prototypes", value="prototype"),
        ])
        
        # Modern Practices
        choices.extend([
            questionary.Choice("DevOps - Development and operations collaboration", value="devops"),
            questionary.Choice("GitOps - Git-based operational workflows", value="gitops"),
            questionary.Choice("Shift Left - Early testing and quality practices", value="shift_left"),
            questionary.Choice("Continuous Delivery - Automated deployment pipeline", value="continuous_delivery"),
            questionary.Choice("Infrastructure as Code - Manage infrastructure with code", value="infrastructure_as_code"),
        ])
        
        # Quality Approaches
        choices.extend([
            questionary.Choice("Code Review - Peer review of code changes", value="code_review"),
            questionary.Choice("Pair Programming - Two developers working together", value="pair_programming"),
            questionary.Choice("Mob Programming - Team programming together", value="mob_programming"),
            questionary.Choice("Code Standards - Enforced coding conventions", value="code_standards"),
            questionary.Choice("Static Analysis - Automated code quality analysis", value="static_analysis"),
        ])
        
        # Other
        choices.extend([
            questionary.Choice("Other - Custom or unlisted approach", value="other"),
        ])

        # Find default choice
        default_idx = next((i for i, c in enumerate(choices) if c.value == "agile"), 0)

        # Use questionary for arrow key navigation
        choice = questionary.select(
            "Choose development approach:",
            choices=choices,
            default=choices[default_idx],
            style=self.QUESTIONARY_STYLE,
            qmark="→",
        ).ask()

        self.answers["development_approach"] = choice

    def _ask_q11_architecture_style(self) -> None:
        """Q11: What architecture style does the project follow? (WI-51: arrow navigation + descriptions)"""
        if "architecture_style" in self.answers:
            return

        self.console.print("\n[bold]Question 11 of 18: Architecture Style[/bold]")
        self.console.print("What architecture style does the project follow?")

        # Smart default based on project type and development stage
        project_type = self.answers["project_type"]
        dev_stage = self.answers["development_stage"]
        
        # Determine smart default
        if project_type == "api" and dev_stage in ["production", "enterprise"]:
            smart_default = "microservices"
        elif project_type == "web_app" and dev_stage in ["prototype", "mvp"]:
            smart_default = "monolith"
        elif dev_stage in ["production", "enterprise"]:
            smart_default = "modular_monolith"
        else:
            smart_default = "monolith"

        # Build choices with detailed descriptions
        choices = [
            # Core Patterns
            questionary.Choice(
                "Monolith - Single deployable where all features run together; simple to build/deploy but can be hard to scale organisationally",
                value="monolith"
            ),
            questionary.Choice(
                "Modular Monolith - One deployable split into well-defined internal modules; keeps shared deployment while enforcing boundaries",
                value="modular_monolith"
            ),
            questionary.Choice(
                "Layered (n-tier) - Stack of layers (UI, business, data, etc.) with one-way dependencies; easy to grasp but can grow rigid",
                value="layered_n_tier"
            ),
            questionary.Choice(
                "Hexagonal / Ports-and-Adapters - Core domain code isolated behind ports with adapters for I/O; boosts testability and swapability of tech",
                value="hexagonal_ports_adapters"
            ),
            questionary.Choice(
                "Clean / Onion - Concentric layers around the domain model; dependencies always point inward to protect business logic",
                value="clean_onion"
            ),
            questionary.Choice(
                "Microservices - Suite of small, independently deployable services; enables independent scaling and releases but adds operational overhead",
                value="microservices"
            ),
            questionary.Choice(
                "Service-Oriented Architecture (SOA) - Shared services expose standardised contracts; promotes reuse though governance can be heavy",
                value="service_oriented_soa"
            ),
            questionary.Choice(
                "Event-Driven - Components react to events asynchronously; great for decoupling and scalability but harder to reason about flow",
                value="event_driven"
            ),
            questionary.Choice(
                "Serverless / Function-as-a-Service - Workloads run as managed functions triggered by events; eliminates server ops yet limits control and state handling",
                value="serverless_faas"
            ),
            questionary.Choice(
                "Microkernel / Plug-in - Minimal core system with plug-in modules for features; simplifies extensibility at the cost of upfront design",
                value="microkernel_plugin"
            ),
            questionary.Choice(
                "Pipe-and-Filter - Data flows through chained processing steps; excels at stream processing and composability",
                value="pipe_and_filter"
            ),
            questionary.Choice(
                "Blackboard - Shared knowledge base refined by specialised components; suited for complex problem solving with incremental refinement",
                value="blackboard"
            ),
            questionary.Choice(
                "Client-Server - Clients request services from centralised servers; classic pattern still common for web/mobile apps",
                value="client_server"
            ),
            questionary.Choice(
                "Peer-to-Peer - Nodes act as both clients and servers; improves resilience but complicates coordination",
                value="peer_to_peer"
            ),
            questionary.Choice(
                "Component-Based - System assembled from reusable components with explicit contracts; encourages reuse and parallel development",
                value="component_based"
            ),
            questionary.Choice(
                "Space-Based (Grid Computing) - Shared in-memory data grid with distributed processing; addresses scalability spikes and latency",
                value="space_based_grid"
            ),
            questionary.Choice(
                "Cloud-Native / 12-Factor - Applications built for elastic cloud platforms using stateless services, automation, observability; maximises portability and scalability",
                value="cloud_native_12factor"
            ),
            
            # Hybrid Patterns
            questionary.Choice(
                "Modular Monolith + Hexagonal - Keep single deployable simplicity while ports/adapters enforce clean boundaries and make future service extraction painless",
                value="modular_monolith_hexagonal"
            ),
            questionary.Choice(
                "Layered + Clean/Onion - Layer structure guides teams; inward-facing dependency rules protect domain logic from UI/data churn",
                value="layered_clean_onion"
            ),
            questionary.Choice(
                "Microservices + Event-Driven - Autonomous services stay cohesive; async events handle cross-service workflows without tight coupling",
                value="microservices_event_driven"
            ),
            questionary.Choice(
                "Microkernel + Plug-in + Cloud-Native - Lightweight core hosts plug-ins; functions/containers deploy each plug-in independently for elastic scaling",
                value="microkernel_plugin_cloud_native"
            ),
            questionary.Choice(
                "Microservices + Serverless - Core services remain long-lived; bursty or peripheral capabilities run as functions to curb operational load",
                value="microservices_serverless"
            ),
            questionary.Choice(
                "Modular Monolith + CQRS/Event Sourcing - Single codebase yet read/write segregation and event history give scalability and auditability without distributed ops",
                value="modular_monolith_cqrs_event_sourcing"
            ),
            questionary.Choice(
                "Microservices + Space-Based Grid - Services keep ownership boundaries; shared in-memory data grid smooths spike handling and reduces cross-service latency",
                value="microservices_space_based_grid"
            ),
            questionary.Choice(
                "Component-Based + Layered - Reusable components organised by layers give both encapsulation and clear dependency rules, ideal for large teams",
                value="component_based_layered"
            ),
            
            # Other
            questionary.Choice("Other - Custom or specialised architecture pattern", value="other"),
        ]

        # Find default choice
        default_idx = next((i for i, c in enumerate(choices) if c.value == smart_default), 0)

        # Use questionary for arrow key navigation
        choice = questionary.select(
            "Choose architecture style:",
            choices=choices,
            default=choices[default_idx],
            style=self.QUESTIONARY_STYLE,
            qmark="→",
        ).ask()

        self.answers["architecture_style"] = choice

    def _ask_q12_deployment_strategy(self) -> None:
        """Q12: What deployment strategy do you use?"""
        if "deployment_strategy" in self.answers:
            return

        self.console.print("\n[bold]Question 12 of 18: Deployment Strategy[/bold]")
        self.console.print("What deployment strategy do you use?")

        # Smart default based on dev stage
        stage = self.answers["development_stage"]
        default = "ci_cd" if stage in ["production", "enterprise"] else "manual"

        choice = Prompt.ask(
            "Choose deployment strategy",
            choices=self.DEPLOYMENT_STRATEGIES,
            default=default
        )
        self.answers["deployment_strategy"] = choice

    def _ask_q13_team_size_detail(self) -> None:
        """Q13: WHO - Describe your team composition and roles."""
        if "team_size_detail" in self.answers:
            return

        self.console.print("\n[bold]Question 13 of 18: Team Composition (WHO)[/bold]")
        self.console.print("Describe your team composition and roles.")
        self.console.print("[dim]Example: '2 backend developers, 1 frontend developer, 1 QA'[/dim]")

        detail = Prompt.ask(
            "Team composition",
            default="Solo developer"
        )
        self.answers["team_size_detail"] = detail

    def _ask_q14_project_purpose(self) -> None:
        """Q14: WHAT - What is the core purpose of this project?"""
        if "project_purpose" in self.answers:
            return

        self.console.print("\n[bold]Question 14 of 18: Project Purpose (WHAT)[/bold]")
        self.console.print("What is the core purpose of this project?")
        self.console.print("[dim]Minimum 20 characters[/dim]")

        while True:
            purpose = Prompt.ask("Project purpose")
            if len(purpose) >= 20:
                self.answers["project_purpose"] = purpose
                break
            else:
                self.console.print("[red]Purpose must be at least 20 characters[/red]")

    def _ask_q15_target_users(self) -> None:
        """Q15: WHO (external) - Who are the target users?"""
        if "target_users" in self.answers:
            return

        self.console.print("\n[bold]Question 15 of 18: Target Users (WHO)[/bold]")
        self.console.print("Who are the target users of this project?")
        self.console.print("[dim]Example: 'Small business owners managing inventory'[/dim]")

        users = Prompt.ask(
            "Target users",
            default="General users"
        )
        self.answers["target_users"] = users

    def _ask_q16_timeline(self) -> None:
        """Q16: WHEN - What are the key milestones and deadlines?"""
        if "timeline" in self.answers:
            return

        self.console.print("\n[bold]Question 16 of 18: Timeline (WHEN)[/bold]")
        self.console.print("What are the key milestones and deadlines?")
        self.console.print("[dim]Example: 'MVP in 3 months, beta in 6 months'[/dim]")

        timeline = Prompt.ask(
            "Timeline",
            default="Flexible timeline"
        )
        self.answers["timeline"] = timeline

    def _ask_q17_constraints(self) -> None:
        """Q17: WHERE - What are the deployment and operational constraints?"""
        if "constraints" in self.answers:
            return

        self.console.print("\n[bold]Question 17 of 18: Constraints (WHERE)[/bold]")
        self.console.print("What are the deployment and operational constraints?")
        self.console.print("[dim]Example: 'AWS-only, GDPR compliance required'[/dim]")

        constraints = Prompt.ask(
            "Constraints",
            default="No specific constraints"
        )
        self.answers["constraints"] = constraints

    def _ask_q18_tech_rationale(self) -> None:
        """Q18: WHY - Why were these technical choices made?"""
        if "tech_rationale" in self.answers:
            return

        self.console.print("\n[bold]Question 18 of 18: Technical Rationale (WHY)[/bold]")
        self.console.print("Why were these technical choices made?")
        self.console.print("[dim]Example: 'Django for rapid development, PostgreSQL for reliability'[/dim]")

        rationale = Prompt.ask(
            "Technical rationale",
            default="Standard stack for project type"
        )
        self.answers["tech_rationale"] = rationale

    def _confirm_answers(self) -> bool:
        """Display answers summary and confirm with user.

        Returns:
            True if user confirms, False if user wants to restart
        """
        # Create summary table
        table = Table(
            title="Configuration Summary",
            show_header=True,
            header_style="bold cyan",
            box=box.ROUNDED
        )
        table.add_column("Question", style="cyan", width=30)
        table.add_column("Answer", style="yellow")

        # Technical configuration
        table.add_row("1. Project Type", self.answers["project_type"])
        table.add_row("2. Primary Language", self.answers["primary_language"])
        table.add_row("3. Development Stage", self.answers["development_stage"])

        if "backend_framework" in self.answers:
            table.add_row("4. Backend Framework", self.answers["backend_framework"])
        if "frontend_framework" in self.answers:
            table.add_row("5. Frontend Framework", self.answers["frontend_framework"])
        if "database" in self.answers:
            table.add_row("6. Database", self.answers["database"])

        table.add_row("7. Test Coverage Min", f"{self.answers['test_coverage_min']}%")
        table.add_row("8. Code Review Required", str(self.answers["code_review_required"]))
        table.add_row("9. Time-Boxing Hours", f"{self.answers['time_boxing_hours']}h")
        table.add_row("10. Development Approach", self.answers["development_approach"])
        table.add_row("11. Architecture Style", self.answers["architecture_style"])
        table.add_row("12. Deployment Strategy", self.answers["deployment_strategy"])

        # Context (6W)
        table.add_row("13. Team Composition", self.answers["team_size_detail"])
        table.add_row("14. Project Purpose", self.answers["project_purpose"][:50] + "...")
        table.add_row("15. Target Users", self.answers["target_users"])
        table.add_row("16. Timeline", self.answers["timeline"])
        table.add_row("17. Constraints", self.answers["constraints"])
        table.add_row("18. Tech Rationale", self.answers["tech_rationale"][:50] + "...")

        self.console.print("\n")
        self.console.print(table)
        self.console.print("\n")

        return Confirm.ask(
            "[bold]Are these answers correct?[/bold]",
            default=True
        )

    def _get_all_defaults(self) -> Dict[str, Any]:
        """Get default answers for all questions.

        Returns:
            Dictionary with default answers for all 18 questions
        """
        return {
            # Technical configuration
            "project_type": "web_app",
            "primary_language": "python",
            "development_stage": "mvp",
            "backend_framework": "django",
            "frontend_framework": "react",
            "database": "postgresql",
            "test_coverage_min": 80,
            "code_review_required": True,
            "time_boxing_hours": 4.0,
            "development_approach": "agile",
            "architecture_style": "modular_monolith",
            "deployment_strategy": "ci_cd",

            # Context (6W)
            "team_size_detail": "Solo developer",
            "project_purpose": "Build a production-ready web application with best practices",
            "target_users": "General users",
            "timeline": "Flexible timeline",
            "constraints": "No specific constraints",
            "tech_rationale": "Standard stack for project type with proven reliability"
        }
