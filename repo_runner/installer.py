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
    
    def verify_installation(self):
        """Verify that all required dependencies are installed."""
        print("🔍 Verifying installation...")
        
        # Check Python packages
        required_packages = [
            "click", "requests", "PyYAML", "python-dotenv",
            "transformers", "torch", "accelerate", "psutil",
            "colorama", "rich", "jinja2"
        ]
        
        missing_packages = []
        for package in required_packages:
            try:
                __import__(package)
                print(f"  ✅ {package}")
            except ImportError:
                missing_packages.append(package)
                print(f"  ❌ {package}")
        
        # Check system tools
        system_tools = ["git", "curl"]
        if self.is_linux or self.is_macos:
            system_tools.append("node")
        
        for tool in system_tools:
            result = subprocess.run(["which", tool], capture_output=True)
            if result.returncode == 0:
                print(f"  ✅ {tool}")
            else:
                print(f"  ❌ {tool}")
                missing_packages.append(tool)
        
        if missing_packages:
            print(f"\n⚠️  Missing packages: {missing_packages}")
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
    
    # Verify installation
    if not installer.verify_installation():
        print("❌ Installation verification failed")
        return False
    
    print("\n🎉 repo_runner is ready to use!")
    print("Run: repo_runner --help")
    return True

if __name__ == "__main__":
    auto_install() 