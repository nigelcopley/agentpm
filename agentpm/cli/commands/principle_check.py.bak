"""
Principle Check Command

CLI command for running principle-based agent analysis on code.
"""

import click
from pathlib import Path
from typing import Optional

from ...core.agents.principle_agents.registry import get_registry
from ...core.agents.principle_agents.r1_integration import get_r1_integration
from rich.console import Console


@click.command()
@click.argument('code_path', type=click.Path(exists=True, path_type=Path))
@click.option('--agent', '-a', 'agents', multiple=True, 
              help='Specific agents to run (solid, dry, kiss)')
@click.option('--format', 'output_format', type=click.Choice(['table', 'json', 'detailed']), 
              default='table', help='Output format')
@click.option('--severity', type=click.Choice(['LOW', 'MEDIUM', 'HIGH']), 
              default='MEDIUM', help='Minimum severity to report')
@click.option('--r1-gate', is_flag=True, help='Run in R1 gate mode')
@click.pass_context
def principle_check(ctx, code_path: Path, agents: tuple, output_format: str, 
                   severity: str, r1_gate: bool):
    """
    Run principle-based agent analysis on code.
    
    Analyzes code against software engineering principles (SOLID, DRY, KISS)
    and provides actionable recommendations for improvement.
    
    Examples:
    
    \b
    # Analyze current directory with all agents
    apm principle-check .
    
    \b
    # Run only SOLID agent analysis
    apm principle-check src/ --agent solid
    
    \b
    # Run in R1 gate mode for quality validation
    apm principle-check src/ --r1-gate
    
    \b
    # Get detailed JSON output
    apm principle-check src/ --format json
    """
    console = ctx.obj['console']
    
    try:
        if r1_gate:
            # Run in R1 gate mode
            integration = get_r1_integration()
            integration.configure_agents(list(agents) if agents else ['solid', 'dry', 'kiss'], severity)
            
            result = integration.analyze_for_r1_gate(str(code_path))
            
            if output_format == 'json':
                console.print_json(data=result)
            else:
                _display_r1_results(console, result)
        else:
            # Run individual agent analysis
            registry = get_registry()
            
            if agents:
                agent_names = list(agents)
            else:
                agent_names = ['solid', 'dry', 'kiss']  # Default MVP agents
            
            # Validate agent names
            available_agents = registry.get_agent_names()
            invalid_agents = [name for name in agent_names if name not in available_agents]
            if invalid_agents:
                console.print(f"[red]Error:[/red] Unknown agents: {', '.join(invalid_agents)}")
                console.print(f"Available agents: {', '.join(available_agents)}")
                return
            
            # Run analysis
            reports = registry.analyze_with_selected_agents(agent_names, str(code_path))
            
            if output_format == 'json':
                _display_json_results(console, reports)
            elif output_format == 'detailed':
                _display_detailed_results(console, reports)
            else:
                _display_table_results(console, reports, severity)
                
    except Exception as e:
        console.print(f"[red]Error running principle analysis:[/red] {e}")
        raise click.Abort()


def _display_r1_results(console, result):
    """Display R1 gate results"""
    console.print(f"\n[bold blue]R1 Principle Agent Gate Results[/bold blue]")
    console.print(f"Status: [{'green' if result['passed'] else 'red'}]{result['status']}[/]")
    console.print(f"Summary: {result['summary']}")
    
    if result['violations']:
        console.print(f"\n[bold red]Violations Found ({len(result['violations'])}):[/bold red]")
        for violation in result['violations']:
            severity_color = {
                'HIGH': 'red',
                'MEDIUM': 'yellow', 
                'LOW': 'blue'
            }.get(violation['severity'], 'white')
            
            console.print(f"  [{severity_color}]{violation['severity']}[/] {violation['location']}")
            console.print(f"    {violation['issue']}")
            console.print(f"    [dim]Recommendation: {violation['recommendation']}[/dim]")
    
    # Display principle scores
    console.print(f"\n[bold blue]Principle Scores:[/bold blue]")
    for agent, score in result['principle_scores'].items():
        score_color = 'green' if score >= 80 else 'yellow' if score >= 60 else 'red'
        console.print(f"  {agent.upper()}: [{score_color}]{score}/100[/]")
    
    # Display metrics
    metrics = result['metrics']
    console.print(f"\n[bold blue]Analysis Metrics:[/bold blue]")
    console.print(f"  Files analyzed: {metrics['files_analyzed']}")
    console.print(f"  Agents run: {metrics['agents_run']}")
    console.print(f"  Analysis time: {metrics['average_analysis_time']:.1f}ms")


