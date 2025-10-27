#!/usr/bin/env python3
"""
Basic test script for ClaudeCodeGenerator

Tests the generator with database agents to verify:
1. Template loading works
2. Agent files are generated
3. CLAUDE.md is generated
4. Hooks are generated
5. Settings.json is generated
"""

from pathlib import Path
from agentpm.core.database.service import DatabaseService
from agentpm.core.database.methods import agents as agent_methods
from agentpm.core.database.methods import rules as rule_methods
from agentpm.core.database.methods import projects as project_methods
from agentpm.providers.anthropic.claude_code.generator import ClaudeCodeGenerator

def main():
    # Setup
    project_root = Path(__file__).parent
    db_path = project_root / ".aipm" / "data" / "aipm.db"

    print(f"🔍 Testing ClaudeCodeGenerator")
    print(f"📁 Project root: {project_root}")
    print(f"💾 Database: {db_path}")
    print()

    # Initialize database
    db = DatabaseService(str(db_path))

    # Get data from database
    print("📊 Loading data from database...")
    agents = agent_methods.list_agents(db)
    rules = rule_methods.list_rules(db)
    projects = project_methods.list_projects(db)

    if not projects:
        print("❌ No projects found in database")
        return 1

    project = projects[0]

    print(f"✅ Loaded {len(agents)} agents")
    print(f"✅ Loaded {len(rules)} rules")
    print(f"✅ Project: {project.name}")
    print()

    # Initialize generator
    print("🏗️ Initializing ClaudeCodeGenerator...")
    try:
        generator = ClaudeCodeGenerator(db)
        print(f"✅ Generator initialized")
        print(f"   Provider: {generator.provider_name}")
        print(f"   Config dir: {generator.config_directory}")
        print()
    except Exception as e:
        print(f"❌ Generator initialization failed: {e}")
        return 1

    # Generate configuration
    print("⚙️ Generating configuration files...")
    output_dir = project_root / "test_output"
    output_dir.mkdir(exist_ok=True)

    try:
        result = generator.generate_from_agents(
            agents=agents,
            rules=rules,
            project=project,
            output_dir=output_dir,
            include_hooks=True,
            include_settings=True
        )

        print(f"✅ Generation complete")
        print(f"   Success: {result.success}")
        print(f"   Files generated: {len(result.files)}")
        print(f"   Errors: {len(result.errors)}")
        print()

        if result.errors:
            print("⚠️ Errors encountered:")
            for error in result.errors:
                print(f"   - {error}")
            print()

        # Display statistics
        print("📈 Statistics:")
        for key, value in result.statistics.items():
            print(f"   {key}: {value}")
        print()

        # List generated files
        print("📄 Generated files:")
        for file_output in result.files:
            relative_path = file_output.path.relative_to(output_dir)
            print(f"   - {relative_path}")
            print(f"     Size: {file_output.size_bytes} bytes")
            print(f"     Hash: {file_output.content_hash[:16]}...")
        print()

        # Validate configuration
        print("✔️ Validating configuration...")
        config_dir = output_dir / generator.config_directory
        validation_errors = generator.validate_config(config_dir)

        if validation_errors:
            print("⚠️ Validation errors:")
            for error in validation_errors:
                print(f"   - {error}")
        else:
            print("✅ Configuration is valid")
        print()

        return 0 if result.success and not validation_errors else 1

    except Exception as e:
        print(f"❌ Generation failed: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    exit(main())
