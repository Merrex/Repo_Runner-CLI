"""
Project structure detection functionality.
"""

import os
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from .logger import get_logger


class ProjectDetector:
    """Detects project structure and technologies."""
    
    def __init__(self, path: Path):
        self.path = path
        self.logger = get_logger()
    
    def detect(self) -> Dict[str, Any]:
        """Main detection method."""
        structure = {
            'type': 'unknown',
            'technologies': [],
            'components': {},
            'database': None,
            'docker': False,
            'ci_cd': [],
            'files': {},
            'package_managers': []
        }
        
        # Detect files
        structure['files'] = self._detect_files()
        
        # Detect project type and technologies
        structure = self._detect_project_type(structure)
        structure = self._detect_technologies(structure)
        structure = self._detect_components(structure)
        structure = self._detect_database(structure)
        structure = self._detect_docker(structure)
        structure = self._detect_ci_cd(structure)
        structure = self._detect_package_managers(structure)
        
        return structure
    
    def _detect_files(self) -> Dict[str, bool]:
        """Detect presence of key files."""
        key_files = {
            # Python
            'main.py': False,
            'app.py': False,
            'manage.py': False,
            'requirements.txt': False,
            'pyproject.toml': False,
            'poetry.lock': False,
            'Pipfile': False,
            'setup.py': False,
            
            # JavaScript/Node
            'package.json': False,
            'package-lock.json': False,
            'yarn.lock': False,
            'pnpm-lock.yaml': False,
            'index.js': False,
            'index.ts': False,
            'server.js': False,
            
            # Frontend
            'index.html': False,
            'vite.config.js': False,
            'vite.config.ts': False,
            'webpack.config.js': False,
            'next.config.js': False,
            'nuxt.config.js': False,
            'angular.json': False,
            'vue.config.js': False,
            
            # Docker
            'Dockerfile': False,
            'docker-compose.yml': False,
            'docker-compose.yaml': False,
            '.dockerignore': False,
            
            # Database
            'prisma/schema.prisma': False,
            'alembic.ini': False,
            'migrate.py': False,
            'database.py': False,
            'models.py': False,
            'schema.sql': False,
            
            # Config
            '.env': False,
            '.env.example': False,
            '.env.local': False,
            'config.py': False,
            'settings.py': False,
            
            # CI/CD
            '.github/workflows': False,
            '.gitlab-ci.yml': False,
            'azure-pipelines.yml': False,
            'Jenkinsfile': False,
            '.travis.yml': False,
            
            # Other
            'README.md': False,
            'LICENSE': False,
            'Makefile': False,
            '.gitignore': False,
        }
        
        for file_path in key_files.keys():
            full_path = self.path / file_path
            key_files[file_path] = full_path.exists()
        
        return key_files
    
    def _detect_project_type(self, structure: Dict[str, Any]) -> Dict[str, Any]:
        """Detect the main project type."""
        files = structure['files']
        
        # Django
        if files.get('manage.py') and files.get('settings.py'):
            structure['type'] = 'django'
        # Flask/FastAPI
        elif files.get('app.py') or files.get('main.py'):
            structure['type'] = 'python-web'
        # Next.js
        elif files.get('next.config.js') and files.get('package.json'):
            structure['type'] = 'nextjs'
        # Nuxt.js
        elif files.get('nuxt.config.js') and files.get('package.json'):
            structure['type'] = 'nuxtjs'
        # Angular
        elif files.get('angular.json'):
            structure['type'] = 'angular'
        # Vue
        elif files.get('vue.config.js') and files.get('package.json'):
            structure['type'] = 'vue'
        # React (Vite)
        elif files.get('vite.config.js') or files.get('vite.config.ts'):
            structure['type'] = 'vite-react'
        # React (Create React App)
        elif files.get('package.json') and self._check_react_app():
            structure['type'] = 'react'
        # Node.js
        elif files.get('package.json') and (files.get('server.js') or files.get('index.js')):
            structure['type'] = 'nodejs'
        # Python
        elif any(files.get(f) for f in ['requirements.txt', 'pyproject.toml', 'setup.py']):
            structure['type'] = 'python'
        # Docker-only
        elif files.get('Dockerfile') or files.get('docker-compose.yml'):
            structure['type'] = 'docker'
        
        return structure
    
    def _detect_technologies(self, structure: Dict[str, Any]) -> Dict[str, Any]:
        """Detect technologies used in the project."""
        files = structure['files']
        technologies = []
        
        # Backend technologies
        if any(files.get(f) for f in ['main.py', 'app.py', 'requirements.txt', 'pyproject.toml']):
            technologies.append('Python')
        
        if files.get('package.json'):
            technologies.append('Node.js')
        
        # Frontend technologies
        if self._check_react():
            technologies.append('React')
        
        if self._check_vue():
            technologies.append('Vue.js')
        
        if files.get('angular.json'):
            technologies.append('Angular')
        
        # Build tools
        if files.get('vite.config.js') or files.get('vite.config.ts'):
            technologies.append('Vite')
        
        if files.get('webpack.config.js'):
            technologies.append('Webpack')
        
        # Database technologies
        if files.get('prisma/schema.prisma'):
            technologies.append('Prisma')
        
        if files.get('alembic.ini'):
            technologies.append('Alembic')
        
        # Docker
        if files.get('Dockerfile') or files.get('docker-compose.yml'):
            technologies.append('Docker')
        
        structure['technologies'] = technologies
        return structure
    
    def _detect_components(self, structure: Dict[str, Any]) -> Dict[str, Any]:
        """Detect application components."""
        files = structure['files']
        components = {}
        
        # Backend components
        if files.get('main.py'):
            components['backend'] = {'type': 'python', 'entry': 'main.py'}
        elif files.get('app.py'):
            components['backend'] = {'type': 'python', 'entry': 'app.py'}
        elif files.get('server.js'):
            components['backend'] = {'type': 'nodejs', 'entry': 'server.js'}
        elif files.get('index.js') and not self._is_frontend_project():
            components['backend'] = {'type': 'nodejs', 'entry': 'index.js'}
        
        # Frontend components
        if self._is_frontend_project():
            if files.get('index.html'):
                components['frontend'] = {'type': 'web', 'entry': 'index.html'}
            elif files.get('package.json'):
                components['frontend'] = {'type': 'spa', 'entry': 'package.json'}
        
        structure['components'] = components
        return structure
    
    def _detect_database(self, structure: Dict[str, Any]) -> Dict[str, Any]:
        """Detect database configuration."""
        files = structure['files']
        
        # Check for database files and configs
        if files.get('prisma/schema.prisma'):
            structure['database'] = {'type': 'prisma', 'config': 'prisma/schema.prisma'}
        elif files.get('alembic.ini'):
            structure['database'] = {'type': 'alembic', 'config': 'alembic.ini'}
        elif files.get('models.py'):
            structure['database'] = {'type': 'orm', 'config': 'models.py'}
        elif files.get('schema.sql'):
            structure['database'] = {'type': 'sql', 'config': 'schema.sql'}
        elif self._check_sqlite():
            structure['database'] = {'type': 'sqlite', 'config': 'auto-detected'}
        
        return structure
    
    def _detect_docker(self, structure: Dict[str, Any]) -> Dict[str, Any]:
        """Detect Docker configuration."""
        files = structure['files']
        
        structure['docker'] = (
            files.get('Dockerfile') or 
            files.get('docker-compose.yml') or 
            files.get('docker-compose.yaml')
        )
        
        return structure
    
    def _detect_ci_cd(self, structure: Dict[str, Any]) -> Dict[str, Any]:
        """Detect CI/CD configuration."""
        files = structure['files']
        ci_cd = []
        
        if files.get('.github/workflows'):
            ci_cd.append('GitHub Actions')
        
        if files.get('.gitlab-ci.yml'):
            ci_cd.append('GitLab CI')
        
        if files.get('azure-pipelines.yml'):
            ci_cd.append('Azure Pipelines')
        
        if files.get('Jenkinsfile'):
            ci_cd.append('Jenkins')
        
        if files.get('.travis.yml'):
            ci_cd.append('Travis CI')
        
        structure['ci_cd'] = ci_cd
        return structure
    
    def _detect_package_managers(self, structure: Dict[str, Any]) -> Dict[str, Any]:
        """Detect package managers."""
        files = structure['files']
        package_managers = []
        
        # Python package managers
        if files.get('requirements.txt'):
            package_managers.append('pip')
        
        if files.get('pyproject.toml') or files.get('poetry.lock'):
            package_managers.append('poetry')
        
        if files.get('Pipfile'):
            package_managers.append('pipenv')
        
        # Node.js package managers
        if files.get('package-lock.json'):
            package_managers.append('npm')
        
        if files.get('yarn.lock'):
            package_managers.append('yarn')
        
        if files.get('pnpm-lock.yaml'):
            package_managers.append('pnpm')
        
        structure['package_managers'] = package_managers
        return structure
    
    def _check_react(self) -> bool:
        """Check if project uses React."""
        package_json = self.path / 'package.json'
        if package_json.exists():
            try:
                with open(package_json, 'r') as f:
                    data = json.load(f)
                    deps = {**data.get('dependencies', {}), **data.get('devDependencies', {})}
                    return 'react' in deps
            except:
                pass
        return False
    
    def _check_vue(self) -> bool:
        """Check if project uses Vue.js."""
        package_json = self.path / 'package.json'
        if package_json.exists():
            try:
                with open(package_json, 'r') as f:
                    data = json.load(f)
                    deps = {**data.get('dependencies', {}), **data.get('devDependencies', {})}
                    return 'vue' in deps
            except:
                pass
        return False
    
    def _check_react_app(self) -> bool:
        """Check if project is a Create React App."""
        package_json = self.path / 'package.json'
        if package_json.exists():
            try:
                with open(package_json, 'r') as f:
                    data = json.load(f)
                    deps = {**data.get('dependencies', {}), **data.get('devDependencies', {})}
                    return 'react-scripts' in deps
            except:
                pass
        return False
    
    def _is_frontend_project(self) -> bool:
        """Check if this is primarily a frontend project."""
        files = self.path.glob('*')
        frontend_indicators = [
            'src', 'public', 'assets', 'components', 'pages', 'views',
            'index.html', 'vite.config.js', 'webpack.config.js'
        ]
        
        return any(
            f.name in frontend_indicators 
            for f in files
        ) or self._check_react() or self._check_vue()
    
    def _check_sqlite(self) -> bool:
        """Check for SQLite database files."""
        sqlite_files = list(self.path.glob('*.db')) + list(self.path.glob('*.sqlite'))
        return len(sqlite_files) > 0