import streamlit as st
import pygame
import pygame_gui
from PIL import Image, ImageSequence
import time
import os
import io
import base64
import tempfile
import subprocess
import sys

# Page config
st.set_page_config(
    page_title="GIF BPM Sync Tool",
    page_icon="🎵",
    layout="wide"
)

# Custom CSS for better UI
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
    .download-section {
        background: #2a2a2a;
        padding: 20px;
        border-radius: 10px;
        margin: 20px 0;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'bpm' not in st.session_state:
    st.session_state.bpm = 120
if 'beats' not in st.session_state:
    st.session_state.beats = 2
if 'gif_data' not in st.session_state:
    st.session_state.gif_data = None

def extract_beats_from_filename(filename):
    """Extract beats from filename pattern _XB.gif"""
    import re
    match = re.search(r'_(\d+(?:\.\d+)?)B\.gif$', filename, re.IGNORECASE)
    return float(match.group(1)) if match else 2.0

def calculate_speed_multiplier(bpm, beats, original_duration):
    """Calculate speed multiplier based on BPM"""
    if bpm <= 0:
        return 1.0
    target_duration = (beats / bpm) * 60000  # Convert to milliseconds
    return original_duration / target_duration

def export_synced_gif(gif_data, bpm, beats, speed_multiplier):
    """Export the GIF with BPM synchronization info"""
    if not gif_data:
        return None
    
    # Create a temporary file for the original GIF
    with tempfile.NamedTemporaryFile(suffix='.gif', delete=False) as temp_file:
        temp_file.write(gif_data['original_bytes'])
        temp_path = temp_file.name
    
    # Create output filename with BPM info
    output_filename = f"synced_{bpm}bpm_{beats}beats.gif"
    
    # Use your existing Python app's export logic
    # This would call your actual working export function
    return {
        'original_path': temp_path,
        'output_filename': output_filename,
        'speed_multiplier': speed_multiplier,
        'bpm': bpm,
        'beats': beats
    }

# Main app
st.markdown('<h1 class="main-header">🎵 GIF BPM Sync Tool</h1>', unsafe_allow_html=True)

# Sidebar controls
with st.sidebar:
    st.header("🎛️ Controls")
    
    # BPM controls
    st.subheader("BPM Settings")
    bpm = st.slider("BPM", 30, 600, st.session_state.bpm, key="bpm_slider")
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
        
        # Store the uploaded file data
        gif_bytes = uploaded_file.read()
        uploaded_file.seek(0)  # Reset file pointer
        
        # Load GIF info
        pil_img = Image.open(io.BytesIO(gif_bytes))
        durations = []
        for frame in ImageSequence.Iterator(pil_img):
            durations.append(frame.info.get("duration", 100))
        
        st.session_state.gif_data = {
            'filename': uploaded_file.name,
            'width': pil_img.width,
            'height': pil_img.height,
            'original_duration': sum(durations),
            'original_bytes': gif_bytes,
            'frame_count': len(list(ImageSequence.Iterator(pil_img)))
        }
        
        st.success(f"✅ Loaded {st.session_state.gif_data['frame_count']} frames")
        st.info(f"📊 {pil_img.width}×{pil_img.height} pixels")

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

# GIF display and export
if st.session_state.gif_data:
    # Show GIF info
    st.subheader("📊 GIF Information")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Frames", st.session_state.gif_data['frame_count'])
    with col2:
        st.metric("Duration", f"{st.session_state.gif_data['original_duration']}ms")
    with col3:
        st.metric("Size", f"{st.session_state.gif_data['width']}×{st.session_state.gif_data['height']}")
    
    # Export section
    st.markdown('<div class="download-section">', unsafe_allow_html=True)
    st.subheader("💾 Export Synced GIF")
    
    speed_mult = calculate_speed_multiplier(
        st.session_state.bpm, 
        st.session_state.beats, 
        st.session_state.gif_data['original_duration']
    )
    
    st.write(f"**Target BPM:** {st.session_state.bpm}")
    st.write(f"**Beats in GIF:** {st.session_state.beats}")
    st.write(f"**Speed Multiplier:** {speed_mult:.2f}x")
    st.write(f"**New Duration:** {(st.session_state.beats / st.session_state.bpm) * 60000:.0f}ms")
    
    # Export button
    if st.button("🚀 Export Synced GIF"):
        export_info = export_synced_gif(
            st.session_state.gif_data,
            st.session_state.bpm,
            st.session_state.beats,
            speed_mult
        )
        
        if export_info:
            st.success("✅ Export ready!")
            st.info(f"""
            **Export Details:**
            - Original: {st.session_state.gif_data['filename']}
            - Target BPM: {export_info['bpm']}
            - Speed: {export_info['speed_multiplier']:.2f}x
            - Output: {export_info['output_filename']}
            
            **Note:** This web version shows the sync calculations. 
            For actual GIF export, use the desktop version: `python3 gif_bpm_sync_tool_v2.py`
            """)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Debug info
    with st.expander("🔧 Debug Info"):
        st.write(f"**Original Duration:** {st.session_state.gif_data['original_duration']}ms")
        st.write(f"**Target Duration:** {(st.session_state.beats / st.session_state.bpm) * 60000:.0f}ms")
        st.write(f"**Speed Multiplier:** {speed_mult:.2f}x")
        st.write(f"**Frame Count:** {st.session_state.gif_data['frame_count']}")

else:
    st.markdown("""
    <div style="text-align: center; padding: 4rem; color: #666;">
        <h2>📁 Upload a GIF to get started!</h2>
        <p>Use the sidebar to upload a GIF file and adjust the BPM settings.</p>
        <p><strong>For full functionality including real-time animation:</strong></p>
        <p><code>python3 gif_bpm_sync_tool_v2.py</code></p>
    </div>
    """, unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666;">
    <p>🎵 GIF BPM Sync Tool - Web Interface</p>
    <p><strong>For full functionality with real-time animation:</strong></p>
    <p><code>python3 gif_bpm_sync_tool_v2.py</code></p>
</div>
""", unsafe_allow_html=True) 