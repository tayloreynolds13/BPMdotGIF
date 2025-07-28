# 🎵 GIF BPM Sync Tool

A powerful tool for synchronizing GIF animations to music BPM (Beats Per Minute). Perfect for DJs, content creators, and music producers who want to create perfectly timed visual content.

## ✨ Features

- **🎛️ Real-time BPM Control** - Adjust BPM from 30-600 with slider, buttons, or tap detection
- **📁 GIF Upload & Processing** - Upload GIFs and extract beat information from filenames
- **🎯 10 Animation Slots** - Manage multiple GIFs with hotkeys (1-10)
- **⚡ Speed Calculation** - Real-time sync calculations and speed multipliers
- **📱 Multiple Interfaces** - Desktop app, web interface, and Streamlit wrapper
- **🎮 Hotkey Support** - Full keyboard shortcuts for quick control
- **🔄 Export Ready** - Get sync calculations for external processing

## 🚀 Quick Start

### Desktop App (Recommended)
```bash
# Run the full desktop application
python3 gif_bpm_sync_tool_v2.py
```

### Web Interface
```bash
# Start the web version
cd gif-bpm-sync-web
python3 -m http.server 8000
# Visit http://localhost:8000
```

### Streamlit Web App
```bash
# Run Streamlit wrapper
streamlit run streamlit_wrapper.py
```

## 📦 Installation

### Prerequisites
- Python 3.8+
- pip

### Install Dependencies
```bash
pip install pygame pygame-gui pillow streamlit flask
```

## 🎮 Usage

### Desktop App Controls
- **1-9:** Switch to slot 1-9
- **0:** Switch to slot 10
- **Space:** Pause/Play
- **←/→:** Halve/Double BPM
- **↑/↓:** Adjust BPM ±1
- **Shift+↑/↓:** Adjust BPM ±10
- **Click:** Tap to set BPM

### Web Interface
- **Upload GIF:** Drag & drop or click to select
- **BPM Slider:** Adjust BPM from 30-600
- **Tap Button:** Click to set BPM by tapping
- **Beats Input:** Set number of beats in GIF
- **Export:** Get sync calculations

## 🌐 Deployment

### Railway (Recommended)
```bash
# Deploy to Railway
git push origin main
# Visit railway.app and connect your repo
```

### Streamlit Cloud
```bash
# Deploy to Streamlit Cloud
# Push to GitHub and connect at share.streamlit.io
```

## 📁 Project Structure

```
gif_bpm_sync_tool_v2_with_launchers/
├── gif_bpm_sync_tool_v2.py          # Main desktop app
├── railway_app.py                    # Railway web app
├── streamlit_wrapper.py              # Streamlit web interface
├── gif-bpm-sync-web/                # Pure web version
├── templates/                        # Web templates
├── requirements.txt                  # Python dependencies
├── railway_requirements.txt          # Railway dependencies
├── run_gif_bpm_tool.sh             # Linux/Mac launcher
├── run_gif_bpm_tool.bat            # Windows launcher
└── README.md                        # This file
```

## 🎯 Use Cases

- **DJs** - Sync visual effects to music
- **Content Creators** - Create timed animations
- **Music Producers** - Visualize beats and rhythms
- **Streamers** - Add animated overlays
- **Video Editors** - Precise timing for animations

## 🔧 Technical Details

### Core Features
- **Pygame GUI** - Desktop interface with pygame_gui
- **PIL/Pillow** - GIF processing and frame extraction
- **Flask** - Web API and interface
- **Streamlit** - Data science web interface
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
- **Streamlit** - Web app framework
- **Flask** - Web framework
- **Railway** - Deployment platform

## 📞 Support

- **Issues:** [GitHub Issues](https://github.com/yourusername/gif-bpm-sync-tool/issues)
- **Discussions:** [GitHub Discussions](https://github.com/yourusername/gif-bpm-sync-tool/discussions)
- **Email:** your-email@example.com

---

**Made with ❤️ for the music and content creation community** 