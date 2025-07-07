#!/usr/bin/env python3
"""
CLI interface for repo_runner.
"""

import click
import os
import sys
from pathlib import Path

# Auto-install missing dependencies
def ensure_dependencies():
    """Ensure all required dependencies are installed."""
    missing_deps = []
    
    # Check for python-dotenv
    try:
        import dotenv
    except ImportError:
        missing_deps.append('python-dotenv')
    
    # Check for transformers
    try:
        import transformers
    except ImportError:
        missing_deps.append('transformers')
    
    # Check for torch
    try:
        import torch
    except ImportError:
        missing_deps.append('torch')
    
    # Install missing dependencies
    if missing_deps:
        print(f"🔧 Installing missing dependencies: {', '.join(missing_deps)}")
        try:
            import subprocess
            subprocess.check_call([sys.executable, '-m', 'pip', 'install'] + missing_deps)
            print("✅ Dependencies installed successfully")
        except Exception as e:
            print(f"⚠️ Failed to install some dependencies: {e}")
            print("The system will continue with fallback functionality")

# Run dependency check
ensure_dependencies()

from .core import RepoRunner
from .config import Config
from .logger import setup_logger
from .agents.orchestrator import Orchestrator
from .config_manager import config_manager


@click.group()
@click.version_option(version='1.0.0')
@click.option('--config', '-c', type=click.Path(exists=True), 
              help='Path to configuration file')
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose logging')
@click.option('--dry-run', is_flag=True, help='Show what would be done without executing')
@click.pass_context
def cli(ctx, config, verbose, dry_run):
    """repo_runner - Universal Repository Analysis and Execution Tool"""
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
@click.option('--mode', default='local', help='Execution mode (local/cloud)')
@click.option('--timeout', default=300, help='Timeout in seconds')
def run(repo_path: str, mode: str, timeout: int):
    """Run repo_runner on a repository."""
    from .agents.orchestrator import Orchestrator
    
    print(f"🚀 Starting repo_runner in {mode} mode...")
    print(f"📂 Target repository: {repo_path}")
    print("⏱️ This may take a few minutes for complex repositories...")
    
    orchestrator = Orchestrator(timeout=timeout)
    result = orchestrator.run(repo_path, mode=mode)
    
    if result['status'] == 'success':
        print("✅ repo_runner completed successfully!")
    else:
        print(f"❌ repo_runner failed: {result.get('error', 'Unknown error')}")
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
    """Install dependencies and setup environment."""
    print("🔧 Installing repo_runner dependencies...")
    
    try:
        import subprocess
        
        # Install required packages
        packages = [
            'transformers',
            'torch',
            'requests',
            'psutil',
            'python-dotenv',
            'pyngrok'
        ]
        
        for package in packages:
            print(f"📦 Installing {package}...")
            subprocess.run([sys.executable, '-m', 'pip', 'install', package], check=True)
        
        print("✅ Dependencies installed successfully!")
        
    except Exception as e:
        print(f"❌ Installation failed: {e}")
        sys.exit(1)


@cli.command()
def config():
    """Setup and manage configuration."""
    print("🔧 Configuration Management")
    print("=" * 50)
    
    # Create template
    config_manager.create_env_template()
    print("✅ Created configuration template: .env.template")
    print("📝 Edit this file with your actual tokens and settings")
    
    # Print summary
    config_manager.print_config_summary()


@cli.command()
def debug():
    """Debug configuration and tokens."""
    config_manager.debug_tokens()


@cli.command()
def models():
    """List available models and setup universal authentication."""
    from .llm.llm_utils import list_available_models, setup_model_authentication
    
    print("🤖 Universal Model Configuration")
    print("=" * 50)
    
    # List available models
    list_available_models()
    
    print("\n" + "=" * 50)
    
    # Setup universal authentication
    setup_model_authentication()
    
    print("\n💡 Quick Start:")
    print("1. Run: repo_runner install")
    print("2. Run: repo_runner run /path/to/repo")
    print("3. Models will be configured automatically!")


@cli.command()
def test_models():
    """Test model availability and configuration."""
    print("🧪 Testing Model Configuration")
    print("=" * 50)
    
    from .llm.llm_utils import get_model_config, get_llm_pipeline
    
    agents = ['detection_agent', 'requirements_agent', 'setup_agent', 
              'fixer_agent', 'db_agent', 'health_agent', 'runner_agent']
    
    for agent in agents:
        try:
            config = get_model_config(agent)
            print(f"\n🔍 Testing {agent}:")
            print(f"   Model: {config['model_name']}")
            print(f"   Type: {config.get('type', 'unknown')}")
            print(f"   Max Tokens: {config['max_tokens']}")
            
            # Try to get pipeline
            pipeline = get_llm_pipeline(agent)
            print(f"   Status: ✅ Available")
            
        except Exception as e:
            print(f"   Status: ❌ Failed - {e}")
    
    print("\n✅ Model testing completed!")


@cli.command()
def status():
    """Show current configuration status."""
    print("📊 Configuration Status")
    print("=" * 50)
    
    # Print configuration summary
    config_manager.print_config_summary()
    
    # Check for .env file
    env_file = Path('.env')
    if env_file.exists():
        print(f"\n✅ Configuration file found: {env_file}")
    else:
        print(f"\n⚠️ No .env file found")
        print("💡 Run 'repo_runner config' to create one")


if __name__ == '__main__':
    cli()