import os
import sys
import subprocess
import platform
import time
import psutil
import socket
from datetime import datetime
import logging
import json
import requests
import traceback
from pathlib import Path
from typing import Optional, Dict, List, Union

class TroubleshootManager:
    def __init__(self):
        try:
            # Create directories first
            self.base_dir = self.create_base_directory()
            self.log_file = self.base_dir / 'troubleshoot.log'
            self.backup_dir = self.base_dir / 'backup'
            self.backup_dir.mkdir(exist_ok=True)
            
            # Setup logging with file
            self.setup_logging()
            
            # Initialize system info
            self.system_info = SystemInfo()
            
            # Initial logging
            logging.info("\n" + "=" * 80)  # Add separator line
            logging.info("Starting new troubleshooting session")
            logging.info("Starting initialization...")
            logging.info("Progress monitor initialized")
            logging.info("System info initialized")
            logging.info("Backup directory created")
            logging.info("TroubleshootManager initialized successfully")
            
        except Exception as e:
            print(f"Error initializing TroubleshootManager: {str(e)}")
            raise

    def setup_logging(self):
        """Setup logging configuration"""
        try:
            # Create a formatter
            formatter = logging.Formatter(
                fmt='%(asctime)s - %(levelname)s - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )

            # Setup file handler
            file_handler = logging.FileHandler(self.log_file)
            file_handler.setFormatter(formatter)
            file_handler.setLevel(logging.INFO)

            # Setup console handler
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(formatter)
            console_handler.setLevel(logging.INFO)

            # Get the root logger
            root_logger = logging.getLogger()
            root_logger.setLevel(logging.INFO)
            
            # Clear any existing handlers
            if root_logger.hasHandlers():
                root_logger.handlers.clear()
            
            # Add handlers
            root_logger.addHandler(file_handler)
            root_logger.addHandler(console_handler)

        except Exception as e:
            print(f"Error setting up logging: {str(e)}")
            raise

    def create_base_directory(self) -> Path:
        """Create base directory for troubleshooter files"""
        try:
            base_dir = Path.home() / 'python_troubleshooter'
            base_dir.mkdir(exist_ok=True)
            return base_dir
        except Exception as e:
            print(f"Error creating base directory: {str(e)}")
            raise

    def print_status(self, text: str) -> None:
        """Print status message with proper formatting"""
        try:
            message = f"[*] {text}"
            print(message)
            logging.info(text)  # Log the clean text without [*]
        except Exception as e:
            print(f"Error printing status: {str(e)}")

    def print_header(self, text: str) -> None:
        """Print a formatted header"""
        header = "\n" + "=" * 60 + "\n" + text.center(60) + "\n" + "=" * 60 + "\n"
        print(header)
        logging.info(header)  # Log the full header

    def run_command(self, command: str, silent: bool = False) -> Optional[subprocess.CompletedProcess]:
        """Run a command and return the result"""
        try:
            result = subprocess.run(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                shell=True,
                timeout=60
            )
            
            if not silent:
                if result.stdout:
                    logging.info(f"Command output:\n{result.stdout}")
                if result.stderr:
                    logging.error(f"Command errors:\n{result.stderr}")
            
            return result
            
        except subprocess.TimeoutExpired:
            error_msg = f"Command timed out after 60 seconds: {command}"
            logging.error(error_msg)
            return None
        except Exception as e:
            error_msg = f"Error running command '{command}': {str(e)}"
            logging.error(error_msg)
            return None

    def run_all_checks(self) -> Dict:
        """Run all diagnostic checks and return results"""
        try:
            self.print_status("Starting diagnostic checks...")
            results = {
                'timestamp': datetime.now().isoformat(),
                'system_checks': {},
                'network_checks': {},
                'python_checks': {},
                'issues_found': False
            }

            # System Resources Check
            self.print_header("System Resources Check")
            system_resources = self.check_system_resources()
            results['system_checks']['resources'] = system_resources

            # Network Connectivity Check
            self.print_header("Network Connectivity Check")
            network_status = self.check_network_connectivity()
            results['network_checks'] = network_status

            # Python Environment Check
            self.print_header("Python Environment Check")
            python_status = self.check_python_environment()
            results['python_checks'] = python_status

            # Determine if issues were found
            results['issues_found'] = self.analyze_results(results)

            return results

        except Exception as e:
            error_msg = f"Error running diagnostic checks: {str(e)}"
            logging.error(error_msg)
            return {'error': error_msg}

    def check_system_resources(self) -> Dict:
        """Check system resources and return status"""
        resources = {}
        try:
            # CPU Usage
            cpu_percent = psutil.cpu_percent(interval=1)
            logging.info(f"CPU Usage: {cpu_percent}")
            resources['cpu_usage'] = cpu_percent

            # Memory Usage
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            available_gb = memory.available / (1024**3)
            logging.info(f"Memory Usage: {memory_percent}")
            logging.info(f"Available Memory: {available_gb:.2f}")
            resources['memory_usage'] = memory_percent
            resources['available_memory'] = f"{available_gb:.2f} GB"

            # Disk Usage
            disk = psutil.disk_usage('/')
            disk_percent = disk.percent
            free_gb = disk.free / (1024**3)
            logging.info(f"Disk Usage: {disk_percent}")
            logging.info(f"Free Disk Space: {free_gb:.2f}")
            resources['disk_usage'] = disk_percent
            resources['free_disk_space'] = f"{free_gb:.2f} GB"

            return resources

        except Exception as e:
            error_msg = f"Error checking system resources: {str(e)}"
            logging.error(error_msg)
            return {'error': error_msg}

    def check_network_connectivity(self) -> Dict:
        """Check network connectivity and access to important services"""
        results = {
            'internet_connection': False,
            'pypi_access': False,
            'github_access': False,
            'dns_resolution': False,
            'latency': {},
            'errors': []
        }
        
        try:
            # Test basic internet connectivity
            try:
                socket.create_connection(("8.8.8.8", 53), timeout=3)
                results['internet_connection'] = True
                logging.info("Internet Connection: Available")
            except Exception as e:
                results['errors'].append(f"Internet connection error: {str(e)}")
                logging.error(f"Internet connection error: {str(e)}")

            # Test DNS resolution
            try:
                socket.gethostbyname("python.org")
                results['dns_resolution'] = True
            except Exception as e:
                results['errors'].append(f"DNS resolution error: {str(e)}")
                logging.error(f"DNS resolution error: {str(e)}")

            # Test PyPI access
            try:
                response = requests.get("https://pypi.org", timeout=5)
                results['pypi_access'] = response.status_code == 200
                results['latency']['pypi'] = response.elapsed.total_seconds()
                logging.info("PyPI Access: Available")
            except Exception as e:
                results['errors'].append(f"PyPI access error: {str(e)}")
                logging.error(f"PyPI access error: {str(e)}")

            # Test GitHub access
            try:
                response = requests.get("https://github.com", timeout=5)
                results['github_access'] = response.status_code == 200
                results['latency']['github'] = response.elapsed.total_seconds()
                logging.info("GitHub Access: Available")
            except Exception as e:
                results['errors'].append(f"GitHub access error: {str(e)}")
                logging.error(f"GitHub access error: {str(e)}")

            # Test SSL/TLS functionality
            try:
                import ssl
                ssl_context = ssl.create_default_context()
                with socket.create_connection(("python.org", 443)) as sock:
                    with ssl_context.wrap_socket(sock, server_hostname="python.org") as ssock:
                        results['ssl_working'] = True
            except Exception as e:
                results['errors'].append(f"SSL error: {str(e)}")
                logging.error(f"SSL error: {str(e)}")

            # Check proxy settings
            proxy_settings = {
                'http_proxy': os.environ.get('http_proxy', ''),
                'https_proxy': os.environ.get('https_proxy', ''),
                'no_proxy': os.environ.get('no_proxy', '')
            }
            results['proxy_settings'] = proxy_settings

            # Test network speed (basic)
            try:
                start_time = time.time()
                requests.get("https://www.google.com", timeout=5)
                end_time = time.time()
                results['latency']['google'] = end_time - start_time
            except Exception as e:
                results['errors'].append(f"Speed test error: {str(e)}")
                logging.error(f"Speed test error: {str(e)}")

            # Log detailed results
            self.log_network_results(results)

            return results

        except Exception as e:
            error_msg = f"Error checking network connectivity: {str(e)}"
            logging.error(error_msg)
            results['errors'].append(error_msg)
            return results

    def log_network_results(self, results: Dict):
        """Log detailed network test results"""
        try:
            if results['internet_connection']:
                logging.info("Basic Internet Connection: ✓")
            else:
                logging.error("Basic Internet Connection: ✗")

            if results['dns_resolution']:
                logging.info("DNS Resolution: ✓")
            else:
                logging.error("DNS Resolution: ✗")

            if results['pypi_access']:
                logging.info(f"PyPI Access: ✓ (Latency: {results['latency'].get('pypi', 'N/A')}s)")
            else:
                logging.error("PyPI Access: ✗")

            if results['github_access']:
                logging.info(f"GitHub Access: ✓ (Latency: {results['latency'].get('github', 'N/A')}s)")
            else:
                logging.error("GitHub Access: ✗")

            if results.get('ssl_working', False):
                logging.info("SSL/TLS: ✓")
            else:
                logging.error("SSL/TLS: ✗")

            if results['errors']:
                logging.warning("Network test errors encountered:")
                for error in results['errors']:
                    logging.warning(f"  - {error}")

        except Exception as e:
            logging.error(f"Error logging network results: {str(e)}")

    def analyze_network_issues(self, results: Dict) -> List[str]:
        """Analyze network test results and provide recommendations"""
        recommendations = []
        try:
            if not results['internet_connection']:
                recommendations.append("Check physical network connection and router")
            
            if not results['dns_resolution']:
                recommendations.append("Check DNS settings or try using alternative DNS servers (e.g., 8.8.8.8)")
            
            if not results['pypi_access']:
                recommendations.append("Check if PyPI is blocked by firewall or proxy settings")
            
            if not results['github_access']:
                recommendations.append("Check if GitHub is blocked by firewall or proxy settings")
            
            if not results.get('ssl_working', False):
                recommendations.append("Check SSL/TLS configuration and certificates")
            
            if any(lat > 2.0 for lat in results['latency'].values()):
                recommendations.append("Network latency is high - consider checking network quality")
            
            return recommendations
            
        except Exception as e:
            logging.error(f"Error analyzing network issues: {str(e)}")
            return ["Error analyzing network issues"]

    def check_python_environment(self) -> Dict:
        """Check Python environment status"""
        try:
            python_status = {
                'python_version': sys.version,
                'pip_version': self.get_pip_version(),
                'site_packages': self.check_site_packages(),
                'installed_packages': self.get_installed_packages()
            }
            return python_status
        except Exception as e:
            logging.error(f"Error checking Python environment: {str(e)}")
            return {'error': str(e)}

    def analyze_results(self, results: Dict) -> bool:
        """Analyze results to determine if issues were found"""
        issues_found = False
        try:
            # Check system resources
            if results['system_checks'].get('resources', {}).get('disk_usage', 0) > 90:
                issues_found = True
                logging.warning("High disk usage detected")

            # Check network connectivity
            network = results['network_checks']
            if not network.get('internet_connection', False):
                issues_found = True
                logging.warning("No internet connection detected")

            return issues_found

        except Exception as e:
            logging.error(f"Error analyzing results: {str(e)}")
            return True  # Assume issues if analysis fails

    def get_pip_version(self) -> str:
        """Get pip version"""
        try:
            result = self.run_command('pip --version', silent=True)
            if result and result.returncode == 0:
                return result.stdout.strip()
            return "Unknown"
        except Exception as e:
            logging.error(f"Error getting pip version: {e}")
            return "Error"

    def get_installed_packages(self) -> List[str]:
        """Get list of installed packages"""
        try:
            result = self.run_command('pip list', silent=True)
            if result and result.returncode == 0:
                return result.stdout.strip().split('\n')[2:]  # Skip header rows
            return []
        except Exception as e:
            logging.error(f"Error getting installed packages: {e}")
            return []

    def check_site_packages(self) -> Dict:
        """Check site-packages directory status"""
        try:
            import site
            site_packages = Path(site.getsitepackages()[0])
            return {
                'path': str(site_packages),
                'exists': site_packages.exists(),
                'writable': os.access(site_packages, os.W_OK) if site_packages.exists() else False,
                'size': self.get_directory_size(site_packages) if site_packages.exists() else 0
            }
        except Exception as e:
            logging.error(f"Error checking site-packages: {str(e)}")
            return {'error': str(e)}

    def fix_pip(self) -> bool:
        """Fix pip installation"""
        try:
            self.print_status("Fixing pip installation...")
            
            # Create backup
            self.print_status("Creating pip packages backup...")
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = self.backup_dir / f"pip_list_{timestamp}.txt"
            self.run_command(f'pip freeze > "{backup_file}"')
            
            # Update pip
            self.print_status("Updating pip to latest version...")
            self.run_command('python -m pip install --upgrade pip')
            
            # Install/upgrade essential packages
            self.print_status("Installing/Upgrading setuptools and wheel...")
            self.run_command('pip install --upgrade setuptools wheel')
            
            # Clean pip cache
            self.print_status("Cleaning pip cache...")
            self.run_command('pip cache purge')
            
            return True
            
        except Exception as e:
            logging.error(f"Error fixing pip: {e}")
            return False

    def setup_environment_variables(self) -> bool:
        """Setup and fix environment variables"""
        try:
            self.print_status("Setting up environment variables...")
            
            # Get current user's Python Scripts directories
            python_version = f"Python{sys.version_info.major}{sys.version_info.minor}"
            paths_to_add = [
                Path(sys.executable).parent / 'Scripts',
                Path.home() / 'AppData' / 'Local' / 'Programs' / python_version / 'Scripts',
                Path.home() / 'AppData' / 'Roaming' / python_version / 'Scripts',
                Path.home() / 'AppData' / 'Roaming' / 'Python' / python_version / 'Scripts'
            ]

            # Get current PATH
            current_path = os.environ.get('PATH', '').split(os.pathsep)
            paths_added = []

            # Add missing paths
            for path in paths_to_add:
                if path.exists() and str(path) not in current_path:
                    current_path.append(str(path))
                    paths_added.append(str(path))
                    logging.info(f"Added to PATH: {path}")

            # Set updated PATH
            if paths_added:
                new_path = os.pathsep.join(current_path)
                os.environ['PATH'] = new_path
                
                # Try to set system PATH permanently (Windows only)
                if platform.system() == 'Windows':
                    try:
                        import winreg
                        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, 'Environment', 0, winreg.KEY_ALL_ACCESS) as key:
                            winreg.SetValueEx(key, 'PATH', 0, winreg.REG_EXPAND_SZ, new_path)
                        logging.info("Updated system PATH permanently")
                    except Exception as e:
                        logging.error(f"Could not update system PATH permanently: {e}")

            # Setup PYTHONPATH if not set
            if not os.environ.get('PYTHONPATH'):
                site_packages = [
                    path for path in site.getsitepackages()
                    if 'site-packages' in str(path)
                ]
                if site_packages:
                    python_path = os.pathsep.join(site_packages)
                    os.environ['PYTHONPATH'] = python_path
                    logging.info(f"Set PYTHONPATH to: {python_path}")
                    
                    # Try to set PYTHONPATH permanently (Windows only)
                    if platform.system() == 'Windows':
                        try:
                            import winreg
                            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, 'Environment', 0, winreg.KEY_ALL_ACCESS) as key:
                                winreg.SetValueEx(key, 'PYTHONPATH', 0, winreg.REG_EXPAND_SZ, python_path)
                            logging.info("Set PYTHONPATH permanently")
                        except Exception as e:
                            logging.error(f"Could not set PYTHONPATH permanently: {e}")

            # Verify PyQt6 scripts are accessible
            pyqt_scripts = ['pylupdate6.exe', 'pyuic6.exe']
            for script in pyqt_scripts:
                if self.find_executable(script):
                    logging.info(f"Found {script} in PATH")
                else:
                    logging.warning(f"Could not find {script} in PATH")

            return True

        except Exception as e:
            error_msg = f"Error setting up environment variables: {str(e)}"
            logging.error(error_msg)
            return False

    def find_executable(self, executable: str) -> Optional[str]:
        """Find an executable in PATH"""
        try:
            if platform.system() == "Windows":
                paths = os.environ["PATH"].split(os.pathsep)
                exe_file = executable
                if not executable.endswith('.exe'):
                    exe_file = executable + '.exe'
                
                for path in paths:
                    exe_path = os.path.join(path, exe_file)
                    if os.path.isfile(exe_path):
                        return exe_path
            else:
                return shutil.which(executable)
                
            return None
        except Exception as e:
            logging.error(f"Error finding executable {executable}: {str(e)}")
            return None

    def repair_environment(self) -> bool:
        """Attempt to repair the Python environment"""
        try:
            self.print_status("Starting environment repair...")
            
            # Fix pip first
            if not self.fix_pip():
                logging.error("Failed to fix pip")
                return False
            
            # Repair PyQt6 installation
            self.print_status("Repairing PyQt6 installation...")
            try:
                # Remove existing PyQt6 installations
                self.run_command('pip uninstall PyQt6 PyQt6-Qt6 PyQt6-sip -y')
                # Reinstall PyQt6
                self.run_command('pip install PyQt6')
            except Exception as e:
                logging.error(f"Error repairing PyQt6: {str(e)}")
            
            # Setup environment variables
            self.setup_environment_variables()
            
            # Verify installation
            self.verify_installation()
            
            return True
            
        except Exception as e:
            error_msg = f"Error repairing environment: {str(e)}"
            logging.error(error_msg)
            return False

    def verify_installation(self):
        """Verify the installation and environment setup"""
        try:
            self.print_status("Verifying installation...")
            
            # Check PyQt6 import
            try:
                import PyQt6
                logging.info(f"PyQt6 version: {PyQt6.__version__}")
            except ImportError as e:
                logging.error(f"PyQt6 import failed: {e}")
            
            # Verify executables
            for script in ['pylupdate6', 'pyuic6']:
                path = self.find_executable(script)
                if path:
                    logging.info(f"Found {script} at: {path}")
                else:
                    logging.warning(f"Could not find {script}")
            
            # Check environment variables
            logging.info(f"PYTHONPATH: {os.environ.get('PYTHONPATH', 'Not set')}")
            
        except Exception as e:
            logging.error(f"Error verifying installation: {str(e)}")

class SystemInfo:
    def __init__(self):
        try:
            self.python_version = sys.version
            self.platform = platform.platform()
            self.architecture = platform.architecture()[0]
            self.processor = platform.processor()
            
            try:
                self.memory = psutil.virtual_memory()
            except Exception as e:
                logging.warning(f"Could not get memory info: {e}")
                self.memory = None
            
        except Exception as e:
            logging.error(f"Error initializing SystemInfo: {str(e)}")
            raise

    def to_dict(self) -> Dict:
        """Convert system info to dictionary"""
        return {
            'python_version': self.python_version,
            'platform': self.platform,
            'architecture': self.architecture,
            'processor': self.processor,
            'memory': str(self.memory) if self.memory else 'Unknown'
        }

def main():
    """Main function - automated one-click process"""
    try:
        print("\n=== Python Environment Troubleshooter ===")
        print("Starting automated diagnostic process...\n")
        
        # Initialize troubleshooter
        troubleshooter = TroubleshootManager()
        
        # Run diagnostics
        troubleshooter.print_status("Running diagnostics...")
        results = troubleshooter.run_all_checks()
        
        # Create system report
        troubleshooter.print_status("Creating system report...")
        system_info = troubleshooter.system_info.to_dict()
        
        # Attempt repair
        troubleshooter.print_status("Attempting environment repair...")
        repair_success = troubleshooter.repair_environment()
        
        # Print summary
        print("\n=== Troubleshooting Summary ===")
        print(f"Log file location: {troubleshooter.log_file}")
        print(f"Report directory: {troubleshooter.base_dir}")
        print(f"Repair status: {'Successful' if repair_success else 'Failed'}")
        print("\nProcess complete. Check the log file for detailed information.")
        
    except Exception as e:
        print(f"\nCritical error: {str(e)}")
        traceback.print_exc()
    
    finally:
        # Keep window open
        print("\nPress Enter to exit...")
        input()

if __name__ == "__main__":
    main()