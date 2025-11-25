import subprocess
import platform
import time
import requests
import sys
from typing import Optional

class OllamaManager:
    """Manages Ollama service startup and model downloads."""
    
    def __init__(self, host: str = "http://localhost:11434"):
        self.host = host
        self.api_url = f"{host}/api"
    
    def is_ollama_running(self) -> bool:
        """Check if Ollama service is running."""
        try:
            response = requests.get(f"{self.host}/api/version", timeout=2)
            return response.status_code == 200
        except requests.exceptions.RequestException:
            return False
    
    def start_ollama(self) -> bool:
        """Start Ollama service based on the operating system."""
        if self.is_ollama_running():
            print("✓ Ollama is already running")
            return True
        
        print("Starting Ollama service...")
        system = platform.system()
        
        try:
            if system == "Windows":
                # On Windows, Ollama typically runs as a service or can be started directly
                subprocess.Popen(["ollama", "serve"], 
                               stdout=subprocess.DEVNULL, 
                               stderr=subprocess.DEVNULL,
                               creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, 'CREATE_NO_WINDOW') else 0)
            elif system in ["Linux", "Darwin"]:  # Darwin is macOS
                # On Unix-like systems, start in background
                subprocess.Popen(["ollama", "serve"],
                               stdout=subprocess.DEVNULL,
                               stderr=subprocess.DEVNULL,
                               start_new_session=True)
            else:
                print(f"⚠ Unsupported operating system: {system}")
                return False
            
            # Wait for Ollama to start (max 30 seconds)
            for _ in range(30):
                time.sleep(1)
                if self.is_ollama_running():
                    print("✓ Ollama service started successfully")
                    return True
            
            print("⚠ Ollama service started but not responding")
            return False
            
        except FileNotFoundError:
            print("✗ Ollama executable not found. Please ensure Ollama is installed.")
            print("  Download from: https://ollama.com/download")
            return False
        except Exception as e:
            print(f"✗ Error starting Ollama: {e}")
            return False
    
    def is_model_available(self, model_name: str) -> bool:
        """Check if a model is already downloaded."""
        try:
            response = requests.get(f"{self.api_url}/tags", timeout=5)
            if response.status_code == 200:
                data = response.json()
                models = data.get("models", [])
                return any(model.get("name", "").startswith(model_name) for model in models)
            return False
        except requests.exceptions.RequestException:
            return False
    
    def download_model(self, model_name: str) -> bool:
        """Download a model if not already available."""
        if self.is_model_available(model_name):
            print(f"✓ Model '{model_name}' is already available")
            return True
        
        print(f"Downloading model '{model_name}'... This may take several minutes.")
        try:
            # Use subprocess to run ollama pull command for better feedback
            process = subprocess.Popen(
                ["ollama", "pull", model_name],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True
            )
            
            # Stream output
            for line in process.stdout:
                print(line.strip())
            
            process.wait()
            
            if process.returncode == 0:
                print(f"✓ Model '{model_name}' downloaded successfully")
                return True
            else:
                print(f"✗ Failed to download model '{model_name}'")
                return False
                
        except FileNotFoundError:
            print("✗ Ollama command not found. Please ensure Ollama is installed.")
            return False
        except Exception as e:
            print(f"✗ Error downloading model: {e}")
            return False
    
    def setup(self, model_name: str = "qwen2.5:7b") -> bool:
        """
        Complete setup: start Ollama and ensure model is available.
        
        Args:
            model_name: Name of the model to download (default: qwen2.5:7b)
        
        Returns:
            bool: True if setup successful, False otherwise
        """
        print("=" * 50)
        print("OLLAMA SETUP")
        print("=" * 50)
        
        # Step 1: Start Ollama
        if not self.start_ollama():
            return False
        
        # Step 2: Download model
        if not self.download_model(model_name):
            return False
        
        print("=" * 50)
        print("✓ Setup completed successfully!")
        print("=" * 50)
        return True


def main():
    """CLI interface for Ollama manager."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Manage Ollama service and models")
    parser.add_argument("--model", type=str, default="qwen2.5:7b",
                       help="Model to download (default: qwen2.5:7b)")
    parser.add_argument("--host", type=str, default="http://localhost:11434",
                       help="Ollama host URL (default: http://localhost:11434)")
    
    args = parser.parse_args()
    
    manager = OllamaManager(host=args.host)
    success = manager.setup(model_name=args.model)
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
