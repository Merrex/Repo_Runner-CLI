import json
from pathlib import Path
from ..llm.llm_utils import generate_code_with_llm
from .base_agent import BaseAgent

class RequirementsAgent(BaseAgent):
    def ensure_requirements(self, structure):
        """Ensure requirements/config files exist and are correct using LLM."""
        files = structure.get('files', {})
        missing_files = structure.get('missing_files', [])
        
        generated_files = []
        updated_files = []
        
        # Check for Python requirements
        if 'requirements.txt' in missing_files:
            requirements_content = self._generate_requirements_txt(structure)
            generated_files.append({
                'file': 'requirements.txt',
                'content': requirements_content,
                'type': 'generated'
            })
        
        # Check for package.json (Node.js)
        if 'package.json' in missing_files:
            package_json = self._generate_package_json(structure)
            generated_files.append({
                'file': 'package.json',
                'content': package_json,
                'type': 'generated'
            })
        
        # Check for Dockerfile
        if 'Dockerfile' in missing_files:
            dockerfile = self._generate_dockerfile(structure)
            generated_files.append({
                'file': 'Dockerfile',
                'content': dockerfile,
                'type': 'generated'
            })
        
        # Analyze existing requirements files
        for filename in ['requirements.txt', 'package.json', 'pyproject.toml']:
            if filename in files:
                analysis = self._analyze_existing_file(filename, structure)
                updated_files.append(analysis)
        
        return {
            "status": "requirements_analyzed",
            "generated_files": generated_files,
            "updated_files": updated_files,
            "missing_files": missing_files
        }
    
    def _generate_requirements_txt(self, structure):
        """Generate requirements.txt using LLM."""
        prompt = f"""
        Generate a requirements.txt file for this project:
        
        Project structure: {json.dumps(structure, indent=2)}
        
        Include only the essential dependencies needed to run this project.
        Use specific version numbers where appropriate.
        Format as a standard requirements.txt file.
        """
        
        return generate_code_with_llm(prompt, agent_name='requirements_agent')
    
    def _generate_package_json(self, structure):
        """Generate package.json using LLM."""
        prompt = f"""
        Generate a package.json file for this project:
        
        Project structure: {json.dumps(structure, indent=2)}
        
        Include:
        - Project name and description
        - Essential dependencies
        - Scripts for running the project
        - Proper JSON format
        
        Return only the JSON content.
        """
        
        return generate_code_with_llm(prompt, agent_name='requirements_agent')
    
    def _generate_dockerfile(self, structure):
        """Generate Dockerfile using LLM."""
        prompt = f"""
        Generate a Dockerfile for this project:
        
        Project structure: {json.dumps(structure, indent=2)}
        
        Create a production-ready Dockerfile that:
        - Uses appropriate base image
        - Installs dependencies
        - Sets up the application
        - Exposes necessary ports
        - Follows Docker best practices
        
        Return only the Dockerfile content.
        """
        
        return generate_code_with_llm(prompt, agent_name='requirements_agent')
    
    def _analyze_existing_file(self, filename, structure):
        """Analyze existing requirements file using LLM."""
        prompt = f"""
        Analyze this {filename} file and suggest improvements:
        
        Project structure: {json.dumps(structure, indent=2)}
        
        Provide:
        1. Missing dependencies
        2. Outdated versions
        3. Security issues
        4. Optimization suggestions
        
        Format as JSON with keys: missing, outdated, security, optimizations
        """
        
        analysis = generate_code_with_llm(prompt, agent_name='requirements_agent')
        
        return {
            'file': filename,
            'analysis': analysis,
            'type': 'analyzed'
        } 