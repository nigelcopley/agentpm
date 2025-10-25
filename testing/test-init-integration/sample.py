"""Sample Python project for testing"""
import click
from pathlib import Path

@click.command()
@click.option('--name', help='Name to greet')
def hello(name):
    """Sample CLI command"""
    print(f"Hello {name}!")

if __name__ == '__main__':
    hello()
