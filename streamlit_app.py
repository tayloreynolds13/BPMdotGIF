import streamlit as st
import pygame
import pygame_gui
from PIL import Image, ImageSequence
import time
import os
import io
import base64
import tempfile

# Page config
st.set_page_config(
    page_title="GIF BPM Sync Tool",
    page_icon="🎵",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        text-align: center;
        color: #ff6b6b;
        margin-bottom: 2rem;
    }
    .bpm-display {
        font-size: 4rem;
        text-align: center;
        color: #4ecdc4;
        font-weight: bold;
    }
    .speed-indicator {
        background: rgba(0,0,0,0.8);
        color: white;
        padding: 10px;
        border-radius: 10px;
        text-align: center;
        font-size: 1.2rem;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'bpm' not in st.session_state:
    st.session_state.bpm = 120
if 'beats' not in st.session_state:
    st.session_state.beats = 2.0
if 'gif_data' not in st.session_state:
    st.session_state.gif_data = None
if 'gif_frames' not in st.session_state:
    st.session_state.gif_frames = []
if 'current_frame' not in st.session_state:
    st.session_state.current_frame = 0
if 'last_frame_time' not in st.session_state:
    st.session_state.last_frame_time = 0

def extract_beats_from_filename(filename):
    """Extract beats from filename pattern _XB.gif"""
    import re
    match = re.search(r'_(\d+(?:\.\d+)?)B\.gif$', filename, re.IGNORECASE)
    return float(match.group(1)) if match else 2.0

def load_gif(uploaded_file):
    """Load and parse uploaded GIF"""
    try:
        # Read the uploaded file
        gif_bytes = uploaded_file.read()
        
        # Open with PIL
        pil_img = Image.open(io.BytesIO(gif_bytes))
        frames = []
        durations = []
        
        # Extract frames
        for frame in ImageSequence.Iterator(pil_img):
            frame_rgba = frame.convert("RGBA")
            durations.append(frame.info.get("duration", 100))
            
            # Convert to base64 for display
            buffer = io.BytesIO()
            frame_rgba.save(buffer, format='PNG')
            frame_b64 = base64.b64encode(buffer.getvalue()).decode()
            frames.append(f"data:image/png;base64,{frame_b64}")
        
        return {
            'frames': frames,
            'durations': durations,
            'width': pil_img.width,
            'height': pil_img.height,
            'original_duration': sum(durations)
        }
    except Exception as e:
        st.error(f"Error loading GIF: {e}")
        return None

def calculate_speed_multiplier(bpm, beats, original_duration):
    """Calculate speed multiplier based on BPM"""
    if bpm <= 0:
        return 1.0
    target_duration = (beats / bpm) * 60000  # Convert to milliseconds
    return original_duration / target_duration

# Main app
st.markdown('<h1 class="main-header">🎵 GIF BPM Sync Tool</h1>', unsafe_allow_html=True)

# Sidebar controls
with st.sidebar:
    st.header("🎛️ Controls")
    
    # BPM controls
    st.subheader("BPM Settings")
    bpm = st.slider("BPM", 30, 600, int(st.session_state.bpm), key="bpm_slider")
    st.session_state.bpm = bpm
    
    # Speed controls
    col1, col2 = st.columns(2)
    with col1:
        if st.button("÷2"):
            st.session_state.bpm = max(30, st.session_state.bpm // 2)
    with col2:
        if st.button("×2"):
            st.session_state.bpm = min(600, st.session_state.bpm * 2)
    
    # Beats setting
    beats = st.number_input("Beats in GIF", 0.1, 10.0, float(st.session_state.beats), 0.1)
    st.session_state.beats = beats
    
    # File upload
    st.subheader("📁 GIF Upload")
    uploaded_file = st.file_uploader("Choose a GIF file", type=['gif'])
    
    if uploaded_file is not None:
        # Extract beats from filename
        filename_beats = extract_beats_from_filename(uploaded_file.name)
        st.session_state.beats = filename_beats
        
        # Load GIF
        gif_data = load_gif(uploaded_file)
        if gif_data:
            st.session_state.gif_data = gif_data
            st.success(f"✅ Loaded {len(gif_data['frames'])} frames")
            st.info(f"📊 {gif_data['width']}×{gif_data['height']} pixels")

# Main display area
col1, col2, col3 = st.columns([2, 1, 2])

with col2:
    # BPM display
    st.markdown(f'<div class="bpm-display">{st.session_state.bpm}</div>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; font-size: 1.2rem;">BPM</p>', unsafe_allow_html=True)
    
    # Speed indicator
    if st.session_state.gif_data:
        speed_mult = calculate_speed_multiplier(
            st.session_state.bpm, 
            st.session_state.beats, 
            st.session_state.gif_data['original_duration']
        )
        st.markdown(f'<div class="speed-indicator">{speed_mult:.1f}x speed</div>', unsafe_allow_html=True)

# GIF display
if st.session_state.gif_data and st.session_state.gif_data['frames']:
    # Get current frame
    current_time = time.time()
    frame_duration = st.session_state.gif_data['durations'][st.session_state.current_frame]
    
    # Calculate speed-adjusted duration
    speed_mult = calculate_speed_multiplier(
        st.session_state.bpm, 
        st.session_state.beats, 
        st.session_state.gif_data['original_duration']
    )
    adjusted_duration = frame_duration / speed_mult / 1000  # Convert to seconds
    
    # Update frame if enough time has passed
    if current_time - st.session_state.last_frame_time >= adjusted_duration:
        st.session_state.current_frame = (st.session_state.current_frame + 1) % len(st.session_state.gif_data['frames'])
        st.session_state.last_frame_time = current_time
    
    # Display current frame
    current_frame = st.session_state.gif_data['frames'][st.session_state.current_frame]
    st.image(current_frame, caption=f"Frame {st.session_state.current_frame + 1}/{len(st.session_state.gif_data['frames'])}")
    
    # Debug info
    with st.expander("🔧 Debug Info"):
        st.write(f"**Speed Multiplier:** {speed_mult:.2f}x")
        st.write(f"**Original Duration:** {st.session_state.gif_data['original_duration']}ms")
        st.write(f"**Target Duration:** {(st.session_state.beats / st.session_state.bpm) * 60000:.0f}ms")
        st.write(f"**Frame Duration:** {adjusted_duration:.2f}s")
        st.write(f"**Current Frame:** {st.session_state.current_frame + 1}/{len(st.session_state.gif_data['frames'])}")

else:
    st.markdown("""
    <div style="text-align: center; padding: 4rem; color: #666;">
        <h2>📁 Upload a GIF to get started!</h2>
        <p>Use the sidebar to upload a GIF file and adjust the BPM settings.</p>
    </div>
    """, unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666;">
    <p>🎵 GIF BPM Sync Tool - Streamlit Version</p>
    <p>Upload a GIF, set the BPM, and watch it sync to your music!</p>
</div>
""", unsafe_allow_html=True) 