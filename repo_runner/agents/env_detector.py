from .base_agent import BaseAgent
import os

class EnvDetectorAgent(BaseAgent):
    def run(self, *args, **kwargs):
        env = "local"
        evidence = []
        # Colab detection
        if "COLAB_GPU" in os.environ or "COLAB_TPU" in os.environ or "COLAB_RELEASE_TAG" in os.environ:
            env = "colab"
            evidence.append("COLAB env var detected")
        # AWS detection
        elif "AWS_EXECUTION_ENV" in os.environ or os.path.exists("/etc/aws"):
            env = "aws"
            evidence.append("AWS_EXECUTION_ENV or /etc/aws detected")
        # GCP detection
        elif "GOOGLE_CLOUD_PROJECT" in os.environ or os.path.exists("/gcp"):
            env = "gcp"
            evidence.append("GOOGLE_CLOUD_PROJECT or /gcp detected")
        # Docker detection
        elif os.path.exists("/.dockerenv"):
            env = "docker"
            evidence.append("/.dockerenv detected")
        # Kubernetes detection
        elif "KUBERNETES_SERVICE_HOST" in os.environ:
            env = "kubernetes"
            evidence.append("KUBERNETES_SERVICE_HOST detected")
        else:
            evidence.append("No cloud env vars detected; assuming local")
        self.log_result(f"[EnvDetectorAgent] Detected environment: {env} | Evidence: {evidence}")
        return {"status": "ok", "agent": self.agent_name, "environment": env, "evidence": evidence} 