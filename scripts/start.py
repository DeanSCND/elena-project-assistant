#!/usr/bin/env python3
"""
Cross-platform startup script for Construction Agent POC
Works on Windows, macOS, and Linux
"""

import os
import sys
import subprocess
import time
import webbrowser
import shutil
import platform
import signal
from pathlib import Path

# Colors for terminal output
class Colors:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    NC = '\033[0m'  # No Color

    @staticmethod
    def disable():
        Colors.RED = ''
        Colors.GREEN = ''
        Colors.YELLOW = ''
        Colors.BLUE = ''
        Colors.NC = ''

# Disable colors on Windows if not in modern terminal
if platform.system() == 'Windows' and not os.environ.get('WT_SESSION'):
    Colors.disable()

def print_status(message):
    print(f"{Colors.GREEN}✓{Colors.NC} {message}")

def print_error(message):
    print(f"{Colors.RED}✗{Colors.NC} {message}")

def print_warning(message):
    print(f"{Colors.YELLOW}⚠{Colors.NC} {message}")

def print_header(message):
    print(f"\n{Colors.BLUE}{message}{Colors.NC}")

def command_exists(command):
    """Check if a command exists in PATH"""
    return shutil.which(command) is not None

def check_port_available(port=8000):
    """Check if a port is available"""
    import socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(('127.0.0.1', port))
    sock.close()
    return result != 0

def kill_process_on_port(port=8000):
    """Kill process using the specified port"""
    system = platform.system()
    try:
        if system == 'Windows':
            # Find and kill process on Windows
            result = subprocess.run(
                f'netstat -ano | findstr :{port}',
                shell=True,
                capture_output=True,
                text=True
            )
            if result.stdout:
                lines = result.stdout.strip().split('\n')
                for line in lines:
                    if 'LISTENING' in line:
                        pid = line.strip().split()[-1]
                        subprocess.run(f'taskkill /F /PID {pid}', shell=True)
                        return True
        else:
            # Unix-like systems
            result = subprocess.run(
                f'lsof -ti:{port}',
                shell=True,
                capture_output=True,
                text=True
            )
            if result.stdout:
                pid = result.stdout.strip()
                subprocess.run(f'kill -9 {pid}', shell=True)
                return True
    except Exception as e:
        print_error(f"Failed to kill process: {e}")
    return False

