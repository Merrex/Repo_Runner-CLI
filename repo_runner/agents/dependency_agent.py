import subprocess
import sys
import os
from .base_agent import BaseAgent

# Cloud Environment Dependency Matrix
CLOUD_DEPENDENCY_MATRIX = {
    "colab": {
        "torch": "2.7.1",  # Colab's pre-installed version
        "torchvision": "0.22.0",
        "torchaudio": "2.7.1",
        "transformers": "4.53.1",  # Colab's pre-installed version
        "accelerate": "1.8.1",
        "numpy": "2.3.1",
        "requests": "2.32.4"
    },
    "aws": {
        "torch": "2.6.0",  # AWS Lambda/EC2 compatible
        "torchvision": "0.21.0",
        "torchaudio": "2.6.0",
        "transformers": "4.50.0",
        "accelerate": "1.7.0",
        "numpy": "2.0.0",
        "requests": "2.31.0"
    },
    "gcp": {
        "torch": "2.6.0",  # GCP AI Platform compatible
        "torchvision": "0.21.0",
        "torchaudio": "2.6.0",
        "transformers": "4.50.0",
        "accelerate": "1.7.0",
        "numpy": "2.0.0",
        "requests": "2.31.0"
    },
    "local": {
        "torch": "latest",  # Use latest stable
        "torchvision": "latest",
        "torchaudio": "latest",
        "transformers": "latest",
        "accelerate": "latest",
        "numpy": "latest",
        "requests": "latest"
    }
}

