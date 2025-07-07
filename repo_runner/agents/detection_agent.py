import os
import json
import yaml
import subprocess
from typing import Dict, List, Optional, Any
from pathlib import Path
import re
from ..llm.llm_utils import generate_code_with_llm
from .base_agent import BaseAgent

class RecursiveConfigScanner:
    """Enhanced config scanner that recursively searches all directories"""
    
    def __init__(self):
        self.config_patterns = {
            'python': ['requirements.txt', 'setup.py', 'pyproject.toml', 'Pipfile', 'poetry.lock'],
            'node': ['package.json', 'package-lock.json', 'yarn.lock', 'pnpm-lock.yaml'],
            'docker': ['Dockerfile', 'docker-compose.yml', 'docker-compose.yaml', '.dockerignore'],
            'database': ['schema.sql', 'migrations/', 'prisma/schema.prisma'],
            'config': ['.env', '.env.local', '.env.production', 'config.json', 'config.yml', 'config.yaml'],
            'deployment': ['kubernetes/', 'helm/', 'docker-compose.yml', 'docker-compose.yaml'],
            'frontend': ['index.html', 'App.js', 'App.jsx', 'main.js', 'main.ts', 'vite.config.js', 'next.config.js'],
            'backend': ['server.js', 'app.py', 'main.py', 'index.js', 'app.js', 'server.py'],
            'testing': ['jest.config.js', 'pytest.ini', 'cypress.json', 'playwright.config.js'],
            'ci_cd': ['.github/', '.gitlab-ci.yml', 'Jenkinsfile', 'travis.yml', 'circle.yml']
        }
        
        self.service_patterns = {
            'react': ['react', 'create-react-app', 'vite'],
            'vue': ['vue', 'nuxt'],
            'angular': ['angular', '@angular'],
            'express': ['express', 'koa', 'fastify'],
            'django': ['django', 'djangorestframework'],
            'flask': ['flask', 'fastapi'],
            'spring': ['spring-boot', 'springframework'],
            'laravel': ['laravel'],
            'rails': ['rails', 'ruby-on-rails'],
            'dotnet': ['dotnet', 'aspnetcore']
        }
    
    def scan_all_directories(self, repo_path: str) -> Dict[str, Any]:
        """Recursively scan all directories for configuration files"""
        print(f"🔍 Scanning all directories in {repo_path} for configuration files...")
        
        found_configs = {}
        service_dependencies = {}
        project_structure = {}
        
        for root, dirs, files in os.walk(repo_path):
            rel_path = os.path.relpath(root, repo_path)
            
            # Skip common directories that don't contain configs
            dirs[:] = [d for d in dirs if not self._should_skip_directory(d)]
            
            for file in files:
                file_path = os.path.join(root, file)
                rel_file_path = os.path.join(rel_path, file)
                
                # Categorize file by type
                file_type = self._categorize_file(file, file_path)
                
                if file_type:
                    if file_type not in found_configs:
                        found_configs[file_type] = []
                    
                    config_info = self._analyze_config_file(file_path, file_type)
                    config_info['relative_path'] = rel_file_path
                    config_info['full_path'] = file_path
                    
                    found_configs[file_type].append(config_info)
                    
                    # Build service dependencies
                    if file_type in ['python', 'node', 'docker']:
                        service_info = self._extract_service_info(config_info, file_type)
                        if service_info:
                            service_dependencies[rel_file_path] = service_info
        
        # Build project structure
        project_structure = self._build_project_structure(repo_path)
        
        return {
            'configs': found_configs,
            'services': service_dependencies,
            'structure': project_structure,
            'summary': self._generate_scan_summary(found_configs, service_dependencies)
        }
    
    def _should_skip_directory(self, dir_name: str) -> bool:
        """Check if directory should be skipped during scanning"""
        skip_patterns = [
            'node_modules', '.git', '.svn', '.hg',
            '__pycache__', '.pytest_cache', '.mypy_cache',
            'dist', 'build', 'target', 'out',
            '.vscode', '.idea', '.vs',
            'coverage', '.nyc_output',
            'tmp', 'temp', 'cache'
        ]
        return dir_name in skip_patterns or dir_name.startswith('.')
    
    def _categorize_file(self, filename: str, file_path: str) -> Optional[str]:
        """Categorize file by type based on name and content"""
        filename_lower = filename.lower()
        
        # Check by filename patterns
        for category, patterns in self.config_patterns.items():
            if filename in patterns:
                return category
        
        # Check by file extension
        if filename_lower.endswith('.py'):
            return 'python'
        elif filename_lower.endswith(('.js', '.jsx', '.ts', '.tsx')):
            return 'node'
        elif filename_lower.endswith('.java'):
            return 'java'
        elif filename_lower.endswith(('.go', '.mod')):
            return 'go'
        elif filename_lower.endswith('.rs'):
            return 'rust'
        elif filename_lower.endswith('.php'):
            return 'php'
        elif filename_lower.endswith('.rb'):
            return 'ruby'
        elif filename_lower.endswith('.cs'):
            return 'dotnet'
        
        # Check by content for config files
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read(1024)  # Read first 1KB
                
                if 'package.json' in filename_lower or '"name"' in content:
                    return 'node'
                elif 'requirements.txt' in filename_lower or 'setup.py' in filename_lower:
                    return 'python'
                elif 'dockerfile' in filename_lower or 'FROM ' in content.upper():
                    return 'docker'
                elif 'docker-compose' in filename_lower or 'services:' in content:
                    return 'docker'
                elif '.env' in filename_lower or '=' in content and '\n' in content:
                    return 'config'
        except Exception:
            pass
        
        return None
    
    def _analyze_config_file(self, file_path: str, file_type: str) -> Dict[str, Any]:
        """Analyze configuration file and extract relevant information"""
        config_info = {
            'type': file_type,
            'filename': os.path.basename(file_path),
            'size': os.path.getsize(file_path)
        }
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                config_info['content_preview'] = content[:500]
                
                if file_type == 'node':
                    config_info.update(self._analyze_node_config(content))
                elif file_type == 'python':
                    config_info.update(self._analyze_python_config(content))
                elif file_type == 'docker':
                    config_info.update(self._analyze_docker_config(content))
                elif file_type == 'config':
                    config_info.update(self._analyze_env_config(content))
                
        except Exception as e:
            config_info['error'] = str(e)
        
        return config_info
    
    def _analyze_node_config(self, content: str) -> Dict[str, Any]:
        """Analyze Node.js configuration files"""
        try:
            data = json.loads(content)
            return {
                'name': data.get('name', 'unknown'),
                'version': data.get('version', 'unknown'),
                'scripts': list(data.get('scripts', {}).keys()),
                'dependencies': list(data.get('dependencies', {}).keys()),
                'devDependencies': list(data.get('devDependencies', {}).keys()),
                'engines': data.get('engines', {}),
                'type': data.get('type', 'commonjs')
            }
        except Exception as e:
            return {'error': f'Failed to parse JSON: {e}'}
    
    def _analyze_python_config(self, content: str) -> Dict[str, Any]:
        """Analyze Python configuration files"""
        config = {}
        
        if 'requirements.txt' in content:
            # Parse requirements.txt
            requirements = []
            for line in content.split('\n'):
                line = line.strip()
                if line and not line.startswith('#'):
                    requirements.append(line.split('==')[0].split('>=')[0].split('<=')[0])
            config['requirements'] = requirements
        
        elif 'setup.py' in content:
            # Extract from setup.py
            import re
            name_match = re.search(r'name\s*=\s*["\']([^"\']+)["\']', content)
            if name_match:
                config['name'] = name_match.group(1)
        
        return config
    
    def _analyze_docker_config(self, content: str) -> Dict[str, Any]:
        """Analyze Docker configuration files"""
        config = {}
        
        if 'docker-compose' in content.lower():
            try:
                data = yaml.safe_load(content)
                config['services'] = list(data.get('services', {}).keys())
                config['version'] = data.get('version', 'unknown')
            except Exception as e:
                config['error'] = f'Failed to parse YAML: {e}'
        else:
            # Dockerfile analysis
            import re
            from_match = re.search(r'FROM\s+([^\s]+)', content, re.IGNORECASE)
            if from_match:
                config['base_image'] = from_match.group(1)
            
            expose_matches = re.findall(r'EXPOSE\s+(\d+)', content, re.IGNORECASE)
            if expose_matches:
                config['exposed_ports'] = [int(port) for port in expose_matches]
        
        return config
    
    def _analyze_env_config(self, content: str) -> Dict[str, Any]:
        """Analyze environment configuration files"""
        config = {}
        
        # Parse environment variables
        env_vars = {}
        for line in content.split('\n'):
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                env_vars[key] = value
        
        config['environment_variables'] = env_vars
        config['var_count'] = len(env_vars)
        
        return config
    
    def _extract_service_info(self, config_info: Dict[str, Any], file_type: str) -> Optional[Dict[str, Any]]:
        """Extract service information from configuration"""
        service_info = {
            'type': file_type,
            'name': config_info.get('name', 'unknown'),
            'version': config_info.get('version', 'unknown')
        }
        
        if file_type == 'node':
            # Detect framework
            dependencies = config_info.get('dependencies', [])
            for framework, patterns in self.service_patterns.items():
                if any(pattern in str(dependencies) for pattern in patterns):
                    service_info['framework'] = framework
                    break
            
            # Detect if it's frontend or backend
            scripts = config_info.get('scripts', [])
            if any('dev' in script.lower() for script in scripts):
                service_info['role'] = 'frontend'
            elif any('start' in script.lower() for script in scripts):
                service_info['role'] = 'backend'
        
        elif file_type == 'python':
            requirements = config_info.get('requirements', [])
            if 'django' in str(requirements):
                service_info['framework'] = 'django'
                service_info['role'] = 'backend'
            elif 'flask' in str(requirements):
                service_info['framework'] = 'flask'
                service_info['role'] = 'backend'
            elif 'fastapi' in str(requirements):
                service_info['framework'] = 'fastapi'
                service_info['role'] = 'backend'
        
        elif file_type == 'docker':
            services = config_info.get('services', [])
            if services:
                service_info['services'] = services
                service_info['role'] = 'orchestration'
        
        return service_info if service_info.get('framework') or service_info.get('role') else None
    
    def _build_project_structure(self, repo_path: str) -> Dict[str, Any]:
        """Build a comprehensive project structure"""
        structure = {
            'root': repo_path,
            'directories': {},
            'files': {},
            'depth': 0
        }
        
        for root, dirs, files in os.walk(repo_path):
            rel_path = os.path.relpath(root, repo_path)
            if rel_path == '.':
                rel_path = ''
            
            # Add directories
            if rel_path not in structure['directories']:
                structure['directories'][rel_path] = []
            
            for dir_name in dirs:
                if not self._should_skip_directory(dir_name):
                    structure['directories'][rel_path].append(dir_name)
            
            # Add files
            if rel_path not in structure['files']:
                structure['files'][rel_path] = []
            
            for file_name in files:
                file_type = self._categorize_file(file_name, os.path.join(root, file_name))
                if file_type:
                    structure['files'][rel_path].append({
                        'name': file_name,
                        'type': file_type
                    })
        
        return structure
    
    def _generate_scan_summary(self, configs: Dict[str, List], services: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a summary of the scan results"""
        summary = {
            'total_config_files': sum(len(files) for files in configs.values()),
            'config_types': list(configs.keys()),
            'service_count': len(services),
            'frameworks_detected': [],
            'roles_detected': []
        }
        
        # Extract frameworks and roles
        for service_info in services.values():
            if 'framework' in service_info:
                summary['frameworks_detected'].append(service_info['framework'])
            if 'role' in service_info:
                summary['roles_detected'].append(service_info['role'])
        
        summary['frameworks_detected'] = list(set(summary['frameworks_detected']))
        summary['roles_detected'] = list(set(summary['roles_detected']))
        
        return summary

# Enhanced Detection Agent
class DetectionAgent(BaseAgent):
    """Enhanced detection agent with recursive config scanning"""
    
    def __init__(self):
        super().__init__()
        self.config_scanner = RecursiveConfigScanner()
        self.detected_services = {}
        self.project_structure = {}
    
    def detect_project_structure(self, repo_path: str) -> Dict[str, Any]:
        """Enhanced project detection with recursive scanning"""
        print("🔍 Analyzing repository structure and services...")
        
        try:
            # Perform recursive config scan
            scan_results = self.config_scanner.scan_all_directories(repo_path)
            
            # Store results
            self.detected_services = scan_results['services']
            self.project_structure = scan_results['structure']
            
            # Generate detection summary
            detection_summary = {
                'status': 'success',
                'config_files_found': scan_results['summary']['total_config_files'],
                'services_detected': len(scan_results['services']),
                'frameworks': scan_results['summary']['frameworks_detected'],
                'roles': scan_results['summary']['roles_detected'],
                'structure': scan_results['structure'],
                'services': scan_results['services'],
                'configs': scan_results['configs']
            }
            
            print(f"✅ Repository Analysis completed successfully")
            print(f"   📁 Found {scan_results['summary']['total_config_files']} config files")
            print(f"   🔧 Detected {len(scan_results['services'])} services")
            print(f"   🛠️  Frameworks: {', '.join(scan_results['summary']['frameworks_detected'])}")
            print(f"   🎭 Roles: {', '.join(scan_results['summary']['roles_detected'])}")
            
            return detection_summary
            
        except Exception as e:
            print(f"❌ Repository analysis failed: {e}")
            return {
                'status': 'error',
                'error': str(e),
                'services_detected': 0
            }
    
    def get_service_dependencies(self) -> Dict[str, Any]:
        """Get detected service dependencies"""
        return self.detected_services
    
    def get_project_structure(self) -> Dict[str, Any]:
        """Get project structure information"""
        return self.project_structure

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

    # Deprecated: Use detect_project_structure instead
    def detect_services(self, repo_path):
        raise NotImplementedError('detect_services is deprecated. Use detect_project_structure instead.') 