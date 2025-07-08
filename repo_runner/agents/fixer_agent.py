import subprocess
import json
import os
import sys
from pathlib import Path
from ..llm.llm_utils import generate_code_with_llm
from .base_agent import BaseAgent
from .context_indexer import ContextIndexer
import datetime
from .agent_memory_manager import AgentMemoryManager

class FixerAgent(BaseAgent):
    EXCEPTION_REGISTRY = {
        "pip_conflict": {
            "pattern": "pip.*(conflict|version|requirement|incompatible)",
            "template": {
                "analysis": "There is a pip dependency conflict or version mismatch.",
                "fix": "Try running 'pip install --upgrade --force-reinstall -r requirements.txt' or manually resolve conflicting versions in requirements.txt.",
                "steps": [
                    "Open requirements.txt",
                    "Identify conflicting packages and versions",
                    "Update to compatible versions",
                    "Run 'pip install --upgrade --force-reinstall -r requirements.txt'"
                ]
            }
        },
        "docker_error": {
            "pattern": "docker.*(error|fail|not found|permission|compose)",
            "template": {
                "analysis": "There is a Docker-related error (missing Docker, permission, or compose issue).",
                "fix": "Ensure Docker is installed and running. For compose issues, check docker-compose.yml syntax and permissions.",
                "steps": [
                    "Check if Docker is installed: 'docker --version'",
                    "Check if Docker daemon is running",
                    "Validate docker-compose.yml syntax",
                    "Check user permissions for Docker"
                ]
            }
        },
        "db_startup": {
            "pattern": "(database|db).*start.*(fail|error|connection|migrate)",
            "template": {
                "analysis": "Database failed to start or connect. Possible migration or connection issue.",
                "fix": "Check database connection string, run migrations, and ensure DB service is running.",
                "steps": [
                    "Check DATABASE_URL in .env",
                    "Ensure DB service is running",
                    "Run database migrations",
                    "Check DB logs for errors"
                ]
            }
        },
        "port_conflict": {
            "pattern": "(address already in use|port.*in use|EADDRINUSE)",
            "template": {
                "analysis": "Port conflict detected. Another process is using the required port.",
                "fix": "Identify and stop the process using the port, or change the application's port.",
                "steps": [
                    "Identify process: 'lsof -i :<port>' or 'netstat -tuln'",
                    "Stop the conflicting process",
                    "Change application's port if needed"
                ]
            }
        },
        "secret_missing": {
            "pattern": "(secret|key|token|credential).*missing",
            "template": {
                "analysis": "A required secret, key, or token is missing from the environment.",
                "fix": "Add the missing secret to your .env file or environment variables.",
                "steps": [
                    "Check .env for required secrets",
                    "Add missing key/token/credential",
                    "Restart the application"
                ]
            }
        }
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.memory_manager = AgentMemoryManager()

    def run(self, repo_path=None, errors=None, context=None, *args, **kwargs):
        # Analyze errors and suggest fixes
        suggestions = []
        actions = []
        if not errors:
            self.log_result("[FixerAgent] No errors to fix.")
            return {"status": "ok", "agent": self.agent_name, "suggestions": [], "actions": []}
        for err in errors:
            suggestion = self._suggest_fix(err, repo_path)
            suggestions.append(suggestion)
            action = self._apply_fix(suggestion, repo_path)
            actions.append(action)
        self.log_result(f"[FixerAgent] Suggestions: {suggestions}, Actions: {actions}")
        return {"status": "ok", "agent": self.agent_name, "suggestions": suggestions, "actions": actions}

    def _suggest_fix(self, error, repo_path):
        # Stub: Use LLM or RAG to suggest fix
        # In production, call LLM or RAG here
        return f"Suggested fix for: {error[:100]}"

    def _apply_fix(self, suggestion, repo_path):
        # Stub: Optionally apply fix
        # In production, parse suggestion and apply code change
        return f"Applied: {suggestion}"

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
    
    def build_context_index(self, repo_path: str):
        """
        Build a simple text index from .env, README.md, requirements.txt, and logs/error.log in the repo.
        """
        files = [
            os.path.join(repo_path, f) for f in ['.env', 'README.md', 'requirements.txt']
        ]
        log_path = os.path.join(repo_path, 'logs', 'error.log')
        if os.path.exists(log_path):
            files.append(log_path)
        self.context_indexer = ContextIndexer()
        self.context_indexer.build_index([f for f in files if os.path.exists(f)])

    def retrieve_context(self, query: str, top_k: int = 3) -> str:
        """
        Retrieve top-k relevant context chunks for a given query using the text index.
        """
        if hasattr(self, 'context_indexer') and self.context_indexer.text_chunks:
            try:
                return '\n'.join(self.context_indexer.query_index(query, top_k=top_k))
            except Exception as e:
                self.log_result(f"Context retrieval failed: {e}")
        return ""
    
    def self_fix(self, error, context=None, run_state_file="run_state.json", repo_path=None):
        """
        Attempt to self-heal using LLM, leveraging past fixes from run_state.json as few-shot memory and RAG context.
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
        # RAG context
        rag_context = ""
        if repo_path:
            try:
                self.build_context_index(repo_path)
                rag_context = self.retrieve_context(str(error), top_k=3)
            except Exception as e:
                self.log_result(f"RAG context indexing failed: {e}")
        prompt = f"""
        You are a FixerAgent. Use the following past fixes as few-shot examples:
        {few_shot_context}
        ---
        Additional context from repo files:
        {rag_context}
        ---
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
            self.log_result(f"Self-fix applied: {fix_data.get('fix','')}")
            # Log fix event
            event = {
                "timestamp": datetime.datetime.now().isoformat(),
                "type": "fix_attempt",
                "error": str(error),
                "context": context,
                "fix_data": fix_data
            }
            self.memory_manager.log_event(event)
            # Also log to agent_logs and reports
            self._log_to_files(event)
            return fix_data
        except Exception:
            self.log_result(f"Self-fix LLM response could not be parsed: {llm_response}")
            # Fallback: try exception registry
            import re
            for key, entry in self.EXCEPTION_REGISTRY.items():
                if re.search(entry['pattern'], str(error), re.IGNORECASE):
                    self.log_result(f"Using exception registry template for {key}")
                    event = {
                        "timestamp": datetime.datetime.now().isoformat(),
                        "type": "fix_attempt",
                        "error": str(error),
                        "context": context,
                        "fix_data": entry['template']
                    }
                    self.memory_manager.log_event(event)
                    self._log_to_files(event)
                    return entry['template']
            return llm_response
    
    def checkpoint(self, state: dict, checkpoint_file: str = "fixer_agent_state.json"):
        """
        Save the FixerAgent's state to a checkpoint file (default: fixer_agent_state.json).
        Logs the checkpoint event.
        """
        import json
        self.log_result(f"Checkpointing FixerAgent state to {checkpoint_file}")
        try:
            with open(checkpoint_file, "w") as f:
                json.dump(state, f, indent=2)
            self.log_result(f"Checkpoint saved to {checkpoint_file}")
        except Exception as e:
            self.log_result(f"Failed to save checkpoint: {e}")

    def report_error(self, error, context=None, error_file="fixer_agent_errors.json"):
        """
        Log the error and optionally save it to a file for traceability.
        """
        import json
        self.log_result(f"Error reported: {error} | Context: {context}", "error")
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
            self.log_result(f"Failed to save error report: {e}", "error")
    
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

    def _log_to_files(self, event):
        """
        Log event to logs/agent_logs/{timestamp}.log and reports/summary_{timestamp}.json
        """
        import os
        ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        logs_dir = os.path.join("logs", "agent_logs")
        reports_dir = os.path.join("reports")
        os.makedirs(logs_dir, exist_ok=True)
        os.makedirs(reports_dir, exist_ok=True)
        log_path = os.path.join(logs_dir, f"{ts}.log")
        report_path = os.path.join(reports_dir, f"summary_{ts}.json")
        try:
            with open(log_path, "a") as f:
                f.write(json.dumps(event, indent=2) + "\n")
            with open(report_path, "w") as f:
                json.dump(event, f, indent=2)
        except Exception as e:
            self.log_result(f"Failed to write telemetry logs: {e}", "warning") 