class DependencyAgent(BaseAgent):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.environment = self._detect_environment()
        self.dependency_matrix = CLOUD_DEPENDENCY_MATRIX.get(self.environment, CLOUD_DEPENDENCY_MATRIX["local"])

    def _detect_environment(self):
        """Detect the current cloud environment"""
        if 'COLAB_GPU' in os.environ or 'COLAB_TPU' in os.environ:
            return 'colab'
        elif 'AWS_EXECUTION_ENV' in os.environ:
            return 'aws'
        elif 'GOOGLE_CLOUD_PROJECT' in os.environ:
            return 'gcp'
        else:
            return 'local'

    def _check_faiss_dependencies(self):
        """Check if FAISS dependencies are available or can be installed"""
        try:
            # Check if faiss is already installed
            import faiss
            faiss_available = True
        except ImportError:
            faiss_available = False
        
        try:
            # Check if sentence-transformers is available
            from sentence_transformers import SentenceTransformer
            sentence_transformers_available = True
        except ImportError:
            sentence_transformers_available = False
        
        return {
            "faiss_available": faiss_available,
            "sentence_transformers_available": sentence_transformers_available,
            "can_install_faiss": self._can_install_package("faiss-cpu"),
            "can_install_sentence_transformers": self._can_install_package("sentence-transformers")
        }

    def _can_install_package(self, package):
        """Check if a package can be installed"""
        try:
            result = subprocess.run([sys.executable, '-m', 'pip', 'show', package], 
                                  capture_output=True, text=True)
            return result.returncode == 0
        except:
            return False

    def _generate_faiss_recommendations(self):
        """Generate FAISS recommendations based on dependency analysis"""
        faiss_status = self._check_faiss_dependencies()
        
        if faiss_status["faiss_available"] and faiss_status["sentence_transformers_available"]:
            return {
                "recommend_faiss": True,
                "reason": "FAISS and sentence-transformers are already available",
                "sentence_transformer_model": "all-MiniLM-L6-v2"
            }
        elif faiss_status["can_install_faiss"] and faiss_status["can_install_sentence_transformers"]:
            return {
                "recommend_faiss": True,
                "reason": "FAISS dependencies can be installed",
                "sentence_transformer_model": "all-MiniLM-L6-v2"
            }
        else:
            return {
                "recommend_faiss": False,
                "reason": "FAISS dependencies not available and cannot be installed",
                "sentence_transformer_model": None
            }

    def ensure_packages(self, packages, upgrade=False):
        """Ensure packages are installed with environment-aware versions"""
        print(f"🔧 Ensuring packages for {self.environment} environment...")
        
        for package in packages:
            if package in self.dependency_matrix:
                version = self.dependency_matrix[package]
                if version == "latest":
                    self._install_package(package, upgrade=upgrade)
                else:
                    self._install_package_version(package, version)
            else:
                # Package not in matrix, install latest
                self._install_package(package, upgrade=upgrade)
        
        return True

    def _install_package(self, package, upgrade=False):
        """Install a package with optional upgrade"""
        try:
            cmd = [sys.executable, '-m', 'pip', 'install']
            if upgrade:
                cmd.append('--upgrade')
            cmd.append(package)
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                print(f"✅ {package} installed successfully")
                return True
            else:
                print(f"⚠️ Failed to install {package}: {result.stderr}")
                return False
        except Exception as e:
            print(f"❌ Error installing {package}: {e}")
            return False

    def _install_package_version(self, package, version):
        """Install a specific version of a package"""
        try:
            cmd = [sys.executable, '-m', 'pip', 'install', f"{package}=={version}"]
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                print(f"✅ {package}=={version} installed successfully")
                return True
            else:
                print(f"⚠️ Failed to install {package}=={version}: {result.stderr}")
                # Fallback to latest
                return self._install_package(package)
        except Exception as e:
            print(f"❌ Error installing {package}=={version}: {e}")
            return self._install_package(package)

    def install_pyngrok(self):
        """Install pyngrok for tunnel management"""
        return self._install_package('pyngrok')

    def report_error(self, error, context=None, error_file="dependency_agent_errors.json"):
        import json
        self.log_result(f"Error reported: {error} | Context: {context}", "error")
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
            self.log_result(f"Failed to save error report: {e}", "error")

    def run(self, *args, **kwargs):
        """Manage dependencies with environment-aware versions"""
        detection_result = kwargs.get('detection_result', {})
        environment = kwargs.get('environment', 'local')
        
        try:
            # Use the existing dependency logic
            dependency_result = self.ensure_dependencies(detection_result, environment)
            
            # Add FAISS recommendations for local environment
            recommendations = {}
            if environment == 'local':
                try:
                    import psutil
                    ram_gb = psutil.virtual_memory().total / (1024**3)
                    if ram_gb >= 4.0:
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
                "dependencies": dependency_result,
                "environment": environment,
                "recommendations": recommendations
            }
            
            # Save checkpoint
            self.checkpoint(result)
            return result
            
        except Exception as e:
            error_result = {
                "status": "error",
                "agent": self.agent_name,
                "error": str(e)
            }
            self.report_error(e)
            return error_result

    def _install_pip_requirements(self, req_path):
        try:
            result = subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', req_path], capture_output=True, text=True)
            return {"returncode": result.returncode, "stdout": result.stdout[-500:], "stderr": result.stderr[-500:]}
        except Exception as e:
            self.report_error(e)
            return {"error": str(e)}

    def _install_conda_env(self, conda_path):
        try:
            result = subprocess.run(['conda', 'env', 'update', '-f', conda_path], capture_output=True, text=True)
            return {"returncode": result.returncode, "stdout": result.stdout[-500:], "stderr": result.stderr[-500:]}
        except Exception as e:
            self.report_error(e)
            return {"error": str(e)}

    def _install_apt_packages(self, apt_path):
        try:
            with open(apt_path) as f:
                pkgs = [line.strip() for line in f if line.strip() and not line.startswith('#')]
            if not pkgs:
                return {"skipped": "No apt packages listed"}
            result = subprocess.run(['sudo', 'apt-get', 'update'], capture_output=True, text=True)
            result2 = subprocess.run(['sudo', 'apt-get', 'install', '-y'] + pkgs, capture_output=True, text=True)
            return {"returncode": result2.returncode, "stdout": result2.stdout[-500:], "stderr": result2.stderr[-500:]}
        except Exception as e:
            self.report_error(e)
            return {"error": str(e)} 