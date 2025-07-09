import os
import json
import time
from typing import Dict, List, Any, Optional
from .base_agent import BaseAgent
from ..managers.base_manager import BaseManager
from ..user_management import UserManager, UserTier

class AdminAgent(BaseAgent):
    """
    Admin Agent - CEO of the agentic system.
    
    Responsibilities:
    1. **System Control**: Controls all orchestrators and managers
    2. **Agent Creation**: Creates new agents and managers when needed
    3. **Checkpoint Management**: Handles checkpoints only when new agents need creation
    4. **Failure Recovery**: Intervenes when orchestrators fail to report success
    5. **Developer Access**: Only accessible by users with 'developer' role
    6. **Business Orchestrator Creation**: Creates custom orchestrators for business clients
    
    Access Control:
    - Only users with 'developer' role can access Admin Agent
    - Admin users cannot access Admin Agent (they can only manage users)
    - Developer role is separate from admin role
    """
    
    def __init__(self, config=None):
        super().__init__(config=config)
        self.user_manager = UserManager()
        self.created_agents = {}
        self.created_managers = {}
        self.business_orchestrators = {}
        self.checkpoint_file = "admin_agent_state.json"
        
    def run(self, *args, **kwargs):
        """Run admin agent operations"""
        # Check if current user has developer access
        if not self._check_developer_access():
            return {
                'status': 'error',
                'error': 'Access denied. Only users with developer role can access Admin Agent.'
            }
        
        operation = kwargs.get('operation', 'status')
        
        if operation == 'create_agent':
            return self._create_new_agent(kwargs.get('agent_type'), kwargs.get('config'))
        elif operation == 'create_manager':
            return self._create_new_manager(kwargs.get('manager_type'), kwargs.get('config'))
        elif operation == 'create_business_orchestrator':
            return self._create_business_orchestrator(kwargs.get('business_name'), kwargs.get('config'))
        elif operation == 'intervene':
            return self._intervene_orchestrator_failure(kwargs.get('orchestrator_id'), kwargs.get('issue'))
        elif operation == 'status':
            return self._get_system_status()
        else:
            return {
                'status': 'error',
                'error': f'Unknown operation: {operation}'
            }
    
    def _check_developer_access(self) -> bool:
        """Check if current user has developer role access"""
        if not self.user_manager.current_user:
            return False
        
        user = self.user_manager.users.get(self.user_manager.current_user)
        if not user:
            return False
        
        # Only developer role can access Admin Agent
        return user.get('tier') == 'developer'
    
    def _create_new_agent(self, agent_type: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new agent dynamically"""
        try:
            # Define agent templates
            agent_templates = {
                'custom_detection': {
                    'class_name': 'CustomDetectionAgent',
                    'base_class': 'BaseAgent',
                    'capabilities': ['custom_detection', 'specialized_analysis'],
                    'model_requirements': ['gpt-4', 'claude-3'],
                    'checkpoint_file': 'agent_state_CustomDetectionAgent.json'
                },
                'custom_setup': {
                    'class_name': 'CustomSetupAgent', 
                    'base_class': 'BaseAgent',
                    'capabilities': ['custom_setup', 'specialized_configuration'],
                    'model_requirements': ['gpt-4'],
                    'checkpoint_file': 'agent_state_CustomSetupAgent.json'
                }
            }
            
            if agent_type not in agent_templates:
                return {
                    'status': 'error',
                    'error': f'Unknown agent type: {agent_type}'
                }
            
            template = agent_templates[agent_type]
            
            # Create agent instance
            agent_config = {
                'agent_type': agent_type,
                'capabilities': template['capabilities'],
                'model_requirements': template['model_requirements'],
                'checkpoint_file': template['checkpoint_file'],
                **config
            }
            
            # Store created agent
            agent_id = f"{agent_type}_{int(time.time())}"
            self.created_agents[agent_id] = {
                'type': agent_type,
                'config': agent_config,
                'created_at': time.time(),
                'status': 'active'
            }
            
            # Notify relevant orchestrators about new agent
            self._notify_orchestrators_new_agent(agent_id, agent_config)
            
            return {
                'status': 'success',
                'agent_id': agent_id,
                'agent_type': agent_type,
                'capabilities': template['capabilities'],
                'message': f'Created new {agent_type} agent'
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'error': f'Failed to create agent: {str(e)}'
            }
    
    def _create_new_manager(self, manager_type: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new manager dynamically"""
        try:
            # Define manager templates
            manager_templates = {
                'custom_orchestrator': {
                    'class_name': 'CustomOrchestratorManager',
                    'base_class': 'BaseManager',
                    'capabilities': ['custom_workflow', 'specialized_orchestration'],
                    'agent_management': True,
                    'checkpoint_file': 'manager_state_CustomOrchestratorManager.json'
                },
                'custom_port_manager': {
                    'class_name': 'CustomPortManager',
                    'base_class': 'BaseManager', 
                    'capabilities': ['custom_port_allocation', 'specialized_networking'],
                    'agent_management': False,
                    'checkpoint_file': 'manager_state_CustomPortManager.json'
                }
            }
            
            if manager_type not in manager_templates:
                return {
                    'status': 'error',
                    'error': f'Unknown manager type: {manager_type}'
                }
            
            template = manager_templates[manager_type]
            
            # Create manager instance
            manager_config = {
                'manager_type': manager_type,
                'capabilities': template['capabilities'],
                'agent_management': template['agent_management'],
                'checkpoint_file': template['checkpoint_file'],
                **config
            }
            
            # Store created manager
            manager_id = f"{manager_type}_{int(time.time())}"
            self.created_managers[manager_id] = {
                'type': manager_type,
                'config': manager_config,
                'created_at': time.time(),
                'status': 'active'
            }
            
            # Provide context to other managers
            self._provide_manager_context(manager_id, manager_config)
            
            return {
                'status': 'success',
                'manager_id': manager_id,
                'manager_type': manager_type,
                'capabilities': template['capabilities'],
                'message': f'Created new {manager_type} manager'
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'error': f'Failed to create manager: {str(e)}'
            }
    
    def _create_business_orchestrator(self, business_name: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """Create a custom orchestrator for a business client"""
        try:
            # Validate business name
            if not business_name or not business_name.replace('_', '').replace('-', '').isalnum():
                return {
                    'status': 'error',
                    'error': 'Invalid business name. Use alphanumeric characters, underscores, or hyphens only.'
                }
            
            # Create business orchestrator
            orchestrator_id = f"{business_name}_orchestrator"
            orchestrator_config = {
                'business_name': business_name,
                'orchestrator_id': orchestrator_id,
                'custom_agents': config.get('custom_agents', []),
                'custom_managers': config.get('custom_managers', []),
                'workflow_steps': config.get('workflow_steps', []),
                'checkpoint_file': f'orchestrator_state_{orchestrator_id}.json',
                'created_at': time.time(),
                'status': 'active'
            }
            
            # Store business orchestrator
            self.business_orchestrators[orchestrator_id] = orchestrator_config
            
            # Create the orchestrator instance
            # This would typically involve dynamic class creation or template instantiation
            print(f"🏢 Created business orchestrator: {orchestrator_id}")
            
            return {
                'status': 'success',
                'orchestrator_id': orchestrator_id,
                'business_name': business_name,
                'message': f'Created business orchestrator for {business_name}',
                'poc_info': f'{orchestrator_id} is now the single POC for {business_name}'
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'error': f'Failed to create business orchestrator: {str(e)}'
            }
    
    def _intervene_orchestrator_failure(self, orchestrator_id: str, issue: Dict[str, Any]) -> Dict[str, Any]:
        """Intervene when orchestrator fails to report success"""
        try:
            print(f"🚨 Admin Agent intervening in orchestrator failure: {orchestrator_id}")
            
            # Analyze the issue
            issue_type = issue.get('type', 'unknown')
            failed_agents = issue.get('failed_agents', [])
            error_messages = issue.get('errors', [])
            
            # Determine intervention strategy
            if issue_type == 'agent_failure':
                # Create replacement agent if needed
                for agent_name in failed_agents:
                    if 'detection' in agent_name.lower():
                        self._create_new_agent('custom_detection', {'replacement_for': agent_name})
                    elif 'setup' in agent_name.lower():
                        self._create_new_agent('custom_setup', {'replacement_for': agent_name})
            
            elif issue_type == 'capability_issue':
                # Create specialized manager to handle capability gaps
                self._create_new_manager('custom_orchestrator', {
                    'handles_capabilities': issue.get('missing_capabilities', []),
                    'orchestrator_id': orchestrator_id
                })
            
            elif issue_type == 'out_of_scope':
                # Create new business orchestrator for out-of-scope requirements
                business_name = f"specialized_{orchestrator_id}"
                self._create_business_orchestrator(business_name, {
                    'scope': issue.get('scope', 'unknown'),
                    'requirements': issue.get('requirements', [])
                })
            
            return {
                'status': 'success',
                'intervention_type': issue_type,
                'actions_taken': [
                    'analyzed_failure',
                    'created_replacement_agents' if 'agent_failure' in issue_type else None,
                    'created_specialized_manager' if 'capability_issue' in issue_type else None,
                    'created_business_orchestrator' if 'out_of_scope' in issue_type else None
                ],
                'message': f'Intervention completed for {orchestrator_id}'
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'error': f'Intervention failed: {str(e)}'
            }
    
    def _notify_orchestrators_new_agent(self, agent_id: str, agent_config: Dict[str, Any]):
        """Notify relevant orchestrators about new agent"""
        # This would typically involve updating orchestrator configurations
        # and providing context about the new agent's capabilities
        print(f"📢 Notifying orchestrators about new agent: {agent_id}")
        
        # Update orchestrator context files
        context_update = {
            'new_agent': agent_id,
            'capabilities': agent_config.get('capabilities', []),
            'model_requirements': agent_config.get('model_requirements', []),
            'checkpoint_file': agent_config.get('checkpoint_file'),
            'notified_at': time.time()
        }
        
        # Save context update
        self._save_context_update('orchestrator_context.json', context_update)
    
    def _provide_manager_context(self, manager_id: str, manager_config: Dict[str, Any]):
        """Provide context to other managers about new manager"""
        print(f"📋 Providing context to managers about: {manager_id}")
        
        context_update = {
            'new_manager': manager_id,
            'capabilities': manager_config.get('capabilities', []),
            'agent_management': manager_config.get('agent_management', False),
            'checkpoint_file': manager_config.get('checkpoint_file'),
            'provided_at': time.time()
        }
        
        # Save context update
        self._save_context_update('manager_context.json', context_update)
    
    def _save_context_update(self, filename: str, context: Dict[str, Any]):
        """Save context update to file"""
        try:
            if os.path.exists(filename):
                with open(filename, 'r') as f:
                    existing_context = json.load(f)
            else:
                existing_context = {'updates': []}
            
            existing_context['updates'].append(context)
            
            with open(filename, 'w') as f:
                json.dump(existing_context, f, indent=2)
                
        except Exception as e:
            print(f"⚠️ Failed to save context update: {e}")
    
    def _get_system_status(self) -> Dict[str, Any]:
        """Get overall system status"""
        return {
            'status': 'success',
            'admin_agent_status': 'active',
            'created_agents': len(self.created_agents),
            'created_managers': len(self.created_managers),
            'business_orchestrators': len(self.business_orchestrators),
            'total_agents': list(self.created_agents.keys()),
            'total_managers': list(self.created_managers.keys()),
            'total_orchestrators': list(self.business_orchestrators.keys()),
            'checkpoint_file': self.checkpoint_file,
            'developer_access': self._check_developer_access()
        }
    
    def checkpoint(self, data: Dict[str, Any]):
        """Save admin agent state"""
        checkpoint_data = {
            'admin_agent_state': data,
            'created_agents': self.created_agents,
            'created_managers': self.created_managers,
            'business_orchestrators': self.business_orchestrators,
            'timestamp': time.time()
        }
        
        try:
            with open(self.checkpoint_file, 'w') as f:
                json.dump(checkpoint_data, f, indent=2)
            print(f"✅ Admin Agent checkpoint saved to {self.checkpoint_file}")
        except Exception as e:
            print(f"⚠️ Failed to save admin agent checkpoint: {e}") 