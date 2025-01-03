import click
from . import DependencyFinder
import time
from typing import Dict, List, Union

def format_version_info(version_info: Dict) -> str:
    """Format version information with colors"""
    version = click.style(version_info["version"], fg="green", bold=True)
    python = click.style(version_info["python"], fg="blue")
    return f"{{ version = \"{version}\", python = \"{python}\" }}"

def print_package_info(package_name: str, result: Union[str, List[Dict], Dict]):
    """Print package information with colors"""
    package_name = click.style(package_name, fg="yellow", bold=True)
    
    if isinstance(result, list):
        click.echo(f"{package_name} = [")
        for version in result:
            click.echo(f"    {format_version_info(version)},")
        click.echo("]")
    elif isinstance(result, dict):
        click.echo(f"{package_name} = {format_version_info(result)}")
    else:
        click.echo(f"{package_name} = {click.style(result, fg='green', bold=True)}")

@click.command()
@click.argument('package_name')
@click.option('--python-version', '-p', default=">=3.11", help='Python version requirement (e.g. ">=3.11")')
def main(package_name: str, python_version: str):
    """Find the best version for your package"""
    finder = DependencyFinder()
    try:
        with click.progressbar(
            length=100,
            label=click.style('Fetching package info...', fg='cyan'),
            fill_char=click.style('█', fg='cyan'),
            empty_char='░'
        ) as bar:
            # Get package info
            versions, info = finder.get_package_info(package_name)
            bar.update(30)
            
            # Display package basic information
            click.echo()
            click.echo(click.style("📦 Package Info:", fg="cyan", bold=True))
            click.echo(f"  • Name: {click.style(info.get('name', package_name), fg='yellow')}")
            if info.get('summary'):
                click.echo(f"  • Description: {click.style(info.get('summary', ''), fg='white')}")
            if info.get('home_page'):
                click.echo(f"  • Homepage: {click.style(info.get('home_page', ''), fg='blue', underline=True)}")
            click.echo(f"  • Total Versions: {click.style(str(len(versions)), fg='green')}")
            click.echo()
            
            with click.progressbar(
                length=70,
                label=click.style('Analyzing version compatibility...', fg='cyan'),
                fill_char=click.style('█', fg='cyan'),
                empty_char='░'
            ) as bar2:
                result = finder.find_suitable_versions(package_name, python_version)
                bar2.update(70)
            
            click.echo()
            click.echo(click.style("🎯 Recommended Version(s):", fg="cyan", bold=True))
            print_package_info(package_name, result)
            
    finally:
        finder.close()

if __name__ == '__main__':
    main() 