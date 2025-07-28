#!/usr/bin/env python3
"""
Quick test script to verify the GIF BPM sync tool works
"""
import os
import sys

def test_gif_loading():
    """Test if we can load and process a GIF"""
    try:
        from PIL import Image, ImageSequence
        
        # Look for a test GIF in the BPM gif project folder
        test_gif_path = "BPM gif project/frog_2B.gif"
        
        if os.path.exists(test_gif_path):
            print(f"✓ Found test GIF: {test_gif_path}")
            
            # Test loading the GIF
            pil_img = Image.open(test_gif_path)
            frames = list(ImageSequence.Iterator(pil_img))
            print(f"✓ Successfully loaded GIF with {len(frames)} frames")
            
            # Test extracting beats from filename
            filename = os.path.basename(test_gif_path)
            import re
            match = re.search(r'_(\d+)B\.gif$', filename, re.IGNORECASE)
            if match:
                beats = float(match.group(1))
                print(f"✓ Extracted {beats} beats from filename")
            else:
                print("⚠ Could not extract beats from filename")
                
            return True
        else:
            print(f"✗ Test GIF not found: {test_gif_path}")
            return False
            
    except ImportError as e:
        print(f"✗ Missing dependency: {e}")
        return False
    except Exception as e:
        print(f"✗ Error testing GIF loading: {e}")
        return False

def test_dependencies():
    """Test if all required dependencies are available"""
    dependencies = ['pygame', 'pygame_gui', 'PIL']
    missing = []
    
    for dep in dependencies:
        try:
            if dep == 'PIL':
                import PIL
            else:
                __import__(dep)
            print(f"✓ {dep} is available")
        except ImportError:
            print(f"✗ {dep} is missing")
            missing.append(dep)
    
    return len(missing) == 0

def main():
    print("Testing GIF BPM Sync Tool Prototype")
    print("=" * 40)
    
    # Test dependencies
    print("\n1. Checking dependencies...")
    deps_ok = test_dependencies()
    
    # Test GIF loading
    print("\n2. Testing GIF loading...")
    gif_ok = test_gif_loading()
    
    print("\n" + "=" * 40)
    if deps_ok and gif_ok:
        print("✓ All tests passed! Your prototype should work.")
        print("\nTo run the tool:")
        print("  python3 gif_bpm_sync_tool_v2.py")
        print("  or")
        print("  ./run_gif_bpm_tool.sh")
    else:
        print("✗ Some tests failed. Please install missing dependencies:")
        print("  pip3 install pygame pygame_gui pillow")

if __name__ == "__main__":
    main() 