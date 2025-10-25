"""Sample Python CLI project"""
import click
from pathlib import Path

@click.command()
@click.option('--name', default='World', help='Name to greet')
@click.option('--count', default=1, help='Number of greetings')
def hello(name, count):
    """Simple CLI that greets NAME COUNT times."""
    for _ in range(count):
        click.echo(f'Hello {name}!')

if __name__ == '__main__':
    hello()
