import click
from . import DependencyFinder

@click.command()
@click.argument('package_name')
@click.option('--python-version', '-p', default=">=3.11", help='Python version requirement (e.g. ">=3.11")')
def main(package_name: str, python_version: str):
    """查找包的最佳版本"""
    finder = DependencyFinder()
    try:
        result = finder.find_suitable_versions(package_name, python_version)
        if isinstance(result, list):
            click.echo(f"{package_name} = [")
            for version in result:
                click.echo(f"    {{ version = \"{version['version']}\", python = \"{version['python']}\" }},")
            click.echo("]")
        elif isinstance(result, dict):
            click.echo(f"{package_name} = {{ version = \"{result['version']}\", python = \"{result['python']}\" }}")
        else:
            click.echo(f"{package_name} = \"{result}\"")
    finally:
        finder.close()

if __name__ == '__main__':
    main() 