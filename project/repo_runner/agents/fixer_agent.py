import subprocess
import json
from pathlib import Path
from ..llm.llm_utils import generate_code_with_llm
import os

class FixerAgent:
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