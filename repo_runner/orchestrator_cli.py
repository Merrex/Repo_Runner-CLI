import click
import json
from repo_runner.managers.orchestrator import OrchestratorAgent

@click.command()
@click.option('--repo_path', required=True, type=click.Path(exists=True), help='Path to the target repo')
@click.option('--env', default='detect', help='Target environment (detect/aws/gcp/colab/local)')
@click.option('--model_quality', default='balanced', help='Model quality (balanced/premium/free)')
@click.option('--config', type=click.Path(exists=True), help='Optional config.yaml')
@click.option('--dry_run', is_flag=True, help='Dry run mode')
def run_orchestrator(repo_path, env, model_quality, config, dry_run):
    config_data = {}
    if config:
        import yaml
        with open(config) as f:
            config_data = yaml.safe_load(f)
    agent = OrchestratorAgent(repo_path, env=env, config=config_data)
    result = agent.run()
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    run_orchestrator() 