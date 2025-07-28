# 🎵 GIF BPM Sync Tool

A powerful desktop tool for synchronizing GIF animations to music BPM (Beats Per Minute). Perfect for DJs, content creators, and music producers who want to create perfectly timed visual content.

## ✨ Features

- **🎛️ Real-time BPM Control** - Adjust BPM from 30-600 with slider, buttons, or tap detection
- **📁 GIF Upload & Processing** - Upload GIFs and extract beat information from filenames
- **🎯 10 Animation Slots** - Manage multiple GIFs with hotkeys (1-10)
- **⚡ Speed Calculation** - Real-time sync calculations and speed multipliers
- **🎮 Hotkey Support** - Full keyboard shortcuts for quick control
- **🔄 Export Ready** - Get sync calculations for external processing
- **🎬 Stage Window** - Clean window for streaming to OBS

## 🚀 Quick Start

### Download & Run
1. **Download** `gif_bpm_sync_tool_v2.py` from this repository
2. **Install Python** (3.8 or higher)
3. **Install dependencies**: `pip install pygame pygame-gui pillow`
4. **Run**: `python3 gif_bpm_sync_tool_v2.py`

## 📦 Installation

### Prerequisites
- Python 3.8+
- pip

### Install Dependencies
```bash
pip install pygame pygame-gui pillow
```

## 🎮 Usage

### Desktop App Controls

#### 🎹 Hotkeys
- **1-9:** Switch to slot 1-9
- **0:** Switch to slot 10
- **Space:** Pause/Play
- **←/→:** Halve/Double BPM
- **↑/↓:** Adjust BPM ±1
- **Shift+↑/↓:** Adjust BPM ±10
- **Click:** Tap to set BPM
- **ESC:** Switch between main window and stage window

#### 🎛️ UI Controls

**Row 1 - BPM & Beats:**
- **BPM Input:** Type exact BPM value
- **BPM Slider:** Drag to adjust BPM (30-600)
- **/2 & x2 Buttons:** Quick BPM halving/doubling
- **Beats Input:** Set number of beats in current GIF

**Row 2 - File & Mode:**
- **Upload:** Select GIF file to load
- **Export:** Save sync calculations
- **Squad:** Toggle backup dancer mode
- **Flip:** Horizontal flip GIF
- **Stage:** Open clean stage window for streaming

**Row 3 - Sliders:**
- **Zoom:** Scale GIF size (0.1x to 3x)
- **Spacing:** Squad dancer spacing (0-1)
- **Size:** Squad dancer size (0-100%)

**Row 4 - Background:**
- **BG Color:** Cycle through preset background colors
- **BG Image:** Select custom background image
- **Clear BG:** Remove background image

**Bottom Strip:**
- **Slots 1-10:** Click to switch between GIF slots





## 📁 Project Structure

```
BPMdotGIF/
├── gif_bpm_sync_tool_v2.py          # Main desktop app
├── requirements.txt                  # Python dependencies
└── README.md                        # This file
```

## 🎯 Use Cases

- **DJs** - Sync visual effects to music
- **Content Creators** - Create timed animations
- **Music Producers** - Visualize beats and rhythms
- **Streamers** - Add animated overlays (use Stage window for OBS)
- **Video Editors** - Precise timing for animations

## 🎬 Stage Window for Streaming

The **Stage Window** feature creates a clean, separate window perfect for streaming:

1. **Click "Stage"** - Opens a clean window with just the GIF
2. **Press ESC** - Switch between main controls and stage window
3. **In OBS** - Use "Window Capture" and select "BPMdotGIF - Stage Window"
4. **No controls visible** - Perfect for clean streams

**Perfect for:**
- 🎥 **OBS Streaming** - Clean overlay without controls
- 📱 **Social Media** - Record just the animation
- 🎮 **Gaming Streams** - Animated overlays
- 🎵 **Music Videos** - Sync visuals to beats

## 🔧 Technical Details

### Core Features
- **Pygame GUI** - Desktop interface with pygame_gui
- **PIL/Pillow** - GIF processing and frame extraction
- **Real-time Calculation** - Instant BPM sync math

### File Naming Convention
GIFs with `_XB.gif` pattern automatically extract beat count:
- `dance_4B.gif` = 4 beats
- `animation_2.5B.gif` = 2.5 beats

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

### What MIT License Means:
- ✅ **Free to use** - Anyone can use your code
- ✅ **Free to modify** - Can be changed and improved
- ✅ **Free to distribute** - Can be shared and sold
- ✅ **Attribution required** - Must credit you
- ✅ **No warranty** - You're not liable for issues

## 🙏 Acknowledgments

- **Pygame** - Game development framework
- **Pillow** - Image processing library

## 📞 Support

- **Issues:** [GitHub Issues](https://github.com/tayloreynolds13/BPMdotGIF/issues)
- **Discussions:** [GitHub Discussions](https://github.com/tayloreynolds13/BPMdotGIF/discussions)

---

**Made with ❤️ for the music and content creation community** 