# 🎬 P2P Video Streaming Application

A peer-to-peer video streaming application built with Python and Kivy that allows users to share and stream videos directly with friends without relying on centralized servers.

## 📋 Project Overview

This application addresses the challenge of sharing videos with friends and family without uploading to social media platforms or signing up for file sharing services. Using a peer-to-peer (P2P) architecture, it improves scalability, fault tolerance, and efficiency by distributing data across multiple peers.

### Team Project

This is a Computer Networking and Distributed Systems course project that demonstrates:
- Network communication between multiple nodes
- Distributed computing concepts (concurrency, fault tolerance)
- TCP for reliable data delivery
- Peer-to-peer architecture with tracker-based peer discovery

## ✨ Features

### Core Functionality
- **Peer-to-Peer Video Sharing**: Share videos directly between users without centralized storage
- **User Profiles**: Create and manage persistent user accounts with personalized settings
- **Video Library Management**: 
  - Upload videos to your personal library
  - Organize videos into "Uploaded" and "Network Obtained" sections
  - Edit video information (name and description)
  - Delete videos from your library
- **Network Discovery**: Browse and discover videos available on the network
- **Video Playback**: Play videos using your system's default media player
- **Download to Device**: Save network videos to your local device storage

### Social Features
- **Friends List**: Save frequently connected users for easy access
- **Connected Users**: View all active peers on the network
- **Manual Connection**: Connect directly to specific peers
- **Connection Status**: Visual indicator showing active manual connections

### Customization
- **Theme Toggle**: Switch between Light and Dark modes
- **Display Format**: Optimize for PC or Mobile viewing
- **User Profile Management**: Edit user details or delete user accounts

## 🔧 Requirements

### System Requirements
- **Operating System**: Windows, macOS, or Linux
- **Python**: Version 3.8 or higher
- **RAM**: Minimum 2GB
- **Storage**: 500MB free space (more for video storage)

### Python Dependencies
- `kivy>=2.0.0` - GUI framework
- `plyer` - Cross-platform file chooser support

## 📦 Installation

### Step 1: Install Python

If you don't have Python installed:

