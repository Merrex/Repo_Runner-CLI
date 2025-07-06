"""
Documentation update functionality.
"""

import os
import re
from pathlib import Path
from typing import Dict, Any, Optional
from .logger import get_logger


class DocumentationUpdater:
    """Updates project documentation with setup and run instructions."""
    
    def __init__(self, path: Path, config: Dict = None, dry_run: bool = False):
        self.path = path
        self.config = config or {}
        self.dry_run = dry_run
        self.logger = get_logger()
    
    def update(self, structure: Dict[str, Any], services: Dict[str, Any] = None):
        """Update project documentation."""
        self._update_readme(structure, services)
        self._create_setup_docs(structure)
        self._update_env_example(structure)
    
    def _update_readme(self, structure: Dict[str, Any], services: Dict[str, Any] = None):
        """Update README.md with setup and run instructions."""
        readme_path = self.path / 'README.md'
        
        if readme_path.exists():
            content = readme_path.read_text()
        else:
            content = f"# {self.path.name}\n\nProject automatically detected and configured by repo_runner.\n\n"
        
        # Generate setup section
        setup_section = self._generate_setup_section(structure)
        
        # Generate run section
        run_section = self._generate_run_section(structure, services)
        
        # Generate project info section
        project_info = self._generate_project_info(structure)
        
        # Insert or update sections
        content = self._update_section(content, "Project Information", project_info)
        content = self._update_section(content, "Setup", setup_section)
        content = self._update_section(content, "Running the Application", run_section)
        
        if not self.dry_run:
            readme_path.write_text(content)
            self.logger.info("✅ README.md updated")
    
    def _generate_project_info(self, structure: Dict[str, Any]) -> str:
        """Generate project information section."""
        info = []
        
        project_type = structure.get('type', 'unknown')
        info.append(f"**Project Type**: {project_type.title()}")
        
        technologies = structure.get('technologies', [])
        if technologies:
            info.append(f"**Technologies**: {', '.join(technologies)}")
        
        components = structure.get('components', {})
        if components:
            info.append("**Components**:")
            for component, details in components.items():
                info.append(f"- {component.title()}: {details.get('type', 'detected')}")
        
        database = structure.get('database')
        if database:
            info.append(f"**Database**: {database.get('type', 'unknown').title()}")
        
        package_managers = structure.get('package_managers', [])
        if package_managers:
            info.append(f"**Package Managers**: {', '.join(package_managers)}")
        
        return "\n".join(info)
    
    def _generate_setup_section(self, structure: Dict[str, Any]) -> str:
        """Generate setup instructions section."""
        setup = ["## Prerequisites\n"]
        
        technologies = structure.get('technologies', [])
        package_managers = structure.get('package_managers', [])
        
        # Prerequisites
        if 'Python' in technologies:
            setup.append("- Python 3.8+ installed")
        if 'Node.js' in technologies:
            setup.append("- Node.js 14+ installed")
        if 'Docker' in technologies:
            setup.append("- Docker and Docker Compose installed")
        
        setup.append("\n## Installation\n")
        
        # Automatic setup
        setup.append("### Automatic Setup (Recommended)\n")
        setup.append("```bash")
        setup.append("# Install repo_runner")
        setup.append("pip install repo_runner")
        setup.append("")
        setup.append("# Run automatic setup")
        setup.append("repo_runner setup")
        setup.append("```\n")
        
        # Manual setup
        setup.append("### Manual Setup\n")
        
        # Environment setup
        setup.append("1. **Environment Setup**")
        setup.append("```bash")
        setup.append("cp .env.example .env")
        setup.append("# Edit .env file with your configuration")
        setup.append("```\n")
        
        # Dependencies
        setup.append("2. **Install Dependencies**")
        
        if 'pip' in package_managers:
            setup.append("```bash")
            setup.append("pip install -r requirements.txt")
            setup.append("```")
        
        if 'poetry' in package_managers:
            setup.append("```bash")
            setup.append("poetry install")
            setup.append("```")
        
        if 'npm' in package_managers:
            setup.append("```bash")
            setup.append("npm install")
            setup.append("```")
        
        if 'yarn' in package_managers:
            setup.append("```bash")
            setup.append("yarn install")
            setup.append("```")
        
        # Database setup
        database = structure.get('database')
        if database:
            setup.append("\n3. **Database Setup**")
            db_type = database.get('type', 'unknown')
            
            if db_type == 'django':
                setup.append("```bash")
                setup.append("python manage.py migrate")
                setup.append("python manage.py createsuperuser")
                setup.append("```")
            elif db_type == 'alembic':
                setup.append("```bash")
                setup.append("alembic upgrade head")
                setup.append("```")
            elif db_type == 'prisma':
                setup.append("```bash")
                setup.append("npx prisma generate")
                setup.append("npx prisma db push")
                setup.append("```")
        
        return "\n".join(setup)
    
    def _generate_run_section(self, structure: Dict[str, Any], services: Dict[str, Any] = None) -> str:
        """Generate run instructions section."""
        run = []
        
        # Automatic run
        run.append("### Automatic Run (Recommended)\n")
        run.append("```bash")
        run.append("# Run the complete workflow")
        run.append("repo_runner full")
        run.append("")
        run.append("# Or run individual steps")
        run.append("repo_runner setup")
        run.append("repo_runner run")
        run.append("```\n")
        
        # Manual run
        run.append("### Manual Run\n")
        
        project_type = structure.get('type', 'unknown')
        
        if project_type == 'django':
            run.append("```bash")
            run.append("python manage.py runserver")
            run.append("```")
        elif project_type == 'python-web':
            run.append("```bash")
            run.append("python main.py")
            run.append("# or")
            run.append("python app.py")
            run.append("```")
        elif project_type in ['nodejs', 'react', 'vue', 'angular']:
            run.append("```bash")
            run.append("npm start")
            run.append("# or")
            run.append("npm run dev")
            run.append("```")
        elif project_type == 'nextjs':
            run.append("```bash")
            run.append("npm run dev")
            run.append("```")
        elif project_type == 'nuxtjs':
            run.append("```bash")
            run.append("npm run dev")
            run.append("```")
        
        # Docker run
        if structure.get('docker'):
            run.append("\n### Docker Run\n")
            if (self.path / 'docker-compose.yml').exists():
                run.append("```bash")
                run.append("docker-compose up --build")
                run.append("```")
            else:
                run.append("```bash")
                run.append("docker build -t app .")
                run.append("docker run -p 8000:8000 app")
                run.append("```")
        
        # Service URLs
        if services:
            run.append("\n### Service URLs\n")
            for service_name, service_info in services.items():
                url = service_info.get('url')
                if url:
                    run.append(f"- **{service_name.title()}**: {url}")
        
        return "\n".join(run)
    
    def _update_section(self, content: str, section_title: str, section_content: str) -> str:
        """Update or insert a section in the content."""
        section_pattern = rf"(^|\n)## {re.escape(section_title)}\n.*?(?=\n## |\n# |$)"
        
        new_section = f"\n## {section_title}\n\n{section_content}\n"
        
        if re.search(section_pattern, content, re.DOTALL):
            # Replace existing section
            return re.sub(section_pattern, new_section, content, flags=re.DOTALL)
        else:
            # Append new section
            return content + new_section
    
    def _create_setup_docs(self, structure: Dict[str, Any]):
        """Create additional setup documentation."""
        docs_dir = self.path / 'docs'
        
        if not docs_dir.exists() and not self.dry_run:
            docs_dir.mkdir()
        
        # Create SETUP.md
        setup_content = f"""# Setup Guide

This document provides detailed setup instructions for this {structure.get('type', 'unknown')} project.

## Generated by repo_runner

This project was automatically configured by repo_runner. For the most up-to-date setup instructions, run:

```bash
repo_runner docs
```

## Quick Start

1. Install dependencies:
```bash
repo_runner setup
```

2. Run the application:
```bash
repo_runner run
```

## Manual Setup

If you prefer manual setup, follow the instructions in the README.md file.

## Troubleshooting

### Common Issues

1. **Dependencies not installing**: Make sure you have the required package managers installed
2. **Database connection issues**: Check your .env file configuration
3. **Port conflicts**: Use the --port flag to specify a different port

### Getting Help

Run `repo_runner --help` for more information about available commands.
"""
        
        if not self.dry_run:
            (docs_dir / 'SETUP.md').write_text(setup_content)
            self.logger.info("✅ SETUP.md created")
    
    def _update_env_example(self, structure: Dict[str, Any]):
        """Update .env.example file."""
        env_example_path = self.path / '.env.example'
        
        if env_example_path.exists():
            return  # Don't overwrite existing .env.example
        
        # Create basic .env.example
        env_content = """# Environment Configuration
# Copy this file to .env and update with your values

# Application
NODE_ENV=development
PORT=3000
HOST=localhost

# Database
DATABASE_URL=sqlite:///./app.db

# Security
SECRET_KEY=your-secret-key-here
JWT_SECRET=your-jwt-secret-here

# External APIs
# API_KEY=your-api-key-here
"""
        
        if not self.dry_run:
            env_example_path.write_text(env_content)
            self.logger.info("✅ .env.example created")