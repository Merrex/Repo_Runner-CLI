import subprocess
import json
import os
from pathlib import Path
from ..llm.llm_utils import generate_code_with_llm
from .base_agent import BaseAgent

class SetupAgent(BaseAgent):
    def setup_project(self, repo_path: str):
        """Main setup method called by orchestrator - automatically detects repo root and sets up the project."""
        print(f"🔧 Setting up project at: {repo_path}")
        
        # Automatically find the actual repo root
        actual_repo_root = self._find_repo_root(repo_path)
        if actual_repo_root != repo_path:
            print(f"📂 Found actual repo root: {actual_repo_root}")
            repo_path = actual_repo_root
        
        # Detect project structure
        structure = self._detect_project_structure(repo_path)
        
        # Setup the project
        setup_results = self.setup_services(structure)
        
        return {
            'status': 'success',
            'repo_root': actual_repo_root,
            'structure': structure,
            'setup_results': setup_results
        }
    
    def _find_repo_root(self, start_path: str) -> str:
        """Automatically find the actual repository root by looking for key files."""
        path = Path(start_path)
        
        # Look for key files that indicate a repository root
        key_files = [
            '.git',
            'package.json',
            'requirements.txt',
            'pyproject.toml',
            'Cargo.toml',
            'go.mod',
            'pom.xml',
            'build.gradle',
            'docker-compose.yml',
            'docker-compose.yaml',
            'Dockerfile',
            'Makefile',
            'README.md',
            'README.txt'
        ]
        
        # Search upward from start_path
        current_path = path
        while current_path != current_path.parent:
            for key_file in key_files:
                if (current_path / key_file).exists():
                    print(f"✅ Found repo root at: {current_path} (key file: {key_file})")
                    return str(current_path)
            current_path = current_path.parent
        
        # If no key files found, return the original path
        print(f"⚠️ No key files found, using original path: {start_path}")
        return start_path
    
    def _detect_project_structure(self, repo_path: str) -> dict:
        """Detect the project structure for setup."""
        structure = {
            'services': [],
            'files': {},
            'type': 'unknown'
        }
        
        repo_path_obj = Path(repo_path)
        
        # Look for common project files
        for file_path in repo_path_obj.rglob('*'):
            if file_path.is_file():
                relative_path = file_path.relative_to(repo_path_obj)
                structure['files'][str(relative_path)] = {
                    'type': 'file',
                    'size': file_path.stat().st_size
                }
                
                # Detect service types
                if file_path.name == 'package.json':
                    service_path = str(file_path.parent.relative_to(repo_path_obj))
                    structure['services'].append({
                        'name': file_path.parent.name or 'node-service',
                        'type': 'node',
                        'path': service_path,
                        'framework': self._detect_node_framework(file_path)
                    })
                elif file_path.name == 'requirements.txt':
                    service_path = str(file_path.parent.relative_to(repo_path_obj))
                    structure['services'].append({
                        'name': file_path.parent.name or 'python-service',
                        'type': 'python',
                        'path': service_path,
                        'framework': self._detect_python_framework(file_path.parent)
                    })
                elif file_path.name == 'Dockerfile':
                    service_path = str(file_path.parent.relative_to(repo_path_obj))
                    structure['services'].append({
                        'name': file_path.parent.name or 'docker-service',
                        'type': 'docker',
                        'path': service_path
                    })
        
        return structure
    
    def _detect_node_framework(self, package_json_path: Path) -> str:
        """Detect Node.js framework from package.json."""
        try:
            with open(package_json_path, 'r') as f:
                package_data = json.load(f)
            
            dependencies = package_data.get('dependencies', {})
            dev_dependencies = package_data.get('devDependencies', {})
            all_deps = {**dependencies, **dev_dependencies}
            
            if 'next' in all_deps:
                return 'next'
            elif 'react' in all_deps:
                return 'react'
            elif 'express' in all_deps:
                return 'express'
            elif 'vue' in all_deps:
                return 'vue'
            elif 'angular' in all_deps:
                return 'angular'
            else:
                return 'node'
        except:
            return 'node'
    
    def _detect_python_framework(self, service_path: Path) -> str:
        """Detect Python framework from service directory."""
        try:
            # Check for common Python frameworks
            if (service_path / 'manage.py').exists():
                return 'django'
            elif (service_path / 'app.py').exists() or (service_path / 'main.py').exists():
                return 'flask'
            elif (service_path / 'fastapi').exists() or any('fastapi' in f.read_text() for f in service_path.glob('*.py') if f.is_file()):
                return 'fastapi'
            else:
                return 'python'
        except:
            return 'python'

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

    def setup_services(self, structure):
        """Install dependencies for all detected services."""
        results = []
        for svc in structure.get('services', []):
            svc_type = svc['type']
            svc_path = svc['path']
            result = {'service': svc, 'result': -1, 'error': None}
            
            try:
                if svc_type == 'python':
                    req_path = os.path.join(svc_path, 'requirements.txt')
                    if os.path.exists(req_path):
                        # Try to create virtual environment
                        try:
                            venv_result = subprocess.run(['python3', '-m', 'venv', 'venv'], 
                                                       cwd=svc_path, capture_output=True, text=True)
                            if venv_result.returncode == 0:
                                # Use virtual environment pip
                                pip_path = os.path.join(svc_path, 'venv/bin/pip')
                                if os.path.exists(pip_path):
                                    install_result = subprocess.run([pip_path, 'install', '-r', 'requirements.txt'], 
                                                                  cwd=svc_path, capture_output=True, text=True)
                                    result['result'] = install_result.returncode
                                    if install_result.returncode != 0:
                                        result['error'] = install_result.stderr
                                else:
                                    # Fallback to system pip
                                    install_result = subprocess.run(['pip', 'install', '-r', 'requirements.txt'], 
                                                                  cwd=svc_path, capture_output=True, text=True)
                                    result['result'] = install_result.returncode
                                    if install_result.returncode != 0:
                                        result['error'] = install_result.stderr
                            else:
                                # Fallback to system pip without venv
                                install_result = subprocess.run(['pip', 'install', '-r', 'requirements.txt'], 
                                                              cwd=svc_path, capture_output=True, text=True)
                                result['result'] = install_result.returncode
                                if install_result.returncode != 0:
                                    result['error'] = install_result.stderr
                        except Exception as e:
                            # Final fallback
                            install_result = subprocess.run(['pip', 'install', '-r', 'requirements.txt'], 
                                                          cwd=svc_path, capture_output=True, text=True)
                            result['result'] = install_result.returncode
                            if install_result.returncode != 0:
                                result['error'] = install_result.stderr
                    else:
                        result['error'] = 'No requirements.txt found'
                        
                elif svc_type == 'node':
                    package_json_path = os.path.join(svc_path, 'package.json')
                    if os.path.exists(package_json_path):
                        # Check for yarn.lock first
                        if os.path.exists(os.path.join(svc_path, 'yarn.lock')):
                            install_result = subprocess.run(['yarn', 'install'], 
                                                          cwd=svc_path, capture_output=True, text=True)
                        else:
                            install_result = subprocess.run(['npm', 'install'], 
                                                          cwd=svc_path, capture_output=True, text=True)
                        result['result'] = install_result.returncode
                        if install_result.returncode != 0:
                            result['error'] = install_result.stderr
                    else:
                        result['error'] = 'No package.json found'
                        
            except Exception as e:
                result['error'] = str(e)
                
            results.append(result)
        return results 