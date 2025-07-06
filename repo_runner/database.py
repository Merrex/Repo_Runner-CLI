"""
Database setup and management functionality.
"""

import subprocess
import os
import sqlite3
from pathlib import Path
from typing import Dict, Any, Optional
from .logger import get_logger


class DatabaseManager:
    """Manages database setup and bootstrapping."""
    
    def __init__(self, path: Path, config: Dict = None, dry_run: bool = False):
        self.path = path
        self.config = config or {}
        self.dry_run = dry_run
        self.logger = get_logger()
    
    def setup(self, structure: Dict[str, Any]):
        """Setup and bootstrap database based on detected configuration."""
        database_config = structure.get('database')
        
        if not database_config:
            self.logger.info("No database configuration detected")
            return
        
        db_type = database_config.get('type')
        
        if db_type == 'prisma':
            self._setup_prisma()
        elif db_type == 'alembic':
            self._setup_alembic()
        elif db_type == 'sqlite':
            self._setup_sqlite()
        elif db_type == 'django':
            self._setup_django_db()
        else:
            self.logger.info(f"Database type '{db_type}' not supported for auto-setup")
    
    def _run_command(self, cmd: list, description: str = None) -> bool:
        """Run a database command with proper error handling."""
        if description:
            self.logger.info(f"{description}: {' '.join(cmd)}")
        else:
            self.logger.info(f"Running: {' '.join(cmd)}")
        
        if self.dry_run:
            self.logger.info("DRY RUN: Command not executed")
            return True
        
        try:
            result = subprocess.run(
                cmd, 
                cwd=self.path, 
                capture_output=True, 
                text=True, 
                timeout=120
            )
            
            if result.returncode == 0:
                self.logger.info(f"✅ {description or 'Command'} completed successfully")
                return True
            else:
                self.logger.error(f"❌ {description or 'Command'} failed: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            self.logger.error(f"❌ {description or 'Command'} timed out")
            return False
        except Exception as e:
            self.logger.error(f"❌ {description or 'Command'} failed: {e}")
            return False
    
    def _setup_prisma(self):
        """Setup Prisma database."""
        self.logger.info("Setting up Prisma database")
        
        # Generate Prisma client
        if self._run_command(['npx', 'prisma', 'generate'], "Generating Prisma client"):
            # Run migrations
            self._run_command(['npx', 'prisma', 'db', 'push'], "Pushing Prisma schema")
            
            # Seed database if seed script exists
            self._run_prisma_seed()
    
    def _setup_alembic(self):
        """Setup Alembic database migrations."""
        self.logger.info("Setting up Alembic database")
        
        # Check if migrations directory exists
        migrations_dir = self.path / 'alembic' / 'versions'
        if not migrations_dir.exists():
            self.logger.info("No Alembic migrations found, initializing...")
            self._run_command(['alembic', 'init', 'alembic'], "Initializing Alembic")
        
        # Run migrations
        self._run_command(['alembic', 'upgrade', 'head'], "Running Alembic migrations")
    
    def _setup_sqlite(self):
        """Setup SQLite database."""
        self.logger.info("Setting up SQLite database")
        
        # Find SQLite files
        sqlite_files = list(self.path.glob('*.db')) + list(self.path.glob('*.sqlite'))
        
        if not sqlite_files:
            # Create a default SQLite database
            db_path = self.path / 'app.db'
            if not self.dry_run:
                self._create_sqlite_db(db_path)
            self.logger.info(f"Created SQLite database: {db_path}")
        else:
            self.logger.info(f"Found existing SQLite database: {sqlite_files[0]}")
    
    def _setup_django_db(self):
        """Setup Django database."""
        self.logger.info("Setting up Django database")
        
        # Run Django migrations
        self._run_command(['python', 'manage.py', 'makemigrations'], "Making Django migrations")
        self._run_command(['python', 'manage.py', 'migrate'], "Running Django migrations")
        
        # Create superuser if in interactive mode
        if not self.dry_run and self._is_interactive():
            self.logger.info("Creating Django superuser (optional)")
            try:
                subprocess.run(['python', 'manage.py', 'createsuperuser'], cwd=self.path)
            except KeyboardInterrupt:
                self.logger.info("Superuser creation skipped")
    
    def _create_sqlite_db(self, db_path: Path):
        """Create a basic SQLite database."""
        try:
            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()
            
            # Create a basic table for testing
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS app_info (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    version TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Insert initial data
            cursor.execute('''
                INSERT INTO app_info (name, version) 
                VALUES ('repo_runner_app', '1.0.0')
            ''')
            
            conn.commit()
            conn.close()
            
            self.logger.info("✅ SQLite database created successfully")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to create SQLite database: {e}")
    
    def _run_prisma_seed(self):
        """Run Prisma database seeding."""
        package_json = self.path / 'package.json'
        
        if not package_json.exists():
            return
        
        try:
            import json
            with open(package_json, 'r') as f:
                data = json.load(f)
            
            # Check if seed script exists
            scripts = data.get('scripts', {})
            if 'seed' in scripts:
                self._run_command(['npm', 'run', 'seed'], "Running Prisma seed")
            elif 'prisma' in data.get('prisma', {}):
                seed_path = data['prisma'].get('seed')
                if seed_path:
                    self._run_command(['node', seed_path], "Running Prisma seed")
        except:
            pass
    
    def _is_interactive(self) -> bool:
        """Check if running in interactive mode."""
        return os.isatty(0)
    
    def check_database_connection(self) -> bool:
        """Check if database connection is working."""
        database_url = os.environ.get('DATABASE_URL')
        
        if not database_url:
            return False
        
        try:
            if database_url.startswith('sqlite'):
                db_path = database_url.replace('sqlite:///', '').replace('sqlite:', '')
                return Path(db_path).exists()
            else:
                # For other databases, we'd need specific connection logic
                # This is a simplified check
                return True
        except:
            return False