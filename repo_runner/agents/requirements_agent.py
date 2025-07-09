import json
from pathlib import Path
from ..llm.llm_utils import generate_code_with_llm
from .base_agent import BaseAgent
import os

class RequirementsAgent(BaseAgent):
    def run(self, *args, **kwargs):
        """Analyze project requirements and dependencies"""
        detection_result = kwargs.get('detection_result', {})
        
        try:
            # Use the existing requirements logic
            requirements_result = self.ensure_requirements(detection_result)
            
            result = {
                "status": "ok",
                "agent": self.agent_name,
                "requirements": requirements_result,
                "missing_files": requirements_result.get('missing_files', []),
                "generated_files": requirements_result.get('generated_files', [])
            }
            
            # Save checkpoint
            self.checkpoint(result)
            return result
            
        except Exception as e:
            error_result = {
                "status": "error",
                "agent": self.agent_name,
                "error": str(e)
            }
            self.report_error(e)
            return error_result

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

    def checkpoint(self, state: dict, checkpoint_file: str = "requirements_agent_state.json"):
        """
        Save the RequirementsAgent's state to a checkpoint file (default: requirements_agent_state.json).
        Logs the checkpoint event.
        """
        import json
        self.log(f"Checkpointing RequirementsAgent state to {checkpoint_file}", "info")
        try:
            with open(checkpoint_file, "w") as f:
                json.dump(state, f, indent=2)
            self.log(f"Checkpoint saved to {checkpoint_file}", "info")
        except Exception as e:
            self.log(f"Failed to save checkpoint: {e}", "error")

    def report_error(self, error, context=None, error_file="requirements_agent_errors.json"):
        """
        Log the error and optionally save it to a file for traceability.
        """
        import json
        self.log(f"Error reported: {error} | Context: {context}", "error")
        try:
            error_record = {"error": str(error), "context": context}
            if not os.path.exists(error_file):
                with open(error_file, "w") as f:
                    json.dump([error_record], f, indent=2)
            else:
                with open(error_file, "r+") as f:
                    errors = json.load(f)
                    errors.append(error_record)
                    f.seek(0)
                    json.dump(errors, f, indent=2)
        except Exception as e:
            self.log(f"Failed to save error report: {e}", "error") 