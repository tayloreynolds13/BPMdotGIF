#!/usr/bin/env python3
"""
Test script to verify Streamlit app functionality
"""
import subprocess
import time
import requests
import sys

def test_streamlit_app():
    """Test if the Streamlit app starts and responds correctly"""
    print("Testing Streamlit GIF BPM Sync Tool...")
    
    try:
        # Start the app in the background
        process = subprocess.Popen([
            'streamlit', 'run', 'streamlit_app.py',
            '--server.headless', 'true',
            '--server.port', '8504'
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Wait a moment for the app to start
        time.sleep(5)
        
        # Test if the app is responding
        try:
            response = requests.get('http://localhost:8504', timeout=10)
            if response.status_code == 200:
                print("✅ Streamlit app is running successfully!")
                print("🌐 Local URL: http://localhost:8504")
                print("📱 You can now access the app in your browser")
                return True
            else:
                print(f"❌ App responded with status code: {response.status_code}")
                return False
        except requests.exceptions.RequestException as e:
            print(f"❌ Could not connect to app: {e}")
            return False
        finally:
            # Clean up
            process.terminate()
            process.wait()
            
    except Exception as e:
        print(f"❌ Error testing Streamlit app: {e}")
        return False

def test_dependencies():
    """Test if all required dependencies are available"""
    print("Checking dependencies...")
    
    required_packages = ['streamlit', 'pillow', 'pygame']
    missing = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package} is available")
        except ImportError:
            print(f"❌ {package} is missing")
            missing.append(package)
    
    if missing:
        print(f"\nInstall missing packages with:")
        print(f"pip install {' '.join(missing)}")
        return False
    
    return True

def main():
    print("🎵 GIF BPM Sync Tool - Streamlit Test")
    print("=" * 40)
    
    # Test dependencies
    print("\n1. Testing dependencies...")
    deps_ok = test_dependencies()
    
    if not deps_ok:
        print("\n❌ Dependencies test failed. Please install missing packages.")
        return
    
    # Test Streamlit app
    print("\n2. Testing Streamlit app...")
    app_ok = test_streamlit_app()
    
    print("\n" + "=" * 40)
    if app_ok:
        print("🎉 All tests passed! Your Streamlit app is ready to deploy.")
        print("\nNext steps:")
        print("1. Push to GitHub")
        print("2. Deploy on Streamlit Cloud")
        print("3. Share your live URL!")
    else:
        print("❌ Some tests failed. Please check the errors above.")

if __name__ == "__main__":
    main() 