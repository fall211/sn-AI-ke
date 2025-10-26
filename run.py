
import os
import platform
import subprocess
import sys

def main():
    # Change to the directory where this script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    # Determine the OS and set appropriate commands
    system = platform.system()
    if system == 'Windows':
        pip_cmd = 'pip'
        python_cmd = 'python'
    else:  # Assuming macOS or Linux
        pip_cmd = 'pip3'
        python_cmd = 'python3'
    
    # Install dependencies
    print("Installing dependencies...")
    try:
        subprocess.check_call([pip_cmd, 'install', '-r', 'requirements.txt'])
        print("Dependencies installed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Failed to install dependencies: {e}")
        sys.exit(1)
    
    # Run the game
    print("Starting the game...")
    try:
        subprocess.run([python_cmd, 'main.py'])
    except subprocess.CalledProcessError as e:
        print(f"Failed to run the game: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()