def main():
    # Get directories
    script_dir = Path(__file__).parent.absolute()
    project_root = script_dir.parent
    backend_dir = project_root / 'backend'
    frontend_dir = project_root / 'frontend'
    aurora_dir = project_root.parent / 'Aurora (Safeway) Regina, SK'
    env_file = project_root / '.env'
    env_example = project_root / '.env.example'

    print(f"{Colors.BLUE}🏗️  Construction Agent POC - Startup Script{Colors.NC}")
    print(f"{Colors.BLUE}==========================================={Colors.NC}")

    # 1. Check Python version
    print_header("Step 1: Checking Python installation...")
    python_version = sys.version_info
    print_status(f"Python {python_version.major}.{python_version.minor}.{python_version.micro} found")

    if python_version.major == 3 and python_version.minor >= 11:
        print_status("Python version meets requirements (3.11+)")
    else:
        print_warning(f"Python 3.11+ recommended, you have {python_version.major}.{python_version.minor}")

    # 2. Check/Install Poetry
    print_header("Step 2: Checking Poetry installation...")
    if command_exists('poetry'):
        result = subprocess.run(['poetry', '--version'], capture_output=True, text=True)
        version = result.stdout.strip()
        print_status(f"Poetry {version} found")
    else:
        print_warning("Poetry not found. Installing Poetry...")
        if platform.system() == 'Windows':
            install_cmd = '(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | py -'
            subprocess.run(['powershell', '-Command', install_cmd], shell=False)
        else:
            install_cmd = 'curl -sSL https://install.python-poetry.org | python3 -'
            subprocess.run(install_cmd, shell=True)

        # Add Poetry to PATH
        home = Path.home()
        poetry_bin = home / '.local' / 'bin' / 'poetry'
        if poetry_bin.exists():
            os.environ['PATH'] = f"{poetry_bin.parent}:{os.environ['PATH']}"
            print_status("Poetry installed successfully")
        else:
            print_error("Failed to install Poetry. Please install manually:")
            print("  curl -sSL https://install.python-poetry.org | python3 -")
            sys.exit(1)

    # 3. Check for .env file
    print_header("Step 3: Checking environment configuration...")
    if env_file.exists():
        print_status(".env file found")

        # Check for OpenAI API key
        with open(env_file, 'r') as f:
            env_content = f.read()

        if 'OPENAI_API_KEY=sk-' in env_content:
            print_status("OpenAI API key configured")
        else:
            print_warning("OpenAI API key not found or invalid in .env")
            response = input("\nWould you like to add it now? (y/n): ")
            if response.lower() == 'y':
                api_key = input("Enter your OpenAI API key: ")
                with open(env_file, 'a') as f:
                    f.write(f"\nOPENAI_API_KEY={api_key}\n")
                print_status("API key added to .env")
            else:
                print_warning("Continuing without API key (chat won't work)")
    else:
        print_warning(".env file not found. Creating from template...")
        shutil.copy(env_example, env_file)
        print_status(".env file created from template")

        response = input("\nWould you like to add your OpenAI API key now? (y/n): ")
        if response.lower() == 'y':
            api_key = input("Enter your OpenAI API key: ")
            with open(env_file, 'r') as f:
                content = f.read()
            content = content.replace('sk-your-openai-api-key-here', api_key)
            with open(env_file, 'w') as f:
                f.write(content)
            print_status("API key added to .env")
        else:
            print_warning("Continuing without API key (chat won't work)")

    # 4. Check Aurora documents
    print_header("Step 4: Checking Aurora project documents...")
    if aurora_dir.exists():
        ai_files = list(aurora_dir.glob('**/*.AI.md'))
        md_files = list(aurora_dir.glob('**/*.md'))
        print_status("Aurora project folder found")
        print_status(f"Found {len(ai_files)} AI analysis files")
        print_status(f"Found {len(md_files)} total markdown files")
    else:
        print_error(f"Aurora project folder not found at:\n  {aurora_dir}")
        print("\nThe agent needs the Aurora documents to function.")
        print("Please ensure the Aurora folder exists in the parent directory.")
        sys.exit(1)

    # 5. Install Python dependencies
    print_header("Step 5: Installing Python dependencies with Poetry...")
    os.chdir(backend_dir)

    result = subprocess.run(['poetry', 'install', '--no-interaction'], capture_output=True)
    if result.returncode == 0:
        print_status("Python dependencies installed")
    else:
        print_error("Failed to install dependencies")
        print(result.stderr.decode())
        sys.exit(1)

    # 6. Check if port is available
    print_header("Step 6: Checking port availability...")

    # Default to port 8100 to avoid conflicts with common services
    DEFAULT_PORT = 8100
    port = DEFAULT_PORT

    if not check_port_available(port):
        print_warning(f"Port {port} is already in use")
        print("\nOptions:")
        print("  1. Kill the existing process")
        print("  2. Use a different port")
        print("  3. Cancel")
        choice = input("Choose (1/2/3): ").strip()

        if choice == '1':
            if kill_process_on_port(port):
                print_status(f"Killed process on port {port}")
                time.sleep(1)
            else:
                print_error("Failed to kill process")
                sys.exit(1)
        elif choice == '2':
            try:
                new_port = input("Enter port number (e.g., 8101): ").strip()
                port = int(new_port)
                print_status(f"Will use port {port}")
            except ValueError:
                print_error("Invalid port number")
                sys.exit(1)
        else:
            print("Cancelled")
            sys.exit(0)
    else:
        print_status(f"Port {port} is available")

    # 7. Start the backend server
    print_header("Step 7: Starting the backend server...")
    print("=" * 40)

    server_url = f"http://localhost:{port}"
    print(f"Starting server on port {port}...")

    # Start server as subprocess
    server_cmd = [
        'poetry', 'run', 'uvicorn',
        'app:app',
        '--reload',
        '--host', '0.0.0.0',
        '--port', str(port)
    ]

    server_process = subprocess.Popen(
        server_cmd,
        cwd=backend_dir,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

    # Wait for server to start
    print("Waiting for server to start...")
    for i in range(10):
        time.sleep(1)
        try:
            import urllib.request
            urllib.request.urlopen(f"{server_url}/health")
            print_status("Backend server is running")
            break
        except:
            if i == 9:
                print_warning("Server might still be starting...")

    # 8. Update frontend configuration
    print_header("Step 8: Configuring frontend...")

    frontend_path = frontend_dir / 'index.html'

    # Update frontend API URL to use the correct port
    app_js_path = frontend_dir / 'app.js'
    if app_js_path.exists():
        with open(app_js_path, 'r') as f:
            js_content = f.read()

        # Update the API_BASE constant
        import re
        js_content = re.sub(
            r"const API_BASE = 'http://localhost:\d+'",
            f"const API_BASE = 'http://localhost:{port}'",
            js_content
        )

        with open(app_js_path, 'w') as f:
            f.write(js_content)

        print_status(f"Updated frontend to use port {port}")

    # 9. Open the frontend
    print_header("Step 9: Opening the chat interface...")
    print("=" * 40)

    frontend_url = f"file://{frontend_path}"

    webbrowser.open(frontend_url)
    print_status("Opened chat interface in browser")

    # Final instructions
    print(f"\n{Colors.GREEN}{'='*50}{Colors.NC}")
    print(f"{Colors.GREEN}🎉 Construction Agent POC is running!{Colors.NC}")
    print(f"{Colors.GREEN}{'='*50}{Colors.NC}\n")
    print(f"📍 Backend API: {server_url}")
    print(f"💬 Chat Interface: {frontend_url}\n")
    print("Example queries to try:")
    print("  • What's the ceiling height in meat prep?")
    print("  • Is there a conflict between trellis and HVAC?")
    print("  • What are the grid dimensions?")
    print("  • Who is the general contractor?\n")
    print(f"{Colors.YELLOW}Press Ctrl+C to stop the server{Colors.NC}\n")

    # Handle shutdown gracefully
    def shutdown(signum, frame):
        print(f"\n{Colors.YELLOW}Shutting down server...{Colors.NC}")
        server_process.terminate()
        time.sleep(1)
        if server_process.poll() is None:
            server_process.kill()
        sys.exit(0)

    signal.signal(signal.SIGINT, shutdown)
    if platform.system() != 'Windows':
        signal.signal(signal.SIGTERM, shutdown)

    # Wait for server process
    try:
        server_process.wait()
    except KeyboardInterrupt:
        shutdown(None, None)

if __name__ == "__main__":
    main()