**Windows:**
1. Download Python from [python.org](https://www.python.org/downloads/)
2. Run the installer
3. ✅ **Important**: Check "Add Python to PATH" during installation

**macOS:**
```bash
brew install python3
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install python3 python3-pip
```

### Step 2: Clone or Download the Project

**Option A: Clone with Git**
```bash
git clone https://github.com/yourusername/P2PVideoStr.git
cd P2PVideoStr
```

**Option B: Download ZIP**
1. Download the project ZIP file
2. Extract to a folder
3. Open terminal/command prompt in that folder

### Step 3: Install Dependencies

Open terminal/command prompt in the project directory and run:

```bash
pip install -r requirements.txt
```

If you encounter permission errors, try:
```bash
pip install --user -r requirements.txt
```

## 🚀 Running the Application

### Starting the Application

#### Method 1: Run Both Components Together (Recommended for Single Machine Testing)

**Windows:**
1. Open Command Prompt
2. Navigate to project folder
3. Start the tracker:
```bash
python start_tracker.py
```
4. Open a **NEW** Command Prompt window
5. Navigate to project folder again
6. Start the application:
```bash
python main.py
```

**macOS/Linux:**
```bash
# Terminal 1 - Start Tracker
python3 start_tracker.py

# Terminal 2 - Start Application
python3 main.py
```

#### Method 2: Distributed Setup (For Multiple Machines)

**Machine 1 (Tracker Server):**
```bash
python start_tracker.py
```
Note the IP address of this machine (e.g., 192.168.1.100)

**Machine 2+ (Peer Clients):**
```bash
python main.py
```
When creating/selecting a profile, use the Tracker Server's IP address instead of "localhost"

## 📖 Usage Guide

### First Time Setup

1. **Start the Application**
   - Run `python main.py`
   - You'll see the Peer Configuration screen

2. **Create Your User Profile**
   - Enter a unique **Peer ID** (e.g., "Alice", "Bob")
   - Enter a **Port** number (default: 5000)
   - Enter **Tracker Host** (default: localhost)
   - Enter **Tracker Port** (default: 6000)
   - Click **"▶️ Start with New Profile"**

3. **Select Existing Profile**
   - If you've used the app before, your profile will appear at the top
   - Click on your profile button to log in with saved settings

### Uploading Videos

1. Navigate to **"🎬 My Videos"** section
2. Click **"⬆️ Upload Video"**
3. Select a video file (.mp4, .avi, .mov, .mkv, .flv)
4. Enter video name and optional description
5. Click **"Upload"**
6. Your video appears in **"📤 My Uploaded Videos"**

### Sharing Videos on Network

1. In **"📤 My Uploaded Videos"**, click **"⋮ Options"** on a video
2. Click **"🌐 Upload to Network"**
3. Video status changes to "🌐 On Network"
4. Other users can now discover and download your video

### Discovering Network Videos

1. Navigate to **"☁️ Network"** section
2. Click **"🔄 Refresh"** to scan the network
3. Browse available videos from other peers
4. Click **"⬇️ Download"** on any video to add it to your library

### Managing Downloaded Videos

Downloaded videos appear in **"📥 Network Obtained Videos"**

**Available Options:**
- **▶️ Play Video**: Watch the video
- **💾 Download to Device**: Save to your computer's storage
- **🗑️ Remove from Library**: Delete from app (can re-download later)

### Connecting with Peers

1. Navigate to **"👥 Peers"** section
2. View **"🌐 Connected Users"** - all active peers
3. Click **"🔄 Refresh"** to update the list

**Adding Friends:**
1. Click **"⋮ Options"** next to a user
2. Select **"⭐ Add to Friends"**
3. User appears in **"⭐ Friends"** section for quick access

**Manual Connection:**
1. Click **"⋮ Options"** next to any user
2. Select **"🔗 Connect Manually"**
3. Connection status appears at bottom of screen
4. Click **"❌"** to disconnect

### User Profile Management

1. Click the **"👤"** icon (top right of any screen)
2. **"✏️ Edit User Details"**: Modify Peer ID, port, or tracker settings
3. **"🗑️ Delete User"**: Remove profile and all associated data

### Customization Settings

1. Click the **"⚙️"** icon (top left of any screen)
2. **Color Theme**: 
   - ☀️ Light Mode - White background, black text
   - 🌙 Dark Mode - Dark background, white text
3. **Display Format**:
   - 💻 PC - Optimized for desktop (900x700)
   - 📱 Mobile - Optimized for mobile devices (400x700)

## 📁 Project Structure

```
P2PVideoStr/
├── KivyUI/                      # Frontend UI components
│   ├── __init__.py             # Package initializer
│   └── app.py                  # Main Kivy application and UI logic
│
├── Server/                      # Backend networking components
│   ├── __init__.py             # Package initializer
│   ├── peer.py                 # Peer node implementation
│   ├── tracker.py              # Tracker server implementation
│   ├── network_utils.py        # Network utility functions
│   └── user_profile.py         # User profile management
│
├── main.py                      # Application entry point
├── start_tracker.py            # Tracker server starter script
├── p2pvideostream.kv           # Kivy UI layout definitions
├── requirements.txt            # Python dependencies
├── README.md                   # This file
│
├── peer_videos_[PeerID]/       # Generated: User's video storage
└── user_profiles/              # Generated: User profile data
    └── profiles.json
```

## 🎮 Keyboard Shortcuts

- **Ctrl+C** (in terminal): Stop the application
- **Escape**: Close popups/dialogs

## 🔍 Troubleshooting

### Common Issues

**Issue: "Failed to register with tracker"**
- **Solution**: Make sure the tracker server is running first
- Check that tracker host and port are correct
- Ensure no firewall is blocking the connection

**Issue: "Port already in use"**
- **Solution**: Choose a different port number
- Or close the other application using that port

**Issue: "No videos showing in Network section"**
- **Solution**: 
  1. Make sure other peers have uploaded videos to the network
  2. Click the Refresh button
  3. Check that all peers are using the same tracker

**Issue: "Cannot connect to other peer"**
- **Solution**:
  1. Verify both peers are registered with the tracker
  2. Check firewall settings
  3. For different machines, use actual IP addresses instead of "localhost"

**Issue: "Video won't play"**
- **Solution**: 
  1. Install a media player (VLC, Windows Media Player, QuickTime)
  2. Check video file isn't corrupted
  3. Try a different video format

**Issue: "Application crashes on startup"**
- **Solution**:
  1. Verify all dependencies are installed: `pip install -r requirements.txt`
  2. Check Python version: `python --version` (should be 3.8+)
  3. Delete `user_profiles/` folder and restart with fresh profile

### Port Configuration

**Default Ports:**
- Tracker Server: 6000
- Peers: 5000, 5001, 5002, etc.

**Testing Multiple Peers on Same Machine:**
- Each peer must use a different port
- Example: Alice (5000), Bob (5001), Charlie (5002)

## 🌐 Network Configuration

### Same Machine Testing
- Use `localhost` for tracker host
- Use different ports for each peer

### Multiple Machines (LAN)
1. **Find Tracker Machine IP:**
   - Windows: `ipconfig`
   - Mac/Linux: `ifconfig` or `ip addr`
2. **Configure Peers:**
   - Use tracker machine's IP (e.g., 192.168.1.100)
   - Keep default tracker port (6000)

### Firewall Settings
If connections fail, allow these in your firewall:
- Port 6000 (Tracker)
- Ports 5000-5010 (Peers)

## 🤝 Contributing

This is a course project. If you'd like to extend it:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📄 License

This project is created for educational purposes as part of a Computer Networking and Distributed Systems course.

## 👥 Team Members

[List your team members here]
- Member 1 - [Email]
- Member 2 - [Email]
- Member 3 - [Email]
- Member 4 - [Email]

## 🙏 Acknowledgments

- **Course**: Computer Networking and Distributed Systems
- **Professor**: [Professor Name]
- **Technologies**: Python, Kivy, TCP/IP
- **Inspiration**: BitTorrent, P2P file sharing protocols

## 📞 Support

For issues or questions:
1. Check the Troubleshooting section above
2. Review the console output for error messages
3. Contact team members via [communication method]

## 🔮 Future Enhancements

Potential features for future versions:
- Video streaming (instead of download-only)
- Video compression/optimization
- Bandwidth throttling
- Resume interrupted downloads
- Chat functionality between peers
- Advanced search and filtering
- Video thumbnails/previews
- Multi-tracker support
- NAT traversal for internet-wide P2P

---

**Version**: 1.0.0  
**Last Updated**: November 2025  
**Status**: Active Development
