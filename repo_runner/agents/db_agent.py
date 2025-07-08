import subprocess
import json
import os
from pathlib import Path
from ..llm.llm_utils import generate_code_with_llm
from .base_agent import BaseAgent

class DBAgent(BaseAgent):
    def setup(self, structure):
        """Detect and set up the database using LLM."""
        files = structure.get('files', {})
        
        db_results = {
            'db_type': None,
            'schema_generated': False,
            'migrations_run': False,
            'connection_tested': False,
            'errors': [],
            'warnings': []
        }
        
        # Detect database type
        db_type = self._detect_database_type(structure)
        db_results['db_type'] = db_type
        
        if db_type == 'none':
            db_results['warnings'].append('No database detected')
            return db_results
        
        # Generate schema if needed
        if self._needs_schema_generation(structure, db_type):
            schema_result = self._generate_schema(structure, db_type)
            db_results.update(schema_result)
        
        # Run migrations if available
        if self._has_migrations(structure, db_type):
            migration_result = self._run_migrations(structure, db_type)
            db_results.update(migration_result)
        
        # Test database connection
        connection_result = self._test_connection(structure, db_type)
        db_results.update(connection_result)
        
        return db_results
    
    def _detect_database_type(self, structure):
        """Detect database type using LLM analysis."""
        files = structure.get('files', {})
        
        prompt = f"""
        Analyze this project structure and determine the database type:
        
        Files: {list(files.keys())}
        Technologies: {structure.get('technologies', [])}
        
        Common database indicators:
        - SQLite: .db, .sqlite files
        - PostgreSQL: postgres, psql, pg_* files
        - MySQL: mysql, .sql files
        - MongoDB: mongo, .bson files
        - Redis: redis, .rdb files
        
        Return only the database type: sqlite, postgresql, mysql, mongodb, redis, or none
        """
        
        db_type = generate_code_with_llm(prompt, agent_name='db_agent').strip().lower()
        
        # Validate the response
        valid_types = ['sqlite', 'postgresql', 'mysql', 'mongodb', 'redis', 'none']
        return db_type if db_type in valid_types else 'none'
    
    def _needs_schema_generation(self, structure, db_type):
        """Check if schema generation is needed."""
        if db_type == 'none':
            return False
        
        files = structure.get('files', {})
        
        # Check for existing schema files
        schema_indicators = {
            'sqlite': ['schema.sql', '*.db'],
            'postgresql': ['schema.sql', 'migrations/'],
            'mysql': ['schema.sql', 'migrations/'],
            'mongodb': ['schema.js', 'models/'],
            'redis': ['redis.conf']
        }
        
        indicators = schema_indicators.get(db_type, [])
        return not any(indicator in str(files.keys()) for indicator in indicators)
    
    def _generate_schema(self, structure, db_type):
        """Generate database schema using LLM."""
        try:
            prompt = f"""
            Generate a database schema for this project:
            
            Database type: {db_type}
            Project structure: {json.dumps(structure, indent=2)}
            
            Create a complete schema that includes:
            - All necessary tables/collections
            - Proper relationships
            - Indexes for performance
            - Constraints and validations
            
            Return only the schema definition (SQL for SQL databases, JSON for NoSQL).
            """
            
            schema_content = generate_code_with_llm(prompt, agent_name='db_agent')
            
            # Save schema file
            schema_file = f"schema.{'sql' if db_type in ['sqlite', 'postgresql', 'mysql'] else 'js'}"
            Path(schema_file).write_text(schema_content)
            
            return {
                'schema_generated': True,
                'schema_file': schema_file,
                'schema_content': schema_content
            }
            
        except Exception as e:
            return {
                'errors': [f"Schema generation failed: {e}"],
                'schema_generated': False
            }
    
    def _has_migrations(self, structure, db_type):
        """Check if migration files exist."""
        files = structure.get('files', {})
        
        migration_indicators = [
            'migrations/', 'alembic/', 'migrate/', 
            '*.sql', 'migration_*.py', 'db_migrate'
        ]
        
        return any(indicator in str(files.keys()) for indicator in migration_indicators)
    
    def _run_migrations(self, structure, db_type):
        """Run database migrations using LLM guidance."""
        try:
            prompt = f"""
            Analyze this project and suggest migration commands:
            
            Database type: {db_type}
            Project structure: {json.dumps(structure, indent=2)}
            
            Common migration commands:
            - SQLite: No migrations needed
            - PostgreSQL: psql -d dbname -f schema.sql
            - MySQL: mysql -u user -p dbname < schema.sql
            - MongoDB: mongo dbname schema.js
            - Alembic: alembic upgrade head
            - Django: python manage.py migrate
            - Flask-Migrate: flask db upgrade
            
            Return only the recommended migration command.
            """
            
            migration_cmd = generate_code_with_llm(prompt, agent_name='db_agent')
            
            if migration_cmd.strip() and migration_cmd.strip() != 'none':
                result = subprocess.run(
                    migration_cmd.split(),
                    capture_output=True,
                    text=True,
                    cwd=os.getcwd()
                )
                
                if result.returncode == 0:
                    return {
                        'migrations_run': True,
                        'migration_command': migration_cmd
                    }
                else:
                    return {
                        'errors': [f"Migration failed: {result.stderr}"],
                        'migration_command': migration_cmd
                    }
            else:
                return {
                    'migrations_run': False,
                    'warnings': ['No migrations needed or available']
                }
                
        except Exception as e:
            return {
                'errors': [f"Migration error: {e}"],
                'migrations_run': False
            }
    
    def _test_connection(self, structure, db_type):
        """Test database connection using LLM guidance."""
        try:
            prompt = f"""
            Suggest a database connection test for {db_type}:
            
            Project structure: {json.dumps(structure, indent=2)}
            
            Common test commands:
            - SQLite: sqlite3 database.db ".tables"
            - PostgreSQL: psql -h localhost -U user -d dbname -c "SELECT 1"
            - MySQL: mysql -h localhost -u user -p -e "SELECT 1"
            - MongoDB: mongo --eval "db.runCommand('ping')"
            - Redis: redis-cli ping
            
            Return only the test command.
            """
            
            test_cmd = generate_code_with_llm(prompt, agent_name='db_agent')
            
            if test_cmd.strip() and test_cmd.strip() != 'none':
                result = subprocess.run(
                    test_cmd.split(),
                    capture_output=True,
                    text=True,
                    cwd=os.getcwd()
                )
                
                if result.returncode == 0:
                    return {
                        'connection_tested': True,
                        'connection_status': 'success',
                        'test_command': test_cmd
                    }
                else:
                    return {
                        'connection_tested': True,
                        'connection_status': 'failed',
                        'test_command': test_cmd,
                        'errors': [f"Connection test failed: {result.stderr}"]
                    }
            else:
                return {
                    'connection_tested': False,
                    'warnings': ['No connection test available']
                }
                
        except Exception as e:
            return {
                'errors': [f"Connection test error: {e}"],
                'connection_tested': False
            } 

    def checkpoint(self, state: dict, checkpoint_file: str = "db_agent_state.json"):
        """
        Save the DBAgent's state to a checkpoint file (default: db_agent_state.json).
        Logs the checkpoint event.
        """
        import json
        self.log(f"Checkpointing DBAgent state to {checkpoint_file}", "info")
        try:
            with open(checkpoint_file, "w") as f:
                json.dump(state, f, indent=2)
            self.log(f"Checkpoint saved to {checkpoint_file}", "info")
        except Exception as e:
            self.log(f"Failed to save checkpoint: {e}", "error")

    def report_error(self, error, context=None, error_file="db_agent_errors.json"):
        """
        Log the error and optionally save it to a file for traceability.
        """
        import json
        self.log(f"Error reported: {error} | Context: {context}", "error")
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
            self.log(f"Failed to save error report: {e}", "error") 