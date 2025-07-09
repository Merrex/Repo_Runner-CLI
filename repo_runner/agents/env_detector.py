from .base_agent import BaseAgent
import os

class EnvDetectorAgent(BaseAgent):
    def run(self, *args, **kwargs):
        """Detect environment and provide FAISS recommendations"""
        env = "local"
        evidence = []
        recommendations = {}
        
        # Colab detection
        if 'COLAB_GPU' in os.environ or 'COLAB_TPU' in os.environ:
            env = "colab"
            evidence.append("COLAB_GPU/COLAB_TPU environment variables detected")
            recommendations['recommend_faiss'] = True
            recommendations['reason'] = "Colab environment has sufficient RAM for FAISS"
            recommendations['sentence_transformer_model'] = 'all-MiniLM-L6-v2'
        
        # AWS detection
        elif 'AWS_EXECUTION_ENV' in os.environ:
            env = "aws"
            evidence.append("AWS_EXECUTION_ENV environment variable detected")
            recommendations['recommend_faiss'] = True
            recommendations['reason'] = "AWS environment supports FAISS"
            recommendations['sentence_transformer_model'] = 'all-MiniLM-L6-v2'
        
        # GCP detection
        elif 'GOOGLE_CLOUD_PROJECT' in os.environ:
            env = "gcp"
            evidence.append("GOOGLE_CLOUD_PROJECT environment variable detected")
            recommendations['recommend_faiss'] = True
            recommendations['reason'] = "GCP environment supports FAISS"
            recommendations['sentence_transformer_model'] = 'all-MiniLM-L6-v2'
        
        # Local environment with RAM check
        else:
            try:
                import psutil
                ram_gb = psutil.virtual_memory().total / (1024**3)
                if ram_gb >= 4.0:  # 4GB minimum for FAISS
                    recommendations['recommend_faiss'] = True
                    recommendations['reason'] = f"Local environment has {ram_gb:.1f}GB RAM, sufficient for FAISS"
                    recommendations['sentence_transformer_model'] = 'all-MiniLM-L6-v2'
                else:
                    recommendations['recommend_faiss'] = False
                    recommendations['reason'] = f"Local environment has {ram_gb:.1f}GB RAM, insufficient for FAISS"
            except ImportError:
                recommendations['recommend_faiss'] = False
                recommendations['reason'] = "Cannot determine RAM, defaulting to simple search"
        
        result = {
            "status": "ok",
            "agent": self.agent_name,
            "environment": env,
            "evidence": evidence,
            "recommendations": recommendations
        }
        
        # Save checkpoint
        self.checkpoint(result)
        return result 