def _display_table_results(console, reports, severity):
    """Display results in table format"""
    from rich.table import Table
    
    console.print(f"\n[bold blue]Principle Agent Analysis Results[/bold blue]")
    
    # Summary table
    summary_table = Table(title="Summary")
    summary_table.add_column("Agent", style="cyan")
    summary_table.add_column("Principle", style="magenta")
    summary_table.add_column("Status", style="green")
    summary_table.add_column("Violations", style="red")
    summary_table.add_column("Files", style="blue")
    summary_table.add_column("Time (ms)", style="yellow")
    
    for agent_name, report in reports.items():
        violation_count = len([v for v in report.violations 
                              if v.severity.value in ['HIGH', 'MEDIUM']])
        
        status = "✅ PASS" if report.passed else "❌ FAIL"
        status_style = "green" if report.passed else "red"
        
        summary_table.add_row(
            agent_name.upper(),
            report.principle,
            f"[{status_style}]{status}[/]",
            str(violation_count),
            str(report.files_analyzed),
            f"{report.analysis_time_ms:.1f}"
        )
    
    console.print(summary_table)
    
    # Violations table
    all_violations = []
    for report in reports.values():
        all_violations.extend([v for v in report.violations 
                              if v.severity.value in ['HIGH', 'MEDIUM']])
    
    if all_violations:
        violations_table = Table(title="Violations")
        violations_table.add_column("Agent", style="cyan")
        violations_table.add_column("Severity", style="red")
        violations_table.add_column("Location", style="blue")
        violations_table.add_column("Issue", style="white")
        
        for violation in all_violations:
            severity_color = {
                'HIGH': 'red',
                'MEDIUM': 'yellow',
                'LOW': 'blue'
            }.get(violation.severity.value, 'white')
            
            violations_table.add_row(
                violation.principle,
                f"[{severity_color}]{violation.severity.value}[/]",
                violation.location,
                violation.issue[:80] + "..." if len(violation.issue) > 80 else violation.issue
            )
        
        console.print(violations_table)


def _display_detailed_results(console, reports):
    """Display detailed results"""
    for agent_name, report in reports.items():
        console.print(f"\n[bold blue]{agent_name.upper()} Agent Results[/bold blue]")
        console.print(f"Principle: {report.principle}")
        console.print(f"Status: [{'green' if report.passed else 'red'}]{'PASS' if report.passed else 'FAIL'}[/]")
        console.print(f"Files analyzed: {report.files_analyzed}")
        console.print(f"Analysis time: {report.analysis_time_ms:.1f}ms")
        console.print(f"Summary: {report.summary}")
        
        if report.violations:
            console.print(f"\n[bold red]Violations ({len(report.violations)}):[/bold red]")
            for violation in report.violations:
                severity_color = {
                    'HIGH': 'red',
                    'MEDIUM': 'yellow',
                    'LOW': 'blue'
                }.get(violation.severity.value, 'white')
                
                console.print(f"  [{severity_color}]{violation.severity.value}[/] {violation.location}")
                console.print(f"    Issue: {violation.issue}")
                console.print(f"    Recommendation: {violation.recommendation}")
                if violation.rule_id:
                    console.print(f"    Rule: {violation.rule_id}")


def _display_json_results(console, reports):
    """Display results in JSON format"""
    json_data = {}
    for agent_name, report in reports.items():
        json_data[agent_name] = {
            'principle': report.principle,
            'passed': report.passed,
            'violations': [
                {
                    'severity': v.severity.value,
                    'location': v.location,
                    'issue': v.issue,
                    'recommendation': v.recommendation,
                    'rule_id': v.rule_id
                }
                for v in report.violations
            ],
            'metrics': report.metrics,
            'summary': report.summary,
            'analysis_time_ms': report.analysis_time_ms,
            'files_analyzed': report.files_analyzed
        }
    
    console.print_json(data=json_data)
