import subprocess, sys

def fix():
    # Step 1: Uninstall GUI opencv
    subprocess.run([sys.executable, '-m', 'pip', 'uninstall', '-y', 'opencv-python'],
                   capture_output=True)
    
    # Step 2: Install headless (without upgrading dependencies)
    subprocess.run([sys.executable, '-m', 'pip', 'install',
                   'opencv-python-headless==4.8.1.78',
                   '--no-deps',           # ← don't touch numpy or anything else
                   '--force-reinstall'],
                   capture_output=True)
    
    # Step 3: Pin numpy back to safe version
    subprocess.run([sys.executable, '-m', 'pip', 'install',
                   'numpy==1.26.4',
                   '--force-reinstall', '--quiet'],
                   capture_output=True)
    
    print("opencv fix applied, numpy pinned to 1.26.4")

if __name__ == '__main__':
    fix()