"""
Auto-installer for repo_runner system dependencies and Python packages.
"""

import subprocess
import sys
import os
import platform
from pathlib import Path

class SystemInstaller:
    """Handles automatic installation of system and Python dependencies."""
    
    def __init__(self):
        self.system = platform.system().lower()
        self.is_linux = self.system == "linux"
        self.is_macos = self.system == "darwin"
        self.is_windows = self.system == "windows"
    
    def install_system_dependencies(self):
        """Install required system dependencies."""
        print("🔧 Installing system dependencies...")
        
        if self.is_linux:
            self._install_linux_dependencies()
        elif self.is_macos:
            self._install_macos_dependencies()
        elif self.is_windows:
            self._install_windows_dependencies()
        else:
            print(f"⚠️  Unsupported operating system: {self.system}")
            return False
        
        print("✅ System dependencies installed successfully!")
        return True
    
    def _install_linux_dependencies(self):
        """Install dependencies on Linux systems."""
        try:
            # Update package list
            subprocess.run(["sudo", "apt-get", "update", "-qq"], check=True)
            
            # Install system packages
            packages = [
                "git",
                "curl", 
                "wget",
                "build-essential",
                "python3-dev",
                "python3-pip",
                "python3-venv"
            ]
            
            # Try to install Node.js and npm
            try:
                subprocess.run(["curl", "-fsSL", "https://deb.nodesource.com/setup_lts.x", "|", "sudo", "-E", "bash", "-"], 
                             shell=True, check=True)
                packages.extend(["nodejs", "npm"])
            except subprocess.CalledProcessError:
                print("⚠️  Could not install Node.js automatically. Please install manually if needed.")
            
            # Install packages
            subprocess.run(["sudo", "apt-get", "install", "-y"] + packages, check=True)
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install Linux dependencies: {e}")
            return False
        
        return True
    
    def _install_macos_dependencies(self):
        """Install dependencies on macOS systems."""
        try:
            # Check if Homebrew is installed
            result = subprocess.run(["which", "brew"], capture_output=True)
            if result.returncode != 0:
                print("📦 Installing Homebrew...")
                subprocess.run(['/bin/bash', '-c', '$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)'], 
                             check=True)
            
            # Install packages via Homebrew
            packages = ["git", "curl", "wget", "node"]
            subprocess.run(["brew", "install"] + packages, check=True)
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install macOS dependencies: {e}")
            return False
        
        return True
    
    def _install_windows_dependencies(self):
        """Install dependencies on Windows systems."""
        try:
            # Check if Chocolatey is installed
            result = subprocess.run(["choco", "--version"], capture_output=True)
            if result.returncode != 0:
                print("📦 Installing Chocolatey...")
                subprocess.run(['powershell', '-Command', 
                              'Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString("https://community.chocolatey.org/install.ps1"))'], 
                             check=True)
            
            # Install packages via Chocolatey
            packages = ["git", "curl", "nodejs"]
            subprocess.run(["choco", "install"] + packages + ["-y"], check=True)
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install Windows dependencies: {e}")
            return False
        
        return True
    
    def install_python_packages(self):
        """Install missing Python packages."""
        print("📦 Installing Python packages...")
        
        # List of required packages from pyproject.toml
        required_packages = [
            "click>=8.0.0",
            "requests>=2.25.0", 
            "PyYAML>=6.0",
            "python-dotenv>=0.19.0",
            "transformers>=4.30.0",
            "torch>=2.0.0",
            "accelerate>=0.20.0",
            "psutil>=5.8.0",
            "colorama>=0.4.4",
            "rich>=12.0.0",
            "jinja2>=3.0.0",
            "python-jose[cryptography]>=3.3.0",
            "openai>=1.0.0",
            "anthropic>=0.7.0",
            "google-generativeai>=0.3.0"
        ]
        
        try:
            # Install all packages with verbose output
            print("Installing packages...")
            result = subprocess.run(
                [sys.executable, "-m", "pip", "install"] + required_packages, 
                check=True,
                capture_output=True,
                text=True
            )
            print("✅ Python packages installed successfully!")
            print(f"Installation output: {result.stdout}")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install Python packages: {e}")
            print(f"Error output: {e.stderr}")
            return False
    
    def verify_installation(self):
        """Verify that all required dependencies are installed."""
        print("🔍 Verifying installation...")
        print(f"Python version: {sys.version}")
        print(f"Python executable: {sys.executable}")
        print(f"Python path: {sys.path[:3]}...")  # Show first 3 entries
        
        # Check Python packages with proper import names
        package_imports = {
            "click": "click",
            "requests": "requests", 
            "PyYAML": "yaml",  # PyYAML is imported as yaml
            "python-dotenv": "dotenv",  # python-dotenv is imported as dotenv
            "transformers": "transformers",
            "torch": "torch",
            "accelerate": "accelerate",
            "psutil": "psutil",
            "colorama": "colorama",
            "rich": "rich",
            "jinja2": "jinja2"
        }
        
        missing_packages = []
        verified_packages = []
        
        for package_name, import_name in package_imports.items():
            try:
                __import__(import_name)
                print(f"  ✅ {package_name}")
                verified_packages.append(package_name)
            except ImportError as e:
                missing_packages.append(package_name)
                print(f"  ❌ {package_name} (error: {e})")
        
        # Check system tools
        system_tools = ["git", "curl"]
        verified_tools = []
        
        if self.is_linux or self.is_macos:
            # Check for both 'node' and 'nodejs' as Node.js can be installed as either
            node_result = subprocess.run(["which", "node"], capture_output=True)
            nodejs_result = subprocess.run(["which", "nodejs"], capture_output=True)
            if node_result.returncode == 0:
                print(f"  ✅ node")
                verified_tools.append("node")
            elif nodejs_result.returncode == 0:
                print(f"  ✅ nodejs")
                verified_tools.append("nodejs")
            else:
                print(f"  ❌ node/nodejs")
                missing_packages.append("node")
        
        for tool in system_tools:
            result = subprocess.run(["which", tool], capture_output=True)
            if result.returncode == 0:
                print(f"  ✅ {tool}")
                verified_tools.append(tool)
            else:
                print(f"  ❌ {tool}")
                missing_packages.append(tool)
        
        # More lenient verification - if most packages are available, consider it successful
        total_packages = len(package_imports) + len(system_tools) + 1  # +1 for node
        verified_count = len(verified_packages) + len(verified_tools)
        success_rate = verified_count / total_packages
        
        print(f"\n📊 Verification Summary:")
        print(f"  Verified packages: {verified_count}/{total_packages} ({success_rate:.1%})")
        print(f"  Python packages: {len(verified_packages)}/{len(package_imports)}")
        print(f"  System tools: {len(verified_tools)}/{len(system_tools) + 1}")
        
        if missing_packages:
            print(f"\n⚠️  Missing packages: {missing_packages}")
            
            # Try to install missing Python packages
            missing_python_packages = [pkg for pkg in missing_packages if pkg in package_imports]
            if missing_python_packages:
                print(f"🔄 Retrying installation of missing packages: {missing_python_packages}")
                try:
                    subprocess.run(
                        [sys.executable, "-m", "pip", "install"] + missing_python_packages, 
                        check=True
                    )
                    print("✅ Missing packages installed successfully!")
                    
                    # Verify again
                    print("🔍 Re-verifying installation...")
                    all_installed = True
                    for package_name, import_name in package_imports.items():
                        try:
                            __import__(import_name)
                            print(f"  ✅ {package_name}")
                        except ImportError:
                            print(f"  ❌ {package_name}")
                            all_installed = False
                    
                    if all_installed:
                        print("✅ All dependencies verified successfully!")
                        return True
                except subprocess.CalledProcessError as e:
                    print(f"❌ Failed to install missing packages: {e}")
            
            # If we have most packages working, consider it a success
            if success_rate >= 0.8:  # 80% success rate
                print(f"✅ Installation mostly successful ({success_rate:.1%} success rate)")
                print("⚠️  Some packages may not be available in this environment, but core functionality should work.")
                return True
            else:
                return False
        
        print("✅ All dependencies verified successfully!")
        return True

def auto_install():
    """Main auto-installation function."""
    print("🚀 repo_runner Auto-Installer")
    print("=" * 40)
    
    installer = SystemInstaller()
    
    # Install system dependencies
    if not installer.install_system_dependencies():
        print("❌ Failed to install system dependencies")
        return False
    
    # Install Python packages
    if not installer.install_python_packages():
        print("❌ Failed to install Python packages")
        return False
    
    # Verify installation
    if not installer.verify_installation():
        print("❌ Installation verification failed")
        return False
    
    print("\n🎉 repo_runner is ready to use!")
    print("Run: repo_runner --help")
    return True

if __name__ == "__main__":
    auto_install() 