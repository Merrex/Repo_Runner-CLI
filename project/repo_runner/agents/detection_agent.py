import os
from pathlib import Path
from ..llm.llm_utils import generate_code_with_llm

class DetectionAgent:
    def analyze(self, repo_path):
        """Analyze the repository using LLM for intelligent detection."""
        repo_path = Path(repo_path)
        
        # Basic file detection
        files = self._scan_files(repo_path)
        
        # Use LLM to analyze project structure
        prompt = f"""
        Analyze this project structure and determine:
        1. Project type (backend, frontend, fullstack, etc.)
        2. Technologies used (Python, Node.js, React, etc.)
        3. Missing critical files
        4. Potential issues or improvements needed
        
        Files found: {list(files.keys())}
        
        Provide a structured analysis in JSON format.
        """
        
        analysis = generate_code_with_llm(prompt, agent_name='detection_agent')
        
        return {
            'type': 'auto-detected',
            'technologies': ['Python', 'Docker'],  # Placeholder
            'files': files,
            'analysis': analysis,
            'missing_files': self._detect_missing_files(files),
            'repo_path': str(repo_path)  # Add repository path
        }
    
    def _scan_files(self, repo_path):
        """Scan repository for important files."""
        files = {}
        for file_path in repo_path.rglob('*'):
            if file_path.is_file():
                rel_path = file_path.relative_to(repo_path)
                files[str(rel_path)] = {
                    'size': file_path.stat().st_size,
                    'type': self._get_file_type(file_path)
                }
        return files
    
    def _get_file_type(self, file_path):
        """Determine file type based on extension."""
        ext = file_path.suffix.lower()
        if ext in ['.py']:
            return 'python'
        elif ext in ['.js', '.ts', '.jsx', '.tsx']:
            return 'javascript'
        elif ext in ['.json']:
            return 'config'
        elif ext in ['.md']:
            return 'documentation'
        elif ext in ['.yml', '.yaml']:
            return 'config'
        else:
            return 'other'
    
    def _detect_missing_files(self, files):
        """Detect commonly missing files."""
        missing = []
        common_files = ['requirements.txt', 'package.json', 'README.md', '.env.example']
        
        for file in common_files:
            if file not in files:
                missing.append(file)
        
        return missing 