#!/usr/bin/env python3
"""
Auto-setup script for Document Manager v2.4 deployments
Creates folder structure, validates settings, and prepares for first run
"""

import os
import sys
import json
import shutil
from pathlib import Path


def print_header(text):
    """Print a formatted header"""
    print("\n" + "=" * 70)
    print(text)
    print("=" * 70)


def print_step(step_num, total, description):
    """Print a step header"""
    print(f"\n[{step_num}/{total}] {description}")
    print("-" * 70)


def check_and_create_settings(script_dir):
    """Check if settings exist, create from template if needed"""
    settings_file = script_dir / "settings_v2_4.json"
    template_file = script_dir / "settings_v2_4_template.json"

    if settings_file.exists():
        print(f"[OK] Settings file already exists: {settings_file.name}")
        print("     Using existing configuration.")

        # Validate it's valid JSON
        try:
            with open(settings_file, 'r') as f:
                settings = json.load(f)

            # Check for absolute paths
            warnings = []
            for key in ['html_path', 'pdf_path', 'archive_path', 'db_path', 'products_file_path']:
                if key in settings:
                    path = settings[key]
                    if path and (path.startswith('C:') or path.startswith('/')):
                        warnings.append(f"  - {key}: {path}")

            if warnings:
                print("\n[WARNING] Found absolute paths in settings:")
                for w in warnings:
                    print(w)
                print("     These may not work for other users!")
                print("     Consider using relative paths like: DATA\\BisTrack Exports")
        except json.JSONDecodeError:
            print("[WARNING] Settings file exists but is not valid JSON!")
        except Exception as e:
            print(f"[WARNING] Could not validate settings: {e}")

        return True

    elif template_file.exists():
        print(f"[SETUP] Creating settings from template...")
        try:
            shutil.copy(template_file, settings_file)
            print(f"[OK] Created {settings_file.name} from template.")
            return True
        except Exception as e:
            print(f"[ERROR] Failed to copy template: {e}")
            return False
    else:
        print(f"[ERROR] Template file '{template_file.name}' not found!")
        print("        Cannot create settings file.")
        return False


def create_data_folders(script_dir):
    """Create the DATA folder structure"""
    folders = [
        "DATA",
        "DATA/BisTrack Exports",
        "DATA/PDFs",
        "DATA/Archive"
    ]

    all_created = True
    for folder in folders:
        folder_path = script_dir / folder
        if not folder_path.exists():
            try:
                folder_path.mkdir(parents=True, exist_ok=True)
                print(f"[OK] Created: {folder}\\")
            except Exception as e:
                print(f"[ERROR] Failed to create {folder}\\: {e}")
                all_created = False
        else:
            print(f"[OK] Already exists: {folder}\\")

    return all_created


def validate_template(script_dir):
    """Check if Word template exists"""
    template_path = script_dir / "LABEL TEMPLATE" / "Contract_Lumber_Label_Template.docx"

    if template_path.exists():
        print(f"[OK] Label template found.")
        return True
    else:
        print(f"[WARNING] Label template not found at:")
        print(f"          {template_path}")
        print()
        print("          Label printing will not work until template is added.")
        print("          You can continue, but add the template before printing.")
        return False


def check_python_dependencies():
    """Check if required Python packages are available"""
    print("\nChecking Python dependencies...")

    required = {
        'PyQt5': 'PyQt5',
        'win32com': 'pywin32',
    }

    missing = []
    for module, package_name in required.items():
        try:
            __import__(module)
            print(f"  [OK] {package_name}")
        except ImportError:
            print(f"  [MISSING] {package_name}")
            missing.append(package_name)

    if missing:
        print()
        print("[WARNING] Missing required packages!")
        print("          Run: pip install " + " ".join(missing))
        return False

    return True


def check_deployment_location(script_dir):
    """Detect deployment location and provide info"""
    path_str = str(script_dir).lower()

    if 'onedrive' in path_str:
        print("[INFO] Detected OneDrive deployment")
        print("       Multiple users can access this installation.")
        print("       Each user will have their own settings after first run.")
        return "OneDrive"
    elif path_str.startswith('\\\\'):
        print("[INFO] Detected network share deployment")
        print("       Multiple users can access this installation.")
        return "Network"
    else:
        print("[INFO] Detected local deployment")
        print("       This installation is for this computer only.")
        return "Local"


def main():
    """Main setup routine"""
    print_header("Document Manager v2.4 - Auto Setup")
    print()
    print("This script will prepare the application for first-time use.")
    print("It will create necessary folders and configuration files.")

    script_dir = Path(__file__).parent.absolute()
    print(f"\nSetup location: {script_dir}")

    deployment_type = check_deployment_location(script_dir)

    input("\nPress Enter to continue...")

    # Step 1: Settings
    print_step(1, 5, "Checking settings file...")
    settings_ok = check_and_create_settings(script_dir)

    if not settings_ok:
        print("\n[FATAL] Cannot proceed without settings file!")
        input("\nPress Enter to exit...")
        return 1

    # Step 2: Folders
    print_step(2, 5, "Creating DATA folder structure...")
    folders_ok = create_data_folders(script_dir)

    # Step 3: Template
    print_step(3, 5, "Validating template files...")
    template_ok = validate_template(script_dir)

    # Step 4: Python check
    print_step(4, 5, "Checking Python installation...")
    print(f"Python version: {sys.version}")

    # Step 5: Dependencies
    print_step(5, 5, "Checking Python dependencies...")
    deps_ok = check_python_dependencies()

    # Summary
    print_header("Setup Complete!")

    print("\nFolder structure created:")
    print("  Document Manager\\")
    print("  ├── DATA\\")
    print("  │   ├── BisTrack Exports\\  (place HTML exports here)")
    print("  │   ├── PDFs\\              (generated labels saved here)")
    print("  │   └── Archive\\           (archived records stored here)")
    print("  ├── settings_v2_4.json     (your configuration)")
    print("  └── LABEL TEMPLATE\\")

    if not template_ok:
        print("\n[ACTION REQUIRED]")
        print("  Add the Word template before using label printing features.")

    if not deps_ok:
        print("\n[ACTION REQUIRED]")
        print("  Install missing Python packages before running the application:")
        print("  pip install PyQt5 pywin32")

    if deployment_type == "OneDrive":
        print("\n[ONEDRIVE DEPLOYMENT]")
        print("  Each user who runs this will get their own settings copy.")
        print("  The DATA folder and database will be shared between users.")
        print("  Close the app when not in use to prevent sync conflicts.")

    print("\n" + "=" * 70)

    if deps_ok:
        launch = input("\nReady to launch? (Y/n): ").strip().lower()
        if launch != 'n':
            print("\nLaunching Document Manager v2.4...")
            try:
                import subprocess
                subprocess.run([sys.executable, script_dir / "run_v2_4.py"])
            except Exception as e:
                print(f"[ERROR] Failed to launch: {e}")
                print("Try running: python run_v2_4.py")
                return 1
    else:
        print("\nInstall dependencies first, then run: python run_v2_4.py")

    return 0


if __name__ == "__main__":
    try:
        exit_code = main()
        input("\nPress Enter to exit...")
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\nSetup cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n[FATAL ERROR] {e}")
        import traceback
        traceback.print_exc()
        input("\nPress Enter to exit...")
        sys.exit(1)
