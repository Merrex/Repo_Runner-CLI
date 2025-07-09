import os
from typing import List, Tuple, Optional, Dict, Any
import re
import json
from ..user_management import get_user_manager, UserTier

class ContextIndexer:
    def __init__(self, use_faiss=None, config=None):
        """
        Initialize context indexer with configurable FAISS support.
        
        Args:
            use_faiss: Boolean or None. If None, will be determined by:
                      1. User config if provided
                      2. User tier permissions
                      3. Agent recommendation based on environment detection
                      4. Fallback to simple text search
            config: Configuration dict with FAISS settings
        """
        self.text_chunks = []
        self.index = None
        self.use_faiss = use_faiss
        self.faiss_available = False
        self.config = config or {}
        self.user_manager = get_user_manager()
        
        # Determine FAISS usage if not explicitly set
        if self.use_faiss is None:
            self.use_faiss = self._determine_faiss_usage()
        
        # Initialize FAISS if requested
        if self.use_faiss:
            self._init_faiss()
    
    def _determine_faiss_usage(self) -> bool:
        """
        Determine whether to use FAISS based on:
        1. User configuration
        2. User tier permissions
        3. Agent recommendations from environment detection
        4. Environment capabilities
        """
        # Check user config first
        if 'use_faiss' in self.config:
            return self.config['use_faiss']
        
        # Check user tier permissions
        if self.user_manager.current_user:
            capabilities = self.user_manager.get_current_user_capabilities()
            if capabilities:
                # Free users can only use simple search
                if capabilities.tier == UserTier.FREE:
                    print(f"🔒 Free tier user - using simple text search")
                    return False
                
                # Advanced users can use FAISS
                if capabilities.tier == UserTier.ADVANCED:
                    print(f"🔓 Advanced tier user - FAISS available")
                    # Continue to agent recommendations
                
                # Premium/Admin/Tester can use all indexers
                if capabilities.tier in [UserTier.PREMIUM, UserTier.ADMIN, UserTier.TESTER]:
                    print(f"🔓 {capabilities.tier.value} tier user - all indexers available")
                    # Continue to agent recommendations
        
        # Check for agent recommendations
        agent_recommendations = self._load_agent_recommendations()
        if agent_recommendations:
            return agent_recommendations.get('recommend_faiss', False)
        
        # Check environment capabilities
        return self._check_environment_capabilities()
    
    def _load_agent_recommendations(self) -> Optional[Dict[str, Any]]:
        """Load recommendations from agent checkpoints"""
        try:
            # Check for recommendations from EnvDetectorAgent
            env_state_file = 'agent_state_EnvDetectorAgent.json'
            if os.path.exists(env_state_file):
                with open(env_state_file, 'r') as f:
                    env_state = json.load(f)
                    if 'recommendations' in env_state:
                        return env_state['recommendations']
            
            # Check for recommendations from DependencyAgent
            dep_state_file = 'agent_state_DependencyAgent.json'
            if os.path.exists(dep_state_file):
                with open(dep_state_file, 'r') as f:
                    dep_state = json.load(f)
                    if 'recommendations' in dep_state:
                        return dep_state['recommendations']
            
            # Check for recommendations from DetectionAgent
            detection_state_file = 'agent_state_DetectionAgent.json'
            if os.path.exists(detection_state_file):
                with open(detection_state_file, 'r') as f:
                    detection_state = json.load(f)
                    if 'recommendations' in detection_state:
                        return detection_state['recommendations']
                        
        except Exception as e:
            print(f"⚠️ Could not load agent recommendations: {e}")
        
        return None
    
    def _check_environment_capabilities(self) -> bool:
        """Check if current environment supports FAISS"""
        try:
            # Check if we're in a resource-constrained environment
            is_colab = 'COLAB_GPU' in os.environ or 'COLAB_TPU' in os.environ
            is_aws_lambda = 'AWS_LAMBDA_FUNCTION_NAME' in os.environ
            
            if is_colab:
                # Colab has good resources, FAISS should work
                return True
            elif is_aws_lambda:
                # Lambda has limited resources, avoid FAISS
                return False
            else:
                # Local environment - check available memory
                import psutil
                memory_gb = psutil.virtual_memory().total / (1024**3)
                return memory_gb >= 2.0  # Require at least 2GB RAM
                
        except Exception as e:
            print(f"⚠️ Could not check environment capabilities: {e}")
            return False
    
    def _init_faiss(self):
        """Initialize FAISS if available."""
        try:
            import faiss
            from sentence_transformers import SentenceTransformer
            
            # Check if dependencies are available
            self.faiss_available = True
            model_name = self.config.get('sentence_transformer_model', 'all-MiniLM-L6-v2')
            self.model = SentenceTransformer(model_name)
            
            print("✅ FAISS and sentence-transformers available")
            print(f"🔧 Using model: {model_name}")
            
        except ImportError as e:
            print(f"⚠️ FAISS not available: {e}")
            print("🔄 Falling back to simple text search")
            self.faiss_available = False
            self.use_faiss = False
        except Exception as e:
            print(f"⚠️ FAISS initialization failed: {e}")
            self.faiss_available = False
            self.use_faiss = False

    def _read_files(self, file_paths: List[str]) -> List[Tuple[str, str]]:
        """
        Reads and splits files into (source, chunk) tuples.
        """
        chunks = []
        for path in file_paths:
            if os.path.exists(path):
                try:
                    with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                        # Split into lines or paragraphs for context granularity
                        for i, para in enumerate(content.split('\n\n')):
                            if para.strip():
                                chunks.append((f"{os.path.basename(path)}:{i}", para.strip()))
                except Exception as e:
                    print(f"Warning: Could not read {path}: {e}")
        return chunks

    def build_index(self, file_paths: List[str]):
        """
        Build an index from the given files (FAISS if available, otherwise simple text).
        """
        self.text_chunks = self._read_files(file_paths)
        if not self.text_chunks:
            print("Warning: No content to index.")
            return
        
        if self.use_faiss and self.faiss_available:
            # Use FAISS for semantic search
            texts = [chunk[1] for chunk in self.text_chunks]
            embeddings = self.model.encode(texts, show_progress_bar=False)
            dim = embeddings.shape[1]
            self.index = faiss.IndexFlatL2(dim)
            self.index.add(embeddings)
            print(f"✅ FAISS index built with {len(self.text_chunks)} chunks")
        else:
            # Use simple text search
            print(f"✅ Simple text index built with {len(self.text_chunks)} chunks")

    def query_index(self, query: str, top_k: int = 3) -> List[str]:
        """
        Query the index for top_k relevant chunks.
        """
        if not self.text_chunks:
            return []
        
        if self.use_faiss and self.faiss_available and self.index is not None:
            # Use FAISS semantic search
            try:
                query_emb = self.model.encode([query])
                D, I = self.index.search(query_emb, top_k)
                return [self.text_chunks[i][1] for i in I[0] if i < len(self.text_chunks)]
            except Exception as e:
                print(f"⚠️ FAISS search failed: {e}")
                # Fall back to text search
                pass
        
        # Simple keyword-based search (fallback)
        query_words = set(re.findall(r'\w+', query.lower()))
        scored_chunks = []
        
        for chunk_id, chunk_text in self.text_chunks:
            chunk_words = set(re.findall(r'\w+', chunk_text.lower()))
            # Calculate simple overlap score
            overlap = len(query_words.intersection(chunk_words))
            if overlap > 0:
                scored_chunks.append((overlap, chunk_text))
        
        # Sort by score and return top_k
        scored_chunks.sort(reverse=True)
        return [chunk for score, chunk in scored_chunks[:top_k]]
    
    def get_index_info(self) -> Dict[str, Any]:
        """Get information about the current index configuration"""
        user_info = {}
        if self.user_manager.current_user:
            capabilities = self.user_manager.get_current_user_capabilities()
            if capabilities:
                user_info = {
                    'user_tier': capabilities.tier.value,
                    'allowed_indexer_types': ['simple'] + (['faiss'] if capabilities.tier != UserTier.FREE else []) + (['chroma'] if capabilities.tier in [UserTier.PREMIUM, UserTier.ADMIN] else [])
                }
        
        return {
            'use_faiss': self.use_faiss,
            'faiss_available': self.faiss_available,
            'chunk_count': len(self.text_chunks),
            'index_type': 'FAISS' if (self.use_faiss and self.faiss_available) else 'Simple Text',
            'config': self.config,
            'user_info': user_info
        }

# Usage examples:
# User-configured:
# indexer = ContextIndexer(use_faiss=True, config={'sentence_transformer_model': 'all-MiniLM-L6-v2'})

# Agent-recommended (automatic):
# indexer = ContextIndexer()  # Will use agent recommendations

# Force simple text search:
# indexer = ContextIndexer(use_faiss=False) 