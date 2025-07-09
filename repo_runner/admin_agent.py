"""
Admin Agent - The CEO of the Repo Runner System

The Admin Agent is the highest-level controller that manages all orchestrators and managers.
Only accessible by the Developer (user), it provides system-wide control and intervention capabilities.
"""

import os
import json
import time
from typing import Dict, Any, List, Optional
from pathlib import Path

from .agents.base_agent import BaseAgent
from .managers.orchestrator import OrchestratorAgent
from .user_management import UserManager, UserTier
from .config_manager import ConfigManager
from .logger import get_logger


class AdminAgent(BaseAgent):
    """
    Admin Agent - The CEO of the Repo Runner System
    
    Responsibilities:
    - Manage all orchestrators and managers
    - Create new agents/managers as needed
    - Handle system-wide checkpoints
    - Intervene when orchestrators fail
    - Create custom business orchestrators
    - Provide system-wide control and monitoring
    """
    
    def __init__(self, config=None):
        super().__init__(config=config)
        self.agent_name = "AdminAgent"
        self.logger = get_logger()
        self.orchestrators = {}
        self.managers = {}
        self.system_status = {}
        self.checkpoint_file = "admin_agent_state.json"
        
        # Load existing state
        self.load_state()
    
    def run(self, *args, **kwargs):
        """Main admin agent workflow."""
        try:
            action = kwargs.get('action', 'status')
            
            if action == 'status':
                return self.get_system_status()
            elif action == 'create_orchestrator':
                return self.create_orchestrator(kwargs.get('name'), kwargs.get('config'))
            elif action == 'intervene':
                return self.intervene(kwargs.get('orchestrator_id'), kwargs.get('issue'))
            elif action == 'checkpoint':
                return self.create_system_checkpoint()
            elif action == 'restore':
                return self.restore_from_checkpoint(kwargs.get('checkpoint_id'))
            else:
                return {
                    "status": "error",
                    "agent": self.agent_name,
                    "error": f"Unknown action: {action}"
                }
                
        except Exception as e:
            error_result = {
                "status": "error",
                "agent": self.agent_name,
                "error": str(e)
            }
            self.report_error(e)
            return error_result
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status."""
        status = {
            "admin_agent": {
                "status": "active",
                "orchestrators_count": len(self.orchestrators),
                "managers_count": len(self.managers),
                "last_checkpoint": self.system_status.get('last_checkpoint'),
                "uptime": time.time() - self.system_status.get('start_time', time.time())
            },
            "orchestrators": {},
            "managers": {},
            "system_health": "healthy"
        }
        
        # Check orchestrator status
        for name, orchestrator in self.orchestrators.items():
            try:
                orchestrator_status = orchestrator.get_status()
                status["orchestrators"][name] = orchestrator_status
            except Exception as e:
                status["orchestrators"][name] = {"status": "error", "error": str(e)}
        
        # Check manager status
        for name, manager in self.managers.items():
            try:
                manager_status = manager.get_status()
                status["managers"][name] = manager_status
            except Exception as e:
                status["managers"][name] = {"status": "error", "error": str(e)}
        
        # Update system health
        healthy_orchestrators = sum(1 for o in status["orchestrators"].values() 
                                  if o.get("status") == "healthy")
        total_orchestrators = len(status["orchestrators"])
        
        if total_orchestrators == 0:
            status["system_health"] = "no_orchestrators"
        elif healthy_orchestrators == total_orchestrators:
            status["system_health"] = "healthy"
        else:
            status["system_health"] = "degraded"
        
        return status
    
    def create_orchestrator(self, name: str, config: Dict[str, Any] = None) -> Dict[str, Any]:
        """Create a new orchestrator instance."""
        try:
            if name in self.orchestrators:
                return {
                    "status": "error",
                    "error": f"Orchestrator '{name}' already exists"
                }
            
            # Create new orchestrator
            orchestrator = OrchestratorAgent(config=config)
            self.orchestrators[name] = orchestrator
            
            # Create checkpoint for new orchestrator
            self.create_system_checkpoint()
            
            self.logger.info(f"✅ Created orchestrator: {name}")
            
            return {
                "status": "success",
                "orchestrator_name": name,
                "message": f"Orchestrator '{name}' created successfully"
            }
            
        except Exception as e:
            self.logger.error(f"❌ Failed to create orchestrator '{name}': {e}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    def intervene(self, orchestrator_id: str, issue: str) -> Dict[str, Any]:
        """Intervene when an orchestrator fails or needs assistance."""
        try:
            if orchestrator_id not in self.orchestrators:
                return {
                    "status": "error",
                    "error": f"Orchestrator '{orchestrator_id}' not found"
                }
            
            orchestrator = self.orchestrators[orchestrator_id]
            
            # Analyze the issue and take action
            intervention_result = self._analyze_and_intervene(orchestrator, issue)
            
            # Create checkpoint after intervention
            self.create_system_checkpoint()
            
            self.logger.info(f"✅ Intervention completed for orchestrator: {orchestrator_id}")
            
            return {
                "status": "success",
                "intervention": intervention_result,
                "orchestrator_id": orchestrator_id
            }
            
        except Exception as e:
            self.logger.error(f"❌ Intervention failed for orchestrator '{orchestrator_id}': {e}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    def _analyze_and_intervene(self, orchestrator: OrchestratorAgent, issue: str) -> Dict[str, Any]:
        """Analyze issue and perform appropriate intervention."""
        intervention = {
            "issue": issue,
            "actions_taken": [],
            "status": "intervened"
        }
        
        # Analyze issue type and take appropriate action
        if "timeout" in issue.lower():
            intervention["actions_taken"].append("restart_orchestrator")
            # Restart orchestrator
            orchestrator.restart()
            
        elif "error" in issue.lower():
            intervention["actions_taken"].append("error_recovery")
            # Attempt error recovery
            orchestrator.recover_from_error()
            
        elif "resource" in issue.lower():
            intervention["actions_taken"].append("resource_optimization")
            # Optimize resource usage
            orchestrator.optimize_resources()
            
        else:
            intervention["actions_taken"].append("general_intervention")
            # General intervention
            orchestrator.force_restart()
        
        return intervention
    
    def create_system_checkpoint(self) -> Dict[str, Any]:
        """Create a system-wide checkpoint."""
        try:
            checkpoint_data = {
                "timestamp": time.time(),
                "admin_agent_status": self.get_system_status(),
                "orchestrators": {},
                "managers": {},
                "checkpoint_id": f"checkpoint_{int(time.time())}"
            }
            
            # Save orchestrator states
            for name, orchestrator in self.orchestrators.items():
                try:
                    checkpoint_data["orchestrators"][name] = orchestrator.get_state()
                except Exception as e:
                    checkpoint_data["orchestrators"][name] = {"error": str(e)}
            
            # Save manager states
            for name, manager in self.managers.items():
                try:
                    checkpoint_data["managers"][name] = manager.get_state()
                except Exception as e:
                    checkpoint_data["managers"][name] = {"error": str(e)}
            
            # Save checkpoint
            with open(self.checkpoint_file, 'w') as f:
                json.dump(checkpoint_data, f, indent=2)
            
            self.system_status['last_checkpoint'] = checkpoint_data['checkpoint_id']
            self.save_state()
            
            self.logger.info(f"✅ System checkpoint created: {checkpoint_data['checkpoint_id']}")
            
            return {
                "status": "success",
                "checkpoint_id": checkpoint_data['checkpoint_id'],
                "timestamp": checkpoint_data['timestamp']
            }
            
        except Exception as e:
            self.logger.error(f"❌ Failed to create system checkpoint: {e}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    def restore_from_checkpoint(self, checkpoint_id: str) -> Dict[str, Any]:
        """Restore system from a checkpoint."""
        try:
            if not os.path.exists(self.checkpoint_file):
                return {
                    "status": "error",
                    "error": "No checkpoint file found"
                }
            
            with open(self.checkpoint_file, 'r') as f:
                checkpoint_data = json.load(f)
            
            if checkpoint_data.get('checkpoint_id') != checkpoint_id:
                return {
                    "status": "error",
                    "error": f"Checkpoint ID mismatch: expected {checkpoint_id}"
                }
            
            # Restore orchestrator states
            for name, state in checkpoint_data.get('orchestrators', {}).items():
                if name in self.orchestrators:
                    try:
                        self.orchestrators[name].restore_state(state)
                    except Exception as e:
                        self.logger.warning(f"Failed to restore orchestrator {name}: {e}")
            
            # Restore manager states
            for name, state in checkpoint_data.get('managers', {}).items():
                if name in self.managers:
                    try:
                        self.managers[name].restore_state(state)
                    except Exception as e:
                        self.logger.warning(f"Failed to restore manager {name}: {e}")
            
            self.logger.info(f"✅ System restored from checkpoint: {checkpoint_id}")
            
            return {
                "status": "success",
                "checkpoint_id": checkpoint_id,
                "restored_components": len(checkpoint_data.get('orchestrators', {})) + len(checkpoint_data.get('managers', {}))
            }
            
        except Exception as e:
            self.logger.error(f"❌ Failed to restore from checkpoint: {e}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    def create_custom_orchestrator(self, name: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """Create a custom business orchestrator with specific configuration."""
        try:
            # Validate configuration
            required_fields = ['business_logic', 'agents', 'workflow']
            for field in required_fields:
                if field not in config:
                    return {
                        "status": "error",
                        "error": f"Missing required field: {field}"
                    }
            
            # Create custom orchestrator
            custom_config = {
                'name': name,
                'business_logic': config['business_logic'],
                'agents': config['agents'],
                'workflow': config['workflow'],
                'custom': True
            }
            
            orchestrator = OrchestratorAgent(config=custom_config)
            self.orchestrators[name] = orchestrator
            
            # Create checkpoint
            self.create_system_checkpoint()
            
            self.logger.info(f"✅ Created custom orchestrator: {name}")
            
            return {
                "status": "success",
                "orchestrator_name": name,
                "config": custom_config
            }
            
        except Exception as e:
            self.logger.error(f"❌ Failed to create custom orchestrator '{name}': {e}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    def get_orchestrator(self, name: str) -> Optional[OrchestratorAgent]:
        """Get an orchestrator by name."""
        return self.orchestrators.get(name)
    
    def list_orchestrators(self) -> List[str]:
        """List all orchestrator names."""
        return list(self.orchestrators.keys())
    
    def remove_orchestrator(self, name: str) -> Dict[str, Any]:
        """Remove an orchestrator."""
        try:
            if name not in self.orchestrators:
                return {
                    "status": "error",
                    "error": f"Orchestrator '{name}' not found"
                }
            
            # Stop orchestrator if running
            orchestrator = self.orchestrators[name]
            try:
                orchestrator.stop()
            except Exception as e:
                self.logger.warning(f"Failed to stop orchestrator {name}: {e}")
            
            # Remove from list
            del self.orchestrators[name]
            
            # Create checkpoint
            self.create_system_checkpoint()
            
            self.logger.info(f"✅ Removed orchestrator: {name}")
            
            return {
                "status": "success",
                "orchestrator_name": name
            }
            
        except Exception as e:
            self.logger.error(f"❌ Failed to remove orchestrator '{name}': {e}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    def load_state(self):
        """Load admin agent state from file."""
        try:
            if os.path.exists(self.checkpoint_file):
                with open(self.checkpoint_file, 'r') as f:
                    state = json.load(f)
                    self.system_status = state.get('admin_agent_status', {})
        except Exception as e:
            self.logger.warning(f"Failed to load admin agent state: {e}")
            self.system_status = {'start_time': time.time()}
    
    def save_state(self):
        """Save admin agent state to file."""
        try:
            state = {
                'admin_agent_status': self.system_status,
                'timestamp': time.time()
            }
            with open(self.checkpoint_file, 'w') as f:
                json.dump(state, f, indent=2)
        except Exception as e:
            self.logger.error(f"Failed to save admin agent state: {e}")
    
    def checkpoint(self, state: dict, checkpoint_file: str = "admin_agent_state.json"):
        """Save admin agent checkpoint."""
        self.logger.info(f"Checkpointing Admin Agent state to {checkpoint_file}")
        try:
            with open(checkpoint_file, "w") as f:
                json.dump(state, f, indent=2)
            self.logger.info(f"Checkpoint saved to {checkpoint_file}")
        except Exception as e:
            self.logger.error(f"Failed to save checkpoint: {e}")
    
    def report_error(self, error, context=None, error_file="admin_agent_errors.json"):
        """Log admin agent error."""
        self.logger.error(f"Admin Agent error: {error} | Context: {context}")
        try:
            error_record = {"error": str(error), "context": context, "timestamp": time.time()}
            if not os.path.exists(error_file):
                with open(error_file, "w") as f:
                    json.dump([error_record], f, indent=2)
            else:
                with open(error_file, "r+") as f:
                    errors = json.load(f)
                    errors.append(error_record)
                    f.seek(0)
                    json.dump(errors, f, indent=2) 