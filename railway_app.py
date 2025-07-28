#!/usr/bin/env python3
"""
Railway-compatible version of the GIF BPM Sync Tool
This version provides a web interface while maintaining the core functionality
"""

import os
import sys
from PIL import Image, ImageSequence
import time
import io
import base64
import tempfile
import threading
from flask import Flask, render_template, request, jsonify, send_file
import json

# Initialize Flask app
app = Flask(__name__)

# Global state (similar to your original app)
class AppState:
    def __init__(self):
        self.bpm = 120
        self.beats = 2
        self.zoom = 1.0
        self.paused = False
        self.squad_mode = False
        self.squad_spacing = 0.5
        self.squad_size = 80
        self.horizontal_flip = False
        self.tap_times = []
        self.last_tap_time = 0
        self.slots = [{'is_loaded': False, 'beats': 2, 'frames': [], 'durations': [], 'current_frame': 0, 'original_duration': 0} for _ in range(10)]
        self.active_slot = 0

state = AppState()

def extract_beats_from_filename(filename):
    """Extract beats from filename pattern _XB.gif"""
    import re
    match = re.search(r'_(\d+(?:\.\d+)?)B\.gif$', filename, re.IGNORECASE)
    return float(match.group(1)) if match else 2.0

def calculate_speed_multiplier(bpm, beats, original_duration):
    """Calculate speed multiplier based on BPM"""
    if bpm <= 0:
        return 1.0
    target_duration = (beats / bpm) * 60000
    return original_duration / target_duration

@app.route('/')
def index():
    """Main web interface"""
    return render_template('index.html')

@app.route('/health')
def health_check():
    """Health check endpoint for Railway"""
    return jsonify({'status': 'healthy', 'message': 'BPMdotGIF is running'})

@app.route('/api/state')
def get_state():
    """Get current app state"""
    return jsonify({
        'bpm': state.bpm,
        'beats': state.beats,
        'active_slot': state.active_slot,
        'paused': state.paused,
        'squad_mode': state.squad_mode,
        'horizontal_flip': state.horizontal_flip,
        'slots': [{
            'is_loaded': slot['is_loaded'],
            'beats': slot['beats'],
            'frame_count': len(slot['frames']),
            'current_frame': slot['current_frame']
        } for slot in state.slots]
    })

@app.route('/api/bpm', methods=['POST'])
def set_bpm():
    """Set BPM"""
    data = request.json
    state.bpm = max(30, min(600, int(data.get('bpm', 120))))
    return jsonify({'success': True, 'bpm': state.bpm})

@app.route('/api/beats', methods=['POST'])
def set_beats():
    """Set beats for active slot"""
    data = request.json
    beats = float(data.get('beats', 2))
    state.beats = beats
    if state.slots[state.active_slot]['is_loaded']:
        state.slots[state.active_slot]['beats'] = beats
    return jsonify({'success': True, 'beats': beats})

@app.route('/api/slot', methods=['POST'])
def set_active_slot():
    """Set active slot"""
    data = request.json
    slot = int(data.get('slot', 0))
    state.active_slot = max(0, min(9, slot))
    return jsonify({'success': True, 'active_slot': state.active_slot})

@app.route('/api/pause', methods=['POST'])
def toggle_pause():
    """Toggle pause state"""
    state.paused = not state.paused
    return jsonify({'success': True, 'paused': state.paused})

@app.route('/api/upload', methods=['POST'])
def upload_gif():
    """Upload and process GIF"""
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    try:
        # Read file
        gif_bytes = file.read()
        
        # Extract beats from filename
        beats = extract_beats_from_filename(file.filename)
        
        # Process GIF with PIL
        pil_img = Image.open(io.BytesIO(gif_bytes))
        frames = []
        durations = []
        
        for frame in ImageSequence.Iterator(pil_img):
            durations.append(frame.info.get("duration", 100))
            # Convert frame to base64 for web display
            buffer = io.BytesIO()
            frame.save(buffer, format='PNG')
            frame_b64 = base64.b64encode(buffer.getvalue()).decode()
            frames.append(f"data:image/png;base64,{frame_b64}")
        
        # Update slot
        slot = state.slots[state.active_slot]
        slot['frames'] = frames
        slot['durations'] = durations
        slot['beats'] = beats
        slot['original_duration'] = sum(durations)
        slot['current_frame'] = 0
        slot['is_loaded'] = True
        
        # Update global beats
        state.beats = beats
        
        return jsonify({
            'success': True,
            'frame_count': len(frames),
            'original_duration': sum(durations),
            'beats': beats,
            'filename': file.filename
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/export', methods=['POST'])
def export_gif():
    """Export synchronized GIF"""
    slot = state.slots[state.active_slot]
    if not slot['is_loaded']:
        return jsonify({'error': 'No GIF loaded'}), 400
    
    try:
        # Calculate speed multiplier
        speed_mult = calculate_speed_multiplier(
            state.bpm, 
            slot['beats'], 
            slot['original_duration']
        )
        
        # Create export info
        export_info = {
            'bpm': state.bpm,
            'beats': slot['beats'],
            'speed_multiplier': speed_mult,
            'target_duration': (slot['beats'] / state.bpm) * 60000,
            'filename': f"synced_{state.bpm}bpm_{slot['beats']}beats.gif"
        }
        
        return jsonify({
            'success': True,
            'export_info': export_info
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/tap', methods=['POST'])
def handle_tap():
    """Handle tap for BPM detection"""
    now = time.time()
    
    # Remove old taps (older than 4 seconds)
    state.tap_times = [t for t in state.tap_times if now - t < 4]
    
    if state.tap_times:
        time_since_last = now - state.tap_times[-1]
        if time_since_last > 0.1:  # Minimum 100ms between taps
            state.tap_times.append(now)
    else:
        state.tap_times.append(now)
    
    # Keep only last 8 taps
    if len(state.tap_times) > 8:
        state.tap_times.pop(0)
    
    # Calculate BPM
    if len(state.tap_times) >= 2:
        intervals = [state.tap_times[i] - state.tap_times[i-1] for i in range(1, len(state.tap_times))]
        avg_interval = sum(intervals) / len(intervals)
        new_bpm = max(30, min(600, int(60 / avg_interval)))
        state.bpm = new_bpm
    
    return jsonify({
        'success': True,
        'bpm': state.bpm,
        'tap_count': len(state.tap_times)
    })

if __name__ == '__main__':
    # Start Flask app
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=False) 