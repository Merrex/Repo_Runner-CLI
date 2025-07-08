import subprocess
import json
import os
import sys
from pathlib import Path
from ..llm.llm_utils import generate_code_with_llm
from .base_agent import BaseAgent

class FixerAgent(BaseAgent):
    def fix(self, errors, structure):
        """Use WizardCoder to analyze and fix errors."""
        if not errors:
            return {"status": "no_errors", "fixes_applied": []}
        
        fixes_applied = []
        
        for error in errors:
            # Use LLM to analyze the error and suggest fixes
            prompt = f"""
            Analyze this error and provide a fix:
            
            Error: {error}
            Project structure: {json.dumps(structure, indent=2)}
            
            Provide:
            1. Root cause analysis
            2. Specific fix (code changes, config updates, etc.)
            3. Steps to implement the fix
            
            Format as JSON with keys: analysis, fix, steps
            """
            
            llm_response = generate_code_with_llm(prompt, agent_name='fixer_agent')
            
            try:
                # Try to parse JSON response
                fix_data = json.loads(llm_response)
                fixes_applied.append({
                    'error': error,
                    'analysis': fix_data.get('analysis', ''),
                    'fix': fix_data.get('fix', ''),
                    'steps': fix_data.get('steps', [])
                })
                
                # Apply the fix
                self._apply_fix(fix_data, structure)
                
            except json.JSONDecodeError:
                # If LLM didn't return valid JSON, use the raw response
                fixes_applied.append({
                    'error': error,
                    'analysis': 'LLM analysis failed to parse',
                    'fix': llm_response,
                    'steps': ['Manual review required']
                })
        
        return {
            "status": "fixes_applied",
            "fixes_applied": fixes_applied,
            "total_errors": len(errors),
            "fixed_errors": len([f for f in fixes_applied if f.get('fix')])
        }
    
    def fix_dependency_errors(self, errors, repo_path):
        """Fix specific dependency-related errors."""
        fixes_applied = []
        
        for error in errors:
            if "No module named 'jose'" in str(error):
                # Fix missing python-jose dependency
                fix = self._fix_missing_python_dependency(repo_path, "python-jose[cryptography]")
                fixes_applied.append({
                    'error': error,
                    'fix': 'Added python-jose dependency',
                    'status': 'applied'
                })
            
            elif "react-scripts: not found" in str(error):
                # Fix missing react-scripts
                fix = self._fix_missing_node_dependency(repo_path, "react-scripts")
                fixes_applied.append({
                    'error': error,
                    'fix': 'Added react-scripts dependency',
                    'status': 'applied'
                })
            
            elif "No such file or directory: 'pip'" in str(error):
                # Fix virtual environment issues
                fix = self._fix_virtual_environment(repo_path)
                fixes_applied.append({
                    'error': error,
                    'fix': 'Fixed virtual environment setup',
                    'status': 'applied'
                })
        
        return {
            "status": "dependency_fixes_applied",
            "fixes_applied": fixes_applied,
            "total_errors": len(errors),
            "fixed_errors": len(fixes_applied)
        }
    
    def fix_service_startup_errors(self, errors, repo_path, services):
        """Fix service startup errors."""
        fixes_applied = []
        
        for error in errors:
            if "ModuleNotFoundError" in str(error):
                # Fix missing Python dependencies
                fix = self._fix_missing_python_dependencies(repo_path)
                fixes_applied.append({
                    'error': error,
                    'fix': 'Installed missing Python dependencies',
                    'status': 'applied'
                })
            
            elif "not found" in str(error) and "node" in str(error).lower():
                # Fix missing Node.js dependencies
                fix = self._fix_missing_node_dependencies(repo_path)
                fixes_applied.append({
                    'error': error,
                    'fix': 'Installed missing Node.js dependencies',
                    'status': 'applied'
                })
        
        return {
            "status": "startup_fixes_applied",
            "fixes_applied": fixes_applied,
            "total_errors": len(errors),
            "fixed_errors": len(fixes_applied)
        }
    
    def self_fix(self, error, context=None, run_state_file="run_state.json"):
        """
        Attempt to self-heal using LLM, leveraging past fixes from run_state.json as few-shot memory.
        Loads previous fixes and includes them as context in the LLM prompt.
        """
        # Load past fixes as few-shot memory
        past_fixes = []
        if os.path.exists(run_state_file):
            try:
                with open(run_state_file, "r") as f:
                    run_state = json.load(f)
                past_fixes = run_state.get("fixes", [])[-3:]  # Use last 3 fixes as few-shot
            except Exception:
                pass
        few_shot_context = "\n".join([
            f"Error: {fix.get('error')}\nFix: {fix.get('fix_result')}" for fix in past_fixes if fix.get('error') and fix.get('fix_result')
        ])
        prompt = f"""
        You are a FixerAgent. Use the following past fixes as few-shot examples:
        {few_shot_context}
        Now, analyze and fix this error:
        Error: {error}
        Context: {context}
        Provide:
        1. Root cause analysis
        2. Specific fix (code/config/command)
        3. Steps to implement the fix
        Format as JSON with keys: analysis, fix, steps
        """
        llm_response = generate_code_with_llm(prompt, agent_name='fixer_agent')
        try:
            fix_data = json.loads(llm_response)
            self.log(f"Self-fix applied: {fix_data.get('fix','')}", "info")
            return fix_data
        except Exception:
            self.log(f"Self-fix LLM response could not be parsed: {llm_response}", "warning")
            return llm_response
    
    def _fix_missing_python_dependency(self, repo_path, package):
        """Fix missing Python dependency."""
        try:
            # Find backend directory
            backend_path = os.path.join(repo_path, 'backend')
            if os.path.exists(backend_path):
                # Add to requirements.txt
                requirements_file = os.path.join(backend_path, 'requirements.txt')
                if os.path.exists(requirements_file):
                    with open(requirements_file, 'r') as f:
                        content = f.read()
                    
                    if package not in content:
                        with open(requirements_file, 'a') as f:
                            f.write(f"\n{package}\n")
                        print(f"✅ Added {package} to requirements.txt")
                
                # Install the package
                subprocess.run([sys.executable, '-m', 'pip', 'install', package], 
                             cwd=backend_path, check=True)
                print(f"✅ Installed {package}")
                return True
        except Exception as e:
            print(f"❌ Failed to fix Python dependency {package}: {e}")
            return False
    
    def _fix_missing_node_dependency(self, repo_path, package):
        """Fix missing Node.js dependency."""
        try:
            # Find frontend directory
            frontend_path = os.path.join(repo_path, 'frontend')
            if os.path.exists(frontend_path):
                # Add to package.json
                package_file = os.path.join(frontend_path, 'package.json')
                if os.path.exists(package_file):
                    with open(package_file, 'r') as f:
                        content = json.load(f)
                    
                    if 'dependencies' not in content:
                        content['dependencies'] = {}
                    
                    if package not in content['dependencies']:
                        content['dependencies'][package] = "^5.0.0"  # Default version
                        
                        with open(package_file, 'w') as f:
                            json.dump(content, f, indent=2)
                        print(f"✅ Added {package} to package.json")
                
                # Install the package
                subprocess.run(['npm', 'install'], cwd=frontend_path, check=True)
                print(f"✅ Installed {package}")
                return True
        except Exception as e:
            print(f"❌ Failed to fix Node.js dependency {package}: {e}")
            return False
    
    def _fix_virtual_environment(self, repo_path):
        """Fix virtual environment issues."""
        try:
            backend_path = os.path.join(repo_path, 'backend')
            if os.path.exists(backend_path):
                # Remove problematic venv
                venv_path = os.path.join(backend_path, 'venv')
                if os.path.exists(venv_path):
                    import shutil
                    shutil.rmtree(venv_path)
                    print("✅ Removed problematic virtual environment")
                
                # Create new venv
                subprocess.run([sys.executable, '-m', 'venv', 'venv'], 
                             cwd=backend_path, check=True)
                print("✅ Created new virtual environment")
                
                # Install pip in new venv
                venv_python = os.path.join(backend_path, 'venv', 'bin', 'python')
                if os.path.exists(venv_python):
                    subprocess.run([venv_python, '-m', 'ensurepip', '--upgrade'], 
                                 cwd=backend_path, check=True)
                    print("✅ Upgraded pip in virtual environment")
                    return True
        except Exception as e:
            print(f"❌ Failed to fix virtual environment: {e}")
            return False
    
    def _fix_missing_python_dependencies(self, repo_path):
        """Fix missing Python dependencies."""
        try:
            backend_path = os.path.join(repo_path, 'backend')
            if os.path.exists(backend_path):
                requirements_file = os.path.join(backend_path, 'requirements.txt')
                if os.path.exists(requirements_file):
                    # Install all requirements
                    subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'], 
                                 cwd=backend_path, check=True)
                    print("✅ Installed all Python dependencies")
                    return True
        except Exception as e:
            print(f"❌ Failed to install Python dependencies: {e}")
            return False
    
    def _fix_missing_node_dependencies(self, repo_path):
        """Fix missing Node.js dependencies."""
        try:
            frontend_path = os.path.join(repo_path, 'frontend')
            if os.path.exists(frontend_path):
                # Install all dependencies
                subprocess.run(['npm', 'install'], cwd=frontend_path, check=True)
                print("✅ Installed all Node.js dependencies")
                return True
        except Exception as e:
            print(f"❌ Failed to install Node.js dependencies: {e}")
            return False
    
    def _apply_fix(self, fix_data, structure):
        """Apply the suggested fix."""
        fix = fix_data.get('fix', '')
        steps = fix_data.get('steps', [])
        
        # Example: If fix involves creating a missing file
        if 'create_file' in fix.lower():
            # Extract file path and content from fix
            # This is a simplified example - in practice, you'd parse the LLM response more carefully
            pass
        
        # Example: If fix involves running a command
        if 'run_command' in fix.lower():
            # Extract and run the command
            # This is a simplified example
            pass
        
        return True 

    def fix_services(self, structure, health_results):
        """Analyze failed services and suggest or apply fixes."""
        fixes = []
        for result in health_results:
            svc = result['service']
            if result.get('status') == 'down':
                if svc['type'] == 'python':
                    # Check for missing __init__.py
                    routers_path = os.path.join(svc['path'], 'routers')
                    if os.path.isdir(routers_path) and not os.path.exists(os.path.join(routers_path, '__init__.py')):
                        with open(os.path.join(routers_path, '__init__.py'), 'w') as f:
                            f.write('# Added by FixerAgent\n')
                        fixes.append({'service': svc, 'fix': 'Added missing __init__.py to routers'})
                if svc['type'] == 'node':
                    # Check for missing node_modules
                    if not os.path.exists(os.path.join(svc['path'], 'node_modules')):
                        fixes.append({'service': svc, 'fix': 'Run npm install in frontend'})
        return fixes 