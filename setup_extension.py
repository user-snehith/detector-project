#!/usr/bin/env python
"""
Setup script for Phishing URL Detector Chrome Extension
This script helps you set up the complete phishing detection system.
"""

import os
import sys
import subprocess
import webbrowser
from pathlib import Path

def print_header():
    print("=" * 70)
    print("🎯 PHISHING URL DETECTOR - CHROME EXTENSION SETUP")
    print("=" * 70)
    print()

def check_python_version():
    """Check if Python version is compatible"""
    print("📋 Checking Python version...")
    version = sys.version_info
    if version.major == 3 and version.minor >= 8:
        print(f"✅ Python {version.major}.{version.minor}.{version.micro} - Compatible")
        return True
    else:
        print(f"❌ Python {version.major}.{version.minor}.{version.micro} - Requires Python 3.8+")
        return False

def install_dependencies():
    """Install required Python packages"""
    print("\n📦 Installing Python dependencies...")
    requirements = [
        "streamlit",
        "scikit-learn",
        "tensorflow",
        "pandas",
        "numpy",
        "tldextract",
        "plotly",
        "joblib"
    ]

    try:
        import subprocess
        for package in requirements:
            print(f"Installing {package}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", package, "-q"])
        print("✅ All dependencies installed")
        return True
    except Exception as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False

def setup_detector():
    """Set up the phishing detector"""
    print("\n🔧 Setting up phishing detector...")

    detector_dir = Path(__file__).parent
    os.chdir(detector_dir)

    # Check if models exist
    model_path = detector_dir / "models" / "sklearn_model.joblib"
    if model_path.exists():
        print("✅ Trained model found")
        return True

    print("⚠️  No trained model found. Training a new one...")

    try:
        # Import and train model
        sys.path.insert(0, str(detector_dir))
        from src import ModelTrainer

        print("Training Scikit-Learn model...")
        result = ModelTrainer.train_sklearn_model(
            data_path=None,  # Use default dataset
            output_path=str(model_path)
        )

        print(f"✅ Model trained with {result['accuracy']:.2%} accuracy")
        return True

    except Exception as e:
        print(f"❌ Failed to train model: {e}")
        return False

def setup_chrome_extension():
    """Set up the Chrome extension"""
    print("\n🌐 Setting up Chrome extension...")

    extension_dir = Path(__file__).parent / "chrome_extension"

    # Generate icons
    icon_script = extension_dir / "generate_icons.py"
    if icon_script.exists():
        print("Generating extension icons...")
        try:
            subprocess.check_call([sys.executable, str(icon_script)])
            print("✅ Extension icons generated")
        except Exception as e:
            print(f"⚠️  Icon generation failed: {e}")

    # Check manifest
    manifest = extension_dir / "manifest.json"
    if manifest.exists():
        print("✅ Extension manifest found")
    else:
        print("❌ Extension manifest missing")
        return False

    return True

def start_detector():
    """Start the Streamlit detector"""
    print("\n🚀 Starting phishing detector...")

    detector_dir = Path(__file__).parent
    os.chdir(detector_dir)

    try:
        print("Opening detector in browser...")
        print("URL: http://localhost:8501")
        print("Press Ctrl+C in terminal to stop the server")
        print()

        # Start Streamlit
        subprocess.run([
            sys.executable, "-m", "streamlit", "run",
            "frontend/app.py", "--server.port", "8501"
        ])

    except KeyboardInterrupt:
        print("\n🛑 Detector stopped")
    except Exception as e:
        print(f"❌ Failed to start detector: {e}")

def show_chrome_setup():
    """Show Chrome extension installation instructions"""
    print("\n" + "=" * 70)
    print("🔧 CHROME EXTENSION INSTALLATION")
    print("=" * 70)
    print()
    print("To install the Chrome extension:")
    print()
    print("1. Open Chrome and go to: chrome://extensions/")
    print("2. Enable 'Developer mode' (top right toggle)")
    print("3. Click 'Load unpacked' button")
    print("4. Select this folder: chrome_extension")
    print("5. The extension should now appear in your toolbar")
    print()
    print("Test it by:")
    print("- Clicking the extension icon")
    print("- Visiting any website and clicking links")
    print("- The extension will check suspicious URLs")
    print()
    print("=" * 70)

def main():
    print_header()

    # Run setup steps
    steps = [
        ("Python Version Check", check_python_version),
        ("Install Dependencies", install_dependencies),
        ("Setup Detector", setup_detector),
        ("Setup Chrome Extension", setup_chrome_extension),
    ]

    all_passed = True
    for step_name, step_func in steps:
        print(f"\n🔄 {step_name}...")
        if not step_func():
            all_passed = False
            print(f"❌ {step_name} failed")
        else:
            print(f"✅ {step_name} completed")

    if all_passed:
        print("\n" + "=" * 70)
        print("🎉 SETUP COMPLETE!")
        print("=" * 70)
        print()
        print("Your phishing detector is ready!")
        print()

        show_chrome_setup()

        # Ask if user wants to start the detector
        try:
            response = input("Start the phishing detector now? (y/n): ").lower().strip()
            if response in ['y', 'yes']:
                start_detector()
            else:
                print("\nTo start later, run:")
                print("streamlit run frontend/app.py")
        except KeyboardInterrupt:
            print("\nSetup cancelled")

    else:
        print("\n❌ Setup failed. Please fix the errors above and try again.")
        sys.exit(1)

if __name__ == "__main__":
    main()