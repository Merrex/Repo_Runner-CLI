#!/usr/bin/env python3
"""
CLI interface for repo_runner.
"""

import click
import os
import sys
from pathlib import Path
from .core import RepoRunner
from .config import Config
from .logger import setup_logger
from .agents.orchestrator import Orchestrator


@click.group()
@click.version_option()
@click.option('--config', '-c', type=click.Path(exists=True), 
              help='Path to configuration file')
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose logging')
@click.option('--dry-run', is_flag=True, help='Show what would be done without executing')
@click.pass_context
def cli(ctx, config, verbose, dry_run):
    """repo_runner - Automatically detect, configure, and run code repositories."""
    ctx.ensure_object(dict)
    ctx.obj['config'] = Config.load(config) if config else Config()
    ctx.obj['verbose'] = verbose
    ctx.obj['dry_run'] = dry_run
    
    # Setup logging
    setup_logger(verbose=verbose)


@cli.command()
@click.argument('path', type=click.Path(exists=True), default='.')
@click.option('--output', '-o', type=click.Choice(['json', 'yaml', 'text']), 
              default='text', help='Output format')
@click.pass_context
def detect(ctx, path, output):
    """Detect project structure and technologies."""
    runner = RepoRunner(path, ctx.obj['config'])
    result = runner.detect_structure()
    
    if output == 'json':
        import json
        click.echo(json.dumps(result, indent=2))
    elif output == 'yaml':
        import yaml
        click.echo(yaml.dump(result, default_flow_style=False))
    else:
        runner.print_detection_summary(result)


@cli.command()
@click.argument('path', type=click.Path(exists=True), default='.')
@click.option('--skip-deps', is_flag=True, help='Skip dependency installation')
@click.option('--skip-env', is_flag=True, help='Skip environment setup')
@click.option('--skip-db', is_flag=True, help='Skip database setup')
@click.pass_context
def setup(ctx, path, skip_deps, skip_env, skip_db):
    """Setup project dependencies and environment."""
    runner = RepoRunner(path, ctx.obj['config'], dry_run=ctx.obj['dry_run'])
    
    try:
        if not skip_deps:
            runner.install_dependencies()
        if not skip_env:
            runner.setup_environment()
        if not skip_db:
            runner.setup_database()
        click.echo("✅ Setup completed successfully!")
    except Exception as e:
        click.echo(f"❌ Setup failed: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.argument('repo_path', type=click.Path(exists=True))
@click.option('--mode', default='local', help='Run mode: local or cloud')
@click.option('--timeout', default=300, help='Timeout in seconds (default: 300)')
def run(repo_path, mode, timeout):
    """Run the agentic repo runner on the given repository."""
    try:
        result = Orchestrator(timeout=timeout).run(repo_path, mode)
        click.echo(f"\nFinal result: {result}")
    except TimeoutError as e:
        click.echo(f"❌ {e}", err=True)
        sys.exit(1)
    except KeyboardInterrupt:
        click.echo("\n🛑 Operation interrupted by user")
        sys.exit(1)
    except Exception as e:
        click.echo(f"❌ Operation failed: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.argument('path', type=click.Path(exists=True), default='.')
@click.pass_context
def full(ctx, path):
    """Run complete workflow: detect, setup, and run."""
    runner = RepoRunner(path, ctx.obj['config'], dry_run=ctx.obj['dry_run'])
    
    try:
        click.echo("🔍 Detecting project structure...")
        structure = runner.detect_structure()
        runner.print_detection_summary(structure)
        
        click.echo("\n📦 Installing dependencies...")
        runner.install_dependencies()
        
        click.echo("\n🔧 Setting up environment...")
        runner.setup_environment()
        
        click.echo("\n🗄️  Setting up database...")
        runner.setup_database()
        
        click.echo("\n🚀 Starting application...")
        runner.run_application()
        runner.perform_health_check()
        runner.show_service_urls()
        
    except KeyboardInterrupt:
        click.echo("\n🛑 Workflow stopped by user")
    except Exception as e:
        click.echo(f"❌ Workflow failed: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.argument('path', type=click.Path(exists=True), default='.')
@click.pass_context
def docs(ctx, path):
    """Update project documentation."""
    runner = RepoRunner(path, ctx.obj['config'], dry_run=ctx.obj['dry_run'])
    
    try:
        runner.update_documentation()
        click.echo("📚 Documentation updated successfully!")
    except Exception as e:
        click.echo(f"❌ Documentation update failed: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.argument('path', type=click.Path(exists=True), default='.')
@click.pass_context
def health(ctx, path):
    """Check application health."""
    runner = RepoRunner(path, ctx.obj['config'])
    
    try:
        status = runner.perform_health_check()
        if status:
            click.echo("✅ Application is healthy!")
            runner.show_service_urls()
        else:
            click.echo("❌ Application health check failed!")
            sys.exit(1)
    except Exception as e:
        click.echo(f"❌ Health check failed: {e}", err=True)
        sys.exit(1)


@cli.command()
def install():
    """Auto-install system dependencies and verify installation."""
    from .installer import auto_install
    success = auto_install()
    if not success:
        sys.exit(1)


@cli.command()
def models():
    """List available models and setup token configuration."""
    from .llm.llm_utils import list_available_models, setup_huggingface_token
    
    print("🤖 Repo Runner Model Configuration")
    print("=" * 50)
    
    # List available models
    list_available_models()
    
    print("\n" + "=" * 50)
    
    # Setup token configuration
    setup_huggingface_token()
    
    print("\n💡 Quick Start:")
    print("1. Run: repo_runner install")
    print("2. Run: repo_runner run /path/to/repo")
    print("3. Models will be downloaded automatically!")


@cli.command()
def test_models():
    """Test all models to ensure they work correctly."""
    from .test_models import test_model_loading, print_summary
    
    print("🧪 Testing All Models")
    print("This will test that each agent's model loads and generates responses.")
    print("This may take a few minutes for the first run as models are downloaded.")
    
    results = test_model_loading()
    print_summary(results)


if __name__ == '__main__':
    cli()