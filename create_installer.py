"""
Document Manager - Single File Installer Creator
This script creates a self-contained installer executable.
"""

import os
import shutil
import subprocess
import sys

def create_installer():
    """Create a single-file installer using PyInstaller."""

    print("=" * 60)
    print("Document Manager Installer Creator")
    print("=" * 60)

    # First, ensure PyInstaller is installed
    print("\n[1/5] Checking PyInstaller...")
    try:
        import PyInstaller
        print("[OK] PyInstaller is installed")
    except ImportError:
        print("Installing PyInstaller...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
        print("[OK] PyInstaller installed")

    # Create the installer script
    print("\n[2/5] Creating installer script...")
    installer_script = """
import os
import sys
import shutil
import subprocess
import zipfile
import tkinter as tk
from tkinter import messagebox, filedialog
from pathlib import Path
import tempfile

def extract_embedded_data(dest_path):
    '''Extract embedded application data to destination.'''
    # The embedded data will be in _MEIPASS when running as PyInstaller bundle
    if getattr(sys, 'frozen', False):
        bundle_dir = sys._MEIPASS
    else:
        bundle_dir = os.path.dirname(os.path.abspath(__file__))

    # Copy all files from bundle to destination
    app_data = os.path.join(bundle_dir, 'app_data')
    if os.path.exists(app_data):
        shutil.copytree(app_data, dest_path, dirs_exist_ok=True)
        return True
    return False

def install_dependencies(install_path):
    '''Install Python dependencies.'''
    req_file = os.path.join(install_path, 'requirements.txt')
    if os.path.exists(req_file):
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', req_file])
        return True
    return False

def create_shortcuts(install_path):
    '''Create desktop and start menu shortcuts.'''
    try:
        # Create a batch file to launch the application
        batch_content = f'''@echo off
cd /d "{install_path}"
python run_v2_3.py
pause
'''
        batch_path = os.path.join(install_path, 'Launch_Document_Manager.bat')
        with open(batch_path, 'w') as f:
            f.write(batch_content)

        # Create desktop shortcut
        desktop = os.path.join(os.path.expanduser('~'), 'Desktop')
        if os.path.exists(desktop):
            shortcut_path = os.path.join(desktop, 'Document Manager.bat')
            shutil.copy(batch_path, shortcut_path)

        return True
    except Exception as e:
        print(f"Warning: Could not create shortcuts: {e}")
        return False

class InstallerGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Document Manager Installer")
        self.root.geometry("500x400")
        self.root.resizable(False, False)

        # Installation path
        self.install_path = tk.StringVar(value=os.path.join(os.path.expanduser('~'), 'Document Manager'))

        self.create_widgets()

    def create_widgets(self):
        # Title
        title = tk.Label(self.root, text="Document Manager Installer",
                        font=('Arial', 16, 'bold'))
        title.pack(pady=20)

        # Description
        desc = tk.Label(self.root,
                       text="This will install Document Manager on your computer.\\n" +
                            "The application requires Python and will install\\n" +
                            "necessary dependencies automatically.\\n\\n" +
                            "For network/shared installations, install to a\\n" +
                            "network share location and configure db_path\\n" +
                            "in settings_v2_3.json after installation.",
                       justify=tk.LEFT)
        desc.pack(pady=10)

        # Installation path frame
        path_frame = tk.LabelFrame(self.root, text="Installation Location",
                                  padx=10, pady=10)
        path_frame.pack(padx=20, pady=20, fill=tk.BOTH)

        path_entry = tk.Entry(path_frame, textvariable=self.install_path,
                            width=50)
        path_entry.pack(side=tk.LEFT, padx=5)

        browse_btn = tk.Button(path_frame, text="Browse...",
                              command=self.browse_path)
        browse_btn.pack(side=tk.LEFT)

        # Options frame
        options_frame = tk.LabelFrame(self.root, text="Options",
                                     padx=10, pady=10)
        options_frame.pack(padx=20, pady=10, fill=tk.BOTH)

        self.create_shortcuts_var = tk.BooleanVar(value=True)
        shortcuts_cb = tk.Checkbutton(options_frame,
                                     text="Create desktop shortcut",
                                     variable=self.create_shortcuts_var)
        shortcuts_cb.pack(anchor=tk.W)

        self.install_deps_var = tk.BooleanVar(value=True)
        deps_cb = tk.Checkbutton(options_frame,
                                text="Install Python dependencies",
                                variable=self.install_deps_var)
        deps_cb.pack(anchor=tk.W)

        # Buttons
        btn_frame = tk.Frame(self.root)
        btn_frame.pack(pady=20)

        install_btn = tk.Button(btn_frame, text="Install",
                               command=self.install,
                               width=15, bg='#4CAF50', fg='white',
                               font=('Arial', 10, 'bold'))
        install_btn.pack(side=tk.LEFT, padx=5)

        cancel_btn = tk.Button(btn_frame, text="Cancel",
                              command=self.root.quit,
                              width=15)
        cancel_btn.pack(side=tk.LEFT, padx=5)

    def browse_path(self):
        path = filedialog.askdirectory(initialdir=self.install_path.get())
        if path:
            self.install_path.set(path)

    def install(self):
        install_path = self.install_path.get()

        # Create progress window
        progress_window = tk.Toplevel(self.root)
        progress_window.title("Installing...")
        progress_window.geometry("400x200")
        progress_window.resizable(False, False)

        status_label = tk.Label(progress_window, text="Starting installation...",
                               font=('Arial', 10))
        status_label.pack(pady=20)

        log_text = tk.Text(progress_window, height=8, width=50)
        log_text.pack(padx=10, pady=10)

        def update_status(message):
            log_text.insert(tk.END, message + "\\n")
            log_text.see(tk.END)
            progress_window.update()

        try:
            # Create installation directory
            update_status(f"Creating directory: {install_path}")
            os.makedirs(install_path, exist_ok=True)

            # Extract files
            update_status("Extracting application files...")
            if extract_embedded_data(install_path):
                update_status("[OK] Files extracted successfully")
            else:
                raise Exception("Failed to extract application files")

            # Install dependencies
            if self.install_deps_var.get():
                update_status("Installing Python dependencies...")
                update_status("(This may take a few minutes)")
                if install_dependencies(install_path):
                    update_status("[OK] Dependencies installed")
                else:
                    update_status("[WARNING] Could not install dependencies")

            # Create shortcuts
            if self.create_shortcuts_var.get():
                update_status("Creating shortcuts...")
                if create_shortcuts(install_path):
                    update_status("[OK] Shortcuts created")

            update_status("")
            update_status("=" * 40)
            update_status("Installation completed successfully!")
            update_status("=" * 40)

            messagebox.showinfo("Success",
                              f"Document Manager has been installed to:\\n{install_path}\\n\\n" +
                              "You can now launch it from the desktop shortcut or by running:\\n" +
                              f"{os.path.join(install_path, 'Launch_Document_Manager.bat')}\\n\\n" +
                              "For shared/network installations:\\n" +
                              "Edit settings_v2_3.json and set db_path to a network location\\n" +
                              "Example: \\\\\\\\SERVER\\\\Shared\\\\DocumentManager\\\\document_manager_v2.1.db")

            progress_window.destroy()
            self.root.quit()

        except Exception as e:
            update_status(f"ERROR: {str(e)}")
            messagebox.showerror("Installation Failed",
                               f"Installation failed with error:\\n{str(e)}")
            progress_window.destroy()

    def run(self):
        self.root.mainloop()

if __name__ == '__main__':
    app = InstallerGUI()
    app.run()
"""

    with open('installer_main.py', 'w', encoding='utf-8') as f:
        f.write(installer_script)
    print("[OK] Installer script created")

    # Create app_data directory with all necessary files
    print("\n[3/5] Preparing application files...")
    app_data_dir = 'app_data'
    if os.path.exists(app_data_dir):
        shutil.rmtree(app_data_dir)
    os.makedirs(app_data_dir)

    # List of files and directories to include
    items_to_copy = [
        'run_v2_3.py',
        'requirements.txt',
        'settings_v2_3.json',
        'settings_v2_3_network_example.json',
        'settings_v2_3_onedrive_example.json',
        'print_presets.json',
        'src/',
        'LABEL TEMPLATE/',
        'README.md',
        'sample csv/',
        'samples/',
        'QUICK_START.txt',
        'PRINTING_GUIDE.md',
        'WORK_MACHINE_QUICKSTART.md',
        'SHARED_DATABASE_SETUP.md',
        'NETWORK_DEPLOYMENT_SETUP_GUIDE.md',
        'ONEDRIVE_DEPLOYMENT_GUIDE.md',
        'ONEDRIVE_QUICK_START.md',
        'ONEDRIVE_LOCATION_GUIDE.md',
        'TEAMS_DEPLOYMENT_GUIDE.md',
        'PORTABLE_PYTHON_SETUP.md',
        'PORTABLE_SETUP_COMPLETE.txt',
        'SETUP_PYTHON_DEPS.bat',
        'START_APP.bat',
        'STARTUP_PORTABLE.bat',
        'DEPLOY_TO_ONEDRIVE.bat',
        'python-embedded/'
    ]

    copied_count = 0
    for item in items_to_copy:
        if os.path.exists(item):
            dest = os.path.join(app_data_dir, item)
            if os.path.isdir(item):
                shutil.copytree(item, dest, dirs_exist_ok=True)
            else:
                os.makedirs(os.path.dirname(dest), exist_ok=True)
                shutil.copy2(item, dest)
            copied_count += 1
            print(f"  [OK] Copied: {item}")
        else:
            print(f"  [SKIP] Not found: {item}")

    print(f"\n[OK] Prepared {copied_count} items")

    # Create PyInstaller spec file
    print("\n[4/5] Creating PyInstaller specification...")
    spec_content = """# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['installer_main.py'],
    pathex=[],
    binaries=[],
    datas=[('app_data', 'app_data')],
    hiddenimports=['tkinter', 'tkinter.filedialog', 'tkinter.messagebox'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='DocumentManager_Installer',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None
)
"""

    with open('installer.spec', 'w', encoding='utf-8') as f:
        f.write(spec_content)
    print("[OK] Specification created")

    # Build the installer
    print("\n[5/5] Building single-file installer...")
    print("This may take several minutes...\n")

    subprocess.check_call([sys.executable, '-m', 'PyInstaller',
                          '--clean', 'installer.spec'])

    print("\n" + "=" * 60)
    print("SUCCESS! Installer created successfully!")
    print("=" * 60)
    print("\nInstaller location:")
    installer_path = os.path.join('dist', 'DocumentManager_Installer.exe')
    if os.path.exists(installer_path):
        full_path = os.path.abspath(installer_path)
        size_mb = os.path.getsize(installer_path) / (1024 * 1024)
        print(f"  {full_path}")
        print(f"  Size: {size_mb:.1f} MB")
        print("\nYou can now distribute this single .exe file!")
        print("When users run it, they'll get a GUI installer.")
    else:
        print("  ERROR: Installer was not created!")

    # Cleanup
    print("\nCleaning up temporary files...")
    try:
        if os.path.exists('app_data'):
            shutil.rmtree('app_data')
        if os.path.exists('build'):
            shutil.rmtree('build')
        if os.path.exists('installer_main.py'):
            os.remove('installer_main.py')
        if os.path.exists('installer.spec'):
            os.remove('installer.spec')
        print("[OK] Cleanup complete")
    except Exception as e:
        print(f"[WARNING] Cleanup warning: {e}")

    print("\n" + "=" * 60)

if __name__ == '__main__':
    try:
        create_installer()
    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
