import subprocess
import sys
import pkg_resources
import platform
import os
from typing import List, Tuple

class Colors:
    """ANSI color codes for terminal output"""
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_colored(text: str, color: str) -> None:
    """Print colored text if platform supports it"""
    if platform.system() == 'Windows':
        # Enable ANSI escape sequences for Windows
        os.system('color')
    print(f"{color}{text}{Colors.ENDC}")

def get_requirements() -> List[Tuple[str, str]]:
    """Define required packages and their minimum versions"""
    return [
        ('psutil', '5.8.0'),
        ('requests', '2.25.0'),
        ('PyQt6', '6.0.0'),
        ('typing', '3.7.4'),
        ('pathlib', '1.0.1'),
        ('setuptools', '45.0.0'),
        ('wheel', '0.37.0'),
        ('pip', '21.0.0'),
    ]

def check_python_version() -> bool:
    """Check if Python version meets minimum requirements"""
    min_version = (3, 7)
    current_version = sys.version_info[:2]
    
    if current_version < min_version:
        print_colored(
            f"Error: Python {min_version[0]}.{min_version[1]} or higher is required. "
            f"You are using Python {current_version[0]}.{current_version[1]}",
            Colors.FAIL
        )
        return False
    return True

def upgrade_pip() -> None:
    """Upgrade pip to latest version"""
    print_colored("\nUpgrading pip to latest version...", Colors.BLUE)
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "pip"])
        print_colored("Pip upgrade successful!", Colors.GREEN)
    except subprocess.CalledProcessError as e:
        print_colored(f"Failed to upgrade pip: {e}", Colors.FAIL)

def verify_installation(package: str, required_version: str) -> bool:
    """Verify that a package is installed with the correct version"""
    try:
        installed_version = pkg_resources.get_distribution(package).version
        if pkg_resources.parse_version(installed_version) < pkg_resources.parse_version(required_version):
            print_colored(
                f"Warning: {package} version {installed_version} is older than required version {required_version}",
                Colors.WARNING
            )
            return False
        print_colored(f"✓ {package} {installed_version} installed successfully", Colors.GREEN)
        return True
    except pkg_resources.DistributionNotFound:
        print_colored(f"✗ {package} not found", Colors.FAIL)
        return False
    except Exception as e:
        print_colored(f"Error verifying {package}: {e}", Colors.FAIL)
        return False

def install_requirements() -> None:
    """Install all required packages"""
    if not check_python_version():
        sys.exit(1)

    print_colored("\n=== PyDoctor Requirements Installer ===", Colors.HEADER)
    
    # Upgrade pip first
    upgrade_pip()

    requirements = get_requirements()
    failed_installations = []

    print_colored("\nInstalling required packages...", Colors.BLUE)
    for package, version in requirements:
        try:
            print_colored(f"\nInstalling {package} (>={version})...", Colors.BLUE)
            subprocess.check_call([
                sys.executable, "-m", "pip", "install", 
                f"{package}>={version}", "--upgrade"
            ])
            
            # Verify installation
            if not verify_installation(package, version):
                failed_installations.append(package)
                
        except subprocess.CalledProcessError as e:
            print_colored(f"Failed to install {package}: {e}", Colors.FAIL)
            failed_installations.append(package)
        except Exception as e:
            print_colored(f"Unexpected error installing {package}: {e}", Colors.FAIL)
            failed_installations.append(package)

    # Installation summary
    print_colored("\n=== Installation Summary ===", Colors.HEADER)
    if failed_installations:
        print_colored(
            f"\nFailed to install the following packages: {', '.join(failed_installations)}", 
            Colors.FAIL
        )
        print_colored(
            "Please try installing these packages manually or check your internet connection.",
            Colors.WARNING
        )
        sys.exit(1)
    else:
        print_colored("\nAll requirements installed successfully! 🎉", Colors.GREEN)
        print_colored(
            "\nYou can now run PyDoctor using: python src/troubleshoot.py", 
            Colors.BLUE
        )

def main():
    """Main function to handle requirement installation"""
    try:
        install_requirements()
    except KeyboardInterrupt:
        print_colored("\nInstallation cancelled by user.", Colors.FAIL)
        sys.exit(1)
    except Exception as e:
        print_colored(f"\nUnexpected error: {e}", Colors.FAIL)
        sys.exit(1)

if __name__ == "__main__":
    main()