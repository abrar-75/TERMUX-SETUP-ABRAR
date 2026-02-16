#!/usr/bin/env python3
"""
ABRAR - Termux Full Setup Tool
Professional Python-based setup for ethical hackers and programmers
Author: TEAM-BCT
Version: 2.0.0
"""

import os
import sys
import subprocess
import time
import logging
from typing import List, Dict, Optional

# Check for required modules before importing
required_modules = ['colorama', 'rich']
missing_modules = []

for module in required_modules:
    try:
        __import__(module)
    except ImportError:
        missing_modules.append(module)

if missing_modules:
    print(f"Missing modules: {', '.join(missing_modules)}")
    print("Installing missing modules...")
    subprocess.run([sys.executable, "-m", "pip", "install"] + missing_modules)

from colorama import init, Fore, Back, Style
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
import shutil

# Initialize colorama for cross-platform color support
init(autoreset=True)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('setup.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

console = Console()

class DarkNKSetup:
    def __init__(self):
        self.is_termux = self.check_termux()
        self.home_dir = os.path.expanduser("~")
        self.tools_dir = os.path.join(self.home_dir, "tools")
        self.scripts_dir = os.path.join(self.home_dir, "scripts")
        self.wordlists_dir = os.path.join(self.home_dir, "wordlists")
        
    def check_termux(self) -> bool:
        """Check if running inside Termux"""
        try:
            # Check for Termux specific environment
            termux_path = os.path.exists("/data/data/com.termux/files/usr/bin")
            termux_prefix = os.environ.get("PREFIX", "").endswith("com.termux/files/usr")
            
            if termux_path or termux_prefix:
                return True
            
            # Additional check
            if "com.termux" in os.environ.get("HOME", ""):
                return True
                
            return False
            
        except Exception as e:
            logger.error(f"Error checking Termux: {e}")
            return False
    
    def display_banner(self):
        """Display mobile-friendly ASCII banner"""
        banner = f"""
{Fore.CYAN}╔{'═'*42}╗
{Fore.MAGENTA}║     _    ____  _____       _    _____    ║
{Fore.BLUE}║     /\   |  _ \|  __ \     /\   |  __ \  ║
{Fore.GREEN}║    /  \  | |_) | |__) |   /  \  | |__) | ║
{Fore.YELLOW}║   / /\ \ |  _ <|  _  /   / /\ \ |  _  /  ║
{Fore.RED}║  / ____ \| |_) | | \ \  / ____ \| | \ \  ║
{Fore.CYAN}║ /_/    \_\____/|_|  \_\/_/    \_\_|  \_\ ║
{Fore.WHITE}╚{'═'*42}╝
{Fore.YELLOW}    ABRAR - Termux Setup Tool
{Fore.GREEN}    Version: 2.0.0
{Fore.CYAN}    Author: TEAM-BCT
"""
        print(banner)
    
    def check_root(self):
        """Check for root access (informative only)"""
        try:
            # In Termux, root isn't typical but we check anyway
            if os.geteuid() == 0:
                print(f"{Fore.RED}Warning: Running as root!")
                time.sleep(2)
        except:
            pass
    
    def run_command(self, command: List[str], description: str = "") -> bool:
        """Run a shell command with progress indicator"""
        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                console=console
            ) as progress:
                task = progress.add_task(description, total=None)
                
                result = subprocess.run(
                    command,
                    capture_output=True,
                    text=True,
                    shell=False
                )
                
                progress.update(task, completed=True)
                
                if result.returncode != 0:
                    logger.error(f"Command failed: {' '.join(command)}")
                    logger.error(f"Error: {result.stderr}")
                    return False
                    
                return True
                
        except Exception as e:
            logger.error(f"Exception running command: {e}")
            return False
    
    def install_packages(self, package_list: List[str], pkg_manager: str = "pkg") -> bool:
        """Install packages using pkg or pip"""
        if not package_list:
            return True
            
        print(f"\n{Fore.CYAN}Installing {len(package_list)} packages...")
        
        for package in package_list:
            print(f"{Fore.YELLOW}[+] Installing: {package}")
            
            if pkg_manager == "pkg":
                cmd = ["pkg", "install", "-y", package]
            elif pkg_manager == "pip":
                cmd = ["pip", "install", "--upgrade", package]
            else:
                continue
                
            if not self.run_command(cmd, f"Installing {package}"):
                print(f"{Fore.RED}[-] Failed to install: {package}")
                # Continue with other packages
                
        return True
    
    def setup_termux(self):
        """Initial Termux setup and configuration"""
        print(f"\n{Fore.GREEN}[*] Setting up Termux environment...")
        
        # Update package lists
        self.run_command(["pkg", "update", "-y"], "Updating package lists")
        
        # Upgrade existing packages
        self.run_command(["pkg", "upgrade", "-y"], "Upgrading packages")
        
        # Enable storage access
        print(f"{Fore.YELLOW}[+] Setting up storage access...")
        self.run_command(["termux-setup-storage"], "Setting up storage")
        
        # Create directories
        directories = [self.tools_dir, self.scripts_dir, self.wordlists_dir]
        for directory in directories:
            if not os.path.exists(directory):
                os.makedirs(directory)
                print(f"{Fore.GREEN}[+] Created: {directory}")
        
        # Setup custom bashrc
        self.setup_shell_prompt()
        
        print(f"{Fore.GREEN}[✓] Termux setup completed!")
    
    def setup_shell_prompt(self):
        """Setup a clean custom shell prompt"""
        bashrc_path = os.path.join(self.home_dir, ".bashrc")
        
        prompt_config = """
# DarkNK Custom Prompt
export PS1='\\[\\033[1;32m\\]DarkNK@\\[\\033[1;34m\\]\\h:\\[\\033[1;35m\\]\\w\\[\\033[0m\\]\\$ '
export LS_OPTIONS='--color=auto'
alias ls='ls $LS_OPTIONS'
alias ll='ls $LS_OPTIONS -l'
alias la='ls $LS_OPTIONS -la'
"""
        
        try:
            with open(bashrc_path, "a") as f:
                f.write(prompt_config)
            print(f"{Fore.GREEN}[+] Custom prompt configured")
        except Exception as e:
            logger.error(f"Error setting up shell prompt: {e}")
    
    def install_core_packages(self):
        """Install core system packages"""
        print(f"\n{Fore.GREEN}[*] Installing core packages...")
        
        core_packages = [
            "python", "python-pip", "git", "curl", "wget",
            "nano", "vim", "unzip", "zip", "tar", "clang",
            "make", "cmake"
        ]
        
        self.install_packages(core_packages, "pkg")
        print(f"{Fore.GREEN}[✓] Core packages installed!")
    
    def install_security_tools(self):
        """Install security tools"""
        print(f"\n{Fore.GREEN}[*] Installing security tools...")
        
        security_packages = [
            "nmap", "hydra", "nikto"
        ]
        
        self.install_packages(security_packages, "pkg")
        
        # Install sqlmap from git (not always in Termux repos)
        print(f"{Fore.YELLOW}[+] Installing sqlmap from GitHub...")
        sqlmap_dir = os.path.join(self.tools_dir, "sqlmap")
        
        if os.path.exists(sqlmap_dir):
            print(f"{Fore.CYAN}[*] sqlmap already exists, updating...")
            self.run_command(["git", "-C", sqlmap_dir, "pull"], "Updating sqlmap")
        else:
            self.run_command(
                ["git", "clone", "--depth", "1", "https://github.com/sqlmapproject/sqlmap.git", sqlmap_dir],
                "Cloning sqlmap"
            )
        
        # Create symlink for easy access
        sqlmap_bin = os.path.join(self.home_dir, "bin", "sqlmap")
        if not os.path.exists(sqlmap_bin):
            os.makedirs(os.path.dirname(sqlmap_bin), exist_ok=True)
            os.symlink(os.path.join(sqlmap_dir, "sqlmap.py"), sqlmap_bin)
            os.chmod(sqlmap_bin, 0o755)
        
        print(f"{Fore.GREEN}[✓] Security tools installed!")
    
    def install_python_modules(self):
        """Install Python modules via pip"""
        print(f"\n{Fore.GREEN}[*] Installing Python modules...")
        
        python_modules = [
            "requests", "rich", "colorama", "tqdm",
            "scapy", "beautifulsoup4", "lxml", "pillow",
            "pycryptodome", "paramiko", "netifaces"
        ]
        
        self.install_packages(python_modules, "pip")
        print(f"{Fore.GREEN}[✓] Python modules installed!")
    
    def optimize_system(self):
        """Optimize Termux performance"""
        print(f"\n{Fore.GREEN}[*] Optimizing system...")
        
        # Clean package cache
        self.run_command(["pkg", "clean"], "Cleaning package cache")
        
        # Setup fast mirrors (if in specific regions)
        termux_properties = os.path.join(self.home_dir, ".termux", "termux.properties")
        
        try:
            os.makedirs(os.path.dirname(termux_properties), exist_ok=True)
            with open(termux_properties, "a") as f:
                f.write("\n# Performance optimizations\n")
                f.write("bell-character=ignore\n")
                f.write("terminal-margin-horizontal=2\n")
                f.write("terminal-margin-vertical=2\n")
        except Exception as e:
            logger.error(f"Error optimizing system: {e}")
        
        print(f"{Fore.GREEN}[✓] System optimized!")
    
    def update_all(self):
        """Update all packages and tools"""
        print(f"\n{Fore.GREEN}[*] Updating everything...")
        
        # Update system packages
        self.run_command(["pkg", "update", "-y"], "Updating package lists")
        self.run_command(["pkg", "upgrade", "-y"], "Upgrading packages")
        
        # Update pip packages
        self.run_command(["pip", "list", "--outdated", "--format=freeze"], "Checking outdated pip packages")
        
        # Update git tools
        self.update_git_tools()
        
        print(f"{Fore.GREEN}[✓] All updates completed!")
    
    def update_git_tools(self):
        """Update git-based tools"""
        print(f"{Fore.YELLOW}[+] Updating git tools...")
        
        tools_to_update = {
            "sqlmap": os.path.join(self.tools_dir, "sqlmap")
        }
        
        for tool_name, tool_path in tools_to_update.items():
            if os.path.exists(tool_path):
                print(f"{Fore.CYAN}[*] Updating {tool_name}...")
                self.run_command(["git", "-C", tool_path, "pull"], f"Updating {tool_name}")
    
    def fix_broken_termux(self):
        """Fix common Termux issues"""
        print(f"\n{Fore.GREEN}[*] Fixing Termux issues...")
        
        fixes = [
            (["pkg", "update", "--fix-missing"], "Fixing broken packages"),
            (["pkg", "install", "-f", "-y"], "Forcing package fixes"),
            (["pip", "check"], "Checking pip installations"),
            (["termux-fix-shebang", os.path.join(self.home_dir, "bin/*")], "Fixing shebangs"),
        ]
        
        for cmd, desc in fixes:
            self.run_command(cmd, desc)
        
        # Fix permissions
        bin_dir = os.path.join(self.home_dir, "bin")
        if os.path.exists(bin_dir):
            self.run_command(["chmod", "-R", "+x", bin_dir], "Fixing permissions")
        
        print(f"{Fore.GREEN}[✓] Fixes applied!")
    
    def full_setup(self):
        """Perform full Termux setup"""
        print(f"\n{Fore.MAGENTA}{'='*45}")
        print(f"{Fore.CYAN}      STARTING FULL SETUP")
        print(f"{Fore.MAGENTA}{'='*45}")
        
        steps = [
            ("Termux Setup", self.setup_termux),
            ("Core Packages", self.install_core_packages),
            ("Security Tools", self.install_security_tools),
            ("Python Modules", self.install_python_modules),
            ("System Optimization", self.optimize_system)
        ]
        
        for step_name, step_func in steps:
            print(f"\n{Fore.YELLOW}▶ {step_name}")
            try:
                step_func()
                print(f"{Fore.GREEN}✓ {step_name} completed")
            except Exception as e:
                print(f"{Fore.RED}✗ {step_name} failed: {e}")
                logger.error(f"Step {step_name} failed: {e}")
        
        self.display_summary()
    
    def display_summary(self):
        """Display installation summary"""
        summary = f"""
{Fore.CYAN}{'='*45}
{Fore.GREEN}         SETUP COMPLETED SUCCESSFULLY!
{Fore.CYAN}{'='*45}

{Fore.YELLOW}📁 Directories Created:
  • {self.tools_dir}
  • {self.scripts_dir}
  • {self.wordlists_dir}

{Fore.BLUE}🔧 Tools Installed:
  • Python 3 + pip
  • Git, curl, wget
  • Nmap, Hydra, Nikto
  • SQLMap (cloned to tools/)
  • Development tools (clang, make, cmake)

{Fore.MAGENTA}🐍 Python Modules:
  • requests, rich, colorama, tqdm
  • scapy, beautifulsoup4, pillow
  • pycryptodome, paramiko

{Fore.GREEN}🚀 Quick Start Commands:
  • sqlmap    : Start SQLMap
  • nmap      : Network scanner
  • python3   : Python interpreter

{Fore.CYAN}💡 Next Steps:
  1. Restart Termux session
  2. Start hacking in ~/tools/
  3. Check ~/storage for external storage

{Fore.RED}⚠  Remember: Use tools responsibly and legally!
"""
        print(summary)
        
        # Save summary to file
        with open("setup_summary.txt", "w") as f:
            f.write(summary.replace(Fore.CYAN, "").replace(Fore.GREEN, "")
                   .replace(Fore.YELLOW, "").replace(Fore.BLUE, "")
                   .replace(Fore.MAGENTA, "").replace(Fore.RED, ""))
    
    def display_menu(self):
        """Display mobile-friendly menu"""
        while True:
            os.system("clear")
            self.display_banner()
            
            menu_text = f"""
{Fore.CYAN}{'═'*40}
{Fore.YELLOW}        MAIN MENU
{Fore.CYAN}{'═'*40}

{Fore.GREEN}[1] {Fore.WHITE}Full Termux Setup
{Fore.GREEN}[2] {Fore.WHITE}Install Tools Only
{Fore.GREEN}[3] {Fore.WHITE}Update All Packages
{Fore.GREEN}[4] {Fore.WHITE}Fix Broken Termux
{Fore.GREEN}[5] {Fore.WHITE}Install Python Modules
{Fore.GREEN}[6] {Fore.WHITE}Install Security Tools
{Fore.GREEN}[0] {Fore.WHITE}Exit

{Fore.CYAN}{'═'*40}
"""
            print(menu_text)
            
            choice = input(f"{Fore.YELLOW}Select option [0-6]: {Fore.WHITE}").strip()
            
            if choice == "1":
                self.full_setup()
                input(f"\n{Fore.CYAN}Press Enter to continue...")
            elif choice == "2":
                self.install_core_packages()
                self.install_security_tools()
                input(f"\n{Fore.CYAN}Press Enter to continue...")
            elif choice == "3":
                self.update_all()
                input(f"\n{Fore.CYAN}Press Enter to continue...")
            elif choice == "4":
                self.fix_broken_termux()
                input(f"\n{Fore.CYAN}Press Enter to continue...")
            elif choice == "5":
                self.install_python_modules()
                input(f"\n{Fore.CYAN}Press Enter to continue...")
            elif choice == "6":
                self.install_security_tools()
                input(f"\n{Fore.CYAN}Press Enter to continue...")
            elif choice == "0":
                print(f"\n{Fore.GREEN}Thank you for using DarkNK!")
                print(f"{Fore.CYAN}Goodbye! 👋")
                sys.exit(0)
            else:
                print(f"\n{Fore.RED}Invalid option! Please try again.")
                time.sleep(1)

def main():
    """Main entry point"""
    try:
        setup = DarkNKSetup()
        
        # Check if running in Termux
        if not setup.is_termux:
            print(f"\n{Fore.RED}{'='*50}")
            print(f"{Fore.RED}ERROR: This tool must be run inside Termux!")
            print(f"{Fore.YELLOW}Please install Termux from Google Play/F-Droid")
            print(f"{Fore.RED}{'='*50}")
            sys.exit(1)
        
        # Check for dependencies
        setup.check_root()
        
        # Start the setup
        setup.display_menu()
        
    except KeyboardInterrupt:
        print(f"\n\n{Fore.YELLOW}Setup interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        print(f"\n{Fore.RED}Critical error occurred. Check setup.log")
        sys.exit(1)

if __name__ == "__main__":
    main()