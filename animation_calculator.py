#!/usr/bin/env python3
"""
Animation Timing Calculator for GIF BPM Sync
Helps determine the right frame counts and durations for beat-synchronized animations
"""

def calculate_animation_timing(bpm=None, beat_count=None, frames_per_beat=None, total_frames=None):
    """
    Calculate animation timing parameters. Provide any 3 values to get the 4th.
    
    Args:
        bpm: Beats per minute (target playback speed)
        beat_count: Number of beats in the full animation loop
        frames_per_beat: Number of animation frames per beat
        total_frames: Total number of frames in the animation
    
    Returns:
        Dictionary with all calculated values
    """
    
    # Count how many parameters we have
    params = [bpm, beat_count, frames_per_beat, total_frames]
    provided = sum(1 for p in params if p is not None)
    
    if provided < 3:
        return {"error": "Please provide at least 3 of the 4 parameters"}
    
    # Calculate the missing parameter
    if total_frames is None:
        total_frames = beat_count * frames_per_beat
    elif frames_per_beat is None:
        frames_per_beat = total_frames / beat_count
    elif beat_count is None:
        beat_count = total_frames / frames_per_beat
    elif bpm is None:
        # BPM isn't directly calculable from frame counts alone
        return {"error": "Cannot calculate BPM from frame counts alone - need duration info"}
    
    # Calculate timing information
    loop_duration_seconds = (beat_count / bpm) * 60
    loop_duration_ms = loop_duration_seconds * 1000
    frame_duration_ms = loop_duration_ms / total_frames
    
    return {
        "bpm": round(bpm, 1),
        "beat_count": round(beat_count, 1),
        "frames_per_beat": round(frames_per_beat, 2),
        "total_frames": int(total_frames),
        "loop_duration_seconds": round(loop_duration_seconds, 2),
        "loop_duration_ms": round(loop_duration_ms, 1),
        "frame_duration_ms": round(frame_duration_ms, 1)
    }

def print_timing_table():
    """Print a reference table of common animation timing scenarios"""
    
    print("=" * 80)
    print("ANIMATION TIMING REFERENCE TABLE")
    print("=" * 80)
    print(f"{'BPM':<6} {'Beat Count':<12} {'Frames/Beat':<12} {'Total Frames':<12} {'Frame Duration (ms)':<18}")
    print("-" * 80)
    
    # Common scenarios
    scenarios = [
        (120, 2, 2, None),  # Simple 2-beat dance, 2 frames per beat
        (120, 2, 4, None),  # Smoother 2-beat dance
        (120, 4, 2, None),  # Simple 4-beat dance
        (120, 4, 4, None),  # Smoother 4-beat dance
        (120, 4, 8, None),  # Very smooth 4-beat dance
        (140, 2, 2, None),  # Faster tempo examples
        (140, 4, 2, None),
        (100, 4, 3, None),  # Slower tempo with 3 frames per beat
        (80, 4, 4, None),   # Slow tempo, smooth animation
    ]
    
    for scenario in scenarios:
        result = calculate_animation_timing(*scenario)
        if "error" not in result:
            print(f"{result['bpm']:<6} {result['beat_count']:<12} {result['frames_per_beat']:<12} "
                  f"{result['total_frames']:<12} {result['frame_duration_ms']:<18}")

def interactive_calculator():
    """Interactive calculator for custom scenarios"""
    
    print("\n" + "=" * 50)
    print("INTERACTIVE ANIMATION CALCULATOR")
    print("=" * 50)
    print("Provide any 3 values to calculate the 4th:")
    print("(Press Enter to skip a value)")
    print()
    
    try:
        bpm_input = input("BPM (target playback speed): ").strip()
        bpm = float(bpm_input) if bpm_input else None
        
        beat_input = input("Beat Count (beats in full loop): ").strip()
        beat_count = float(beat_input) if beat_input else None
        
        fpb_input = input("Frames Per Beat: ").strip()
        frames_per_beat = float(fpb_input) if fpb_input else None
        
        total_input = input("Total Frames: ").strip()
        total_frames = int(total_input) if total_input else None
        
        result = calculate_animation_timing(bpm, beat_count, frames_per_beat, total_frames)
        
        if "error" in result:
            print(f"\nError: {result['error']}")
        else:
            print("\n" + "=" * 40)
            print("CALCULATED RESULTS:")
            print("=" * 40)
            print(f"BPM: {result['bpm']}")
            print(f"Beat Count: {result['beat_count']}")
            print(f"Frames Per Beat: {result['frames_per_beat']}")
            print(f"Total Frames: {result['total_frames']}")
            print(f"Loop Duration: {result['loop_duration_seconds']} seconds")
            print(f"Frame Duration: {result['frame_duration_ms']} ms per frame")
            print()
            print("EXPORT INSTRUCTIONS:")
            print(f"• Create {result['total_frames']} unique frames")
            print(f"• Set each frame duration to {result['frame_duration_ms']} ms")
            print(f"• Name your file with _{int(result['beat_count'])}B.gif suffix")
            print(f"• Expected BPM in sync tool: {result['bpm']}")
            
    except ValueError:
        print("Error: Please enter valid numbers")
    except KeyboardInterrupt:
        print("\nExiting...")

if __name__ == "__main__":
    print_timing_table()
    
    while True:
        print("\nOptions:")
        print("1. Interactive Calculator")
        print("2. Show Reference Table Again") 
        print("3. Exit")
        
        choice = input("\nChoose an option (1-3): ").strip()
        
        if choice == "1":
            interactive_calculator()
        elif choice == "2":
            print_timing_table()
        elif choice == "3":
            break
        else:
            print("Invalid choice, please try again.") 