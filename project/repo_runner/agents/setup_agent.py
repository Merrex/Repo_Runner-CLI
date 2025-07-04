import subprocess
import json
import os
from pathlib import Path
from ..llm.llm_utils import generate_code_with_llm

class SetupAgent:
    def install(self, reqs):
        """Install dependencies and set up environment using LLM."""
        structure = reqs.get('structure', {})
        generated_files = reqs.get('generated_files', [])
        
        setup_results = {
            'installed_deps': [],
            'created_files': [],
            'errors': [],
            'warnings': []
        }
        
        # Create generated files
        for file_info in generated_files:
            try:
                file_path = Path(file_info['file'])
                file_path.write_text(file_info['content'])
                setup_results['created_files'].append(file_info['file'])
            except Exception as e:
                setup_results['errors'].append(f"Failed to create {file_info['file']}: {e}")
        
        # Install Python dependencies
        if 'requirements.txt' in [f['file'] for f in generated_files] or 'requirements.txt' in structure.get('files', {}):
            setup_results.update(self._install_python_deps())
        
        # Install Node.js dependencies
        if 'package.json' in [f['file'] for f in generated_files] or 'package.json' in structure.get('files', {}):
            setup_results.update(self._install_node_deps())
        
        # Setup environment variables
        env_setup = self._setup_environment(structure)
        setup_results.update(env_setup)
        
        return setup_results
    
    def _install_python_deps(self):
        """Install Python dependencies using LLM guidance."""
        try:
            # Use LLM to determine the best installation method
            prompt = """
            Analyze the current Python environment and suggest the best way to install dependencies:
            
            Options:
            1. pip install -r requirements.txt
            2. pip install --user -r requirements.txt
            3. python -m pip install -r requirements.txt
            4. Use virtual environment
            
            Consider:
            - System permissions
            - Virtual environment availability
            - Package conflicts
            - Best practices
            
            Return only the recommended command.
            """
            
            recommended_cmd = generate_code_with_llm(prompt, agent_name='setup_agent')
            
            # Execute the recommended command
            result = subprocess.run(
                recommended_cmd.split(),
                capture_output=True,
                text=True,
                cwd=os.getcwd()
            )
            
            if result.returncode == 0:
                return {
                    'installed_deps': ['python_dependencies'],
                    'python_install_method': recommended_cmd
                }
            else:
                return {
                    'errors': [f"Python install failed: {result.stderr}"],
                    'python_install_method': recommended_cmd
                }
                
        except Exception as e:
            return {'errors': [f"Python setup error: {e}"]}
    
    def _install_node_deps(self):
        """Install Node.js dependencies using LLM guidance."""
        try:
            # Use LLM to determine the best installation method
            prompt = """
            Analyze the current Node.js environment and suggest the best way to install dependencies:
            
            Options:
            1. npm install
            2. yarn install
            3. pnpm install
            4. npm ci (for production)
            
            Consider:
            - Available package managers
            - Lock file presence
            - Performance vs reliability
            - Best practices
            
            Return only the recommended command.
            """
            
            recommended_cmd = generate_code_with_llm(prompt, agent_name='setup_agent')
            
            # Execute the recommended command
            result = subprocess.run(
                recommended_cmd.split(),
                capture_output=True,
                text=True,
                cwd=os.getcwd()
            )
            
            if result.returncode == 0:
                return {
                    'installed_deps': ['node_dependencies'],
                    'node_install_method': recommended_cmd
                }
            else:
                return {
                    'errors': [f"Node.js install failed: {result.stderr}"],
                    'node_install_method': recommended_cmd
                }
                
        except Exception as e:
            return {'errors': [f"Node.js setup error: {e}"]}
    
    def _setup_environment(self, structure):
        """Setup environment variables using LLM."""
        try:
            # Use LLM to generate appropriate environment variables
            prompt = f"""
            Analyze this project and suggest environment variables:
            
            Project structure: {json.dumps(structure, indent=2)}
            
            Generate a .env file with:
            - Database connection strings
            - API keys (with placeholder values)
            - Development settings
            - Security configurations
            
            Return only the .env file content.
            """
            
            env_content = generate_code_with_llm(prompt, agent_name='setup_agent')
            
            # Create .env file
            env_path = Path('.env')
            if not env_path.exists():
                env_path.write_text(env_content)
                return {'created_files': ['.env']}
            else:
                return {'warnings': ['Environment file already exists']}
                
        except Exception as e:
            return {'errors': [f"Environment setup error: {e}"]} 