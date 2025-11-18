# How to Run P2P Video Streaming with Kivy

## 🎯 Quick Start (3 Steps)

### Step 1: Install Kivy
```bash
pip install kivy
```

### Step 2: Start Tracker (Terminal 1)
```bash
cd P2PVideoStr
python start_tracker.py
```
Leave this running! You should see:
```
[TRACKER] Started on localhost:6000
```

### Step 3: Start the App (Terminal 2)
```bash
cd P2PVideoStr
python main.py
```

🎉 **A Kivy window opens!**

## 📱 What You'll See

### Initial Screen: Peer Configuration

```
┌────────────────────────────────────┐
│   📹 P2P Video Streaming          │
├────────────────────────────────────┤
│   🔴 Peer not started             │
├────────────────────────────────────┤
│   Peer Configuration               │
│                                    │
│   [Peer ID: _____________]        │
│   [Port: 5000____________]        │
│   [Tracker Host: localhost]       │
│   [Tracker Port: 6000____]        │
│                                    │
│   [▶️ Start Peer]                 │
└────────────────────────────────────┘
```

### How to Use:

1. **Enter Peer ID:** Type a unique ID (e.g., `my_peer`)
2. **Port:** Leave as `5000` or change if needed
3. **Click "▶️ Start Peer"**
4. Status changes to: **🟢 Peer running**

### Main Navigation

Once peer starts, you'll see three tabs:

```
┌────────────────────────────────────┐
│ [📹 My Videos] [☁️ Network] [👥 Peers] │
└────────────────────────────────────┘
```

## 📹 My Videos Tab

Shows your uploaded videos:
- Video names
- File sizes
- Video IDs

**Features:**
- **⬆️ Upload Video** button (top right)
- Scrollable video list

## ☁️ Network Browse Tab

Shows videos from other peers:
- Video information
- Source peer (host:port)
- **⬇️ Download** button for each video

**Features:**
- **🔄 Refresh** button to update list
- Download videos with one click

## 👥 Peers Tab

Shows connected peers:
- Peer IDs
- Host and port information

**Features:**
- **Connect to Peer** section
  - Enter host and port
  - **➕ Connect** button
- View all known peers

## 🧪 Testing with Multiple Peers

### Peer 1 (Terminal 2):
```bash
cd P2PVideoStr
python main.py
```
- Peer ID: `peer1`
- Port: `5000`
- Click "▶️ Start Peer"

### Peer 2 (Terminal 3):
```bash
cd P2PVideoStr
python main.py
```
- Peer ID: `peer2`
- Port: `5001` ← Different port!
- Click "▶️ Start Peer"

### Test P2P Transfer:

1. **On Peer 1:**
   - Go to "📹 My Videos"
   - Click "⬆️ Upload Video"
   - (For testing, upload any video file)

2. **On Peer 2:**
   - Go to "☁️ Network"
   - Click "🔄 Refresh"
   - You should see Peer 1's video!
   - Click "⬇️ Download"

3. **Verify:**
   - On Peer 2, go to "📹 My Videos"
   - Downloaded video should appear!

## 🎮 Navigation Tips

- **Back buttons** on each tab return to main screen
- **Tab buttons** at top switch between views
- All operations happen in real-time
- Status updates automatically

## ⚙️ Configuration Options

### Default Settings:
- Tracker Host: `localhost`
- Tracker Port: `6000`
- Peer Port: `5000` (use 5001, 5002, etc. for additional peers)

### Custom Configuration:
You can change any values before clicking "▶️ Start Peer"

## 🖥️ Window Controls

### Keyboard Shortcuts:
- **Escape** - Back/Exit
- **F11** - Fullscreen (on some platforms)

### Mouse:
- All buttons are clickable
- Text fields accept keyboard input
- Scroll in list views

## 📊 Status Indicators

| Symbol | Meaning |
|--------|---------|
| 🔴 | Peer not started |
| 🟢 | Peer running |
| 📹 | Your videos |
| ☁️ | Network videos |
| 👥 | Connected peers |
| ⬆️ | Upload |
| ⬇️ | Download |
| 🔄 | Refresh |
| ➕ | Add/Connect |
| 💻 | Peer/Computer |

## 🎯 Common Tasks

### Upload a Video:
1. Make sure peer is started (🟢)
2. Go to "📹 My Videos" tab
3. Click "⬆️ Upload Video"
4. Select video file

### Download from Network:
1. Go to "☁️ Network" tab
2. Click "🔄 Refresh"
3. Find desired video
4. Click "⬇️ Download"

### Connect to Specific Peer:
1. Go to "👥 Peers" tab
2. Enter peer's host and port
3. Click "➕ Connect"

### View Connected Peers:
1. Go to "👥 Peers" tab
2. Scroll through peer list

## ⚠️ Troubleshooting

### Window doesn't open:
```bash
# Check Kivy is installed
python -c "import kivy; print(kivy.__version__)"

# Run with verbose output
python -u main.py
```

### "Failed to register with tracker":
- Make sure tracker is running: `python start_tracker.py`
- Check tracker host and port are correct

### "Port already in use":
- Use a different port number (5001, 5002, etc.)
- Each peer needs a unique port

### Can't see other peer's videos:
- Click "🔄 Refresh" in Network tab
- Make sure both peers are started
- Check both peers connected to same tracker

### Download fails:
- Make sure source peer is still running
- Check network connection
- Verify video still exists on source peer

## 📱 Mobile Support

Kivy apps work on mobile! To deploy:

1. **For Android:**
```bash
pip install buildozer
buildozer init
buildozer android debug deploy run
```

2. **For iOS (macOS only):**
```bash
pip install kivy-ios
toolchain build python3 kivy
toolchain create YourApp /path/to/your/app
```

See Kivy docs for full mobile deployment.

## 🎨 UI Features

### Responsive Design:
- Window resizes properly
- Scrollable lists
- Touch-friendly buttons

### Visual Feedback:
- Status colors (red/green)
- Button highlights on click
- Clear navigation

### Emoji Support:
- Universal across platforms
- No icon font needed
- Works everywhere!

## 🔄 Running Multiple Instances

You can run as many peers as you want:

```bash
# Terminal 1: Tracker
python start_tracker.py

# Terminal 2: Peer 1
python main.py  # Port 5000

# Terminal 3: Peer 2
python main.py  # Port 5001

# Terminal 4: Peer 3
python main.py  # Port 5002

# etc...
```

Each peer can:
- Upload videos
- Download from others
- Share with the network

## 📚 File Structure

```
P2PVideoStr/
├── Server/          # All networking code (unchanged)
│   ├── peer.py
│   ├── tracker.py
│   └── network_utils.py
├── KivyUI/          # Kivy interface (NEW!)
│   ├── app.py
│   └── p2pvideostream.kv
├── main.py          # Run this!
├── start_tracker.py
└── requirements.txt
```

## 🎓 For Your Demo

To show your professor:

1. **Start tracker** (show terminal output)
2. **Launch 2-3 peers** (different windows)
3. **Upload video** from Peer 1
4. **Show Peer 2** finding it in Network tab
5. **Download** on Peer 2
6. **Explain:** Direct P2P, no centralized storage!

## ✨ Kivy Advantages

✅ **Stable** - Mature, well-tested framework
✅ **Mobile** - Deploy to iOS/Android
✅ **Fast** - Native performance
✅ **Beautiful** - Modern UI design
✅ **Reliable** - No version conflicts
✅ **Popular** - Large community support

## 🆘 Need Help?

- **Installation issues:** See `KIVY_INSTALL.md`
- **Networking issues:** See `TROUBLESHOOTING.md`
- **General questions:** See `README.md`

## 🚀 You're Ready!

Your P2P Video Streaming app with Kivy UI is ready to go!

Just run:
```bash
python main.py
```

And enjoy your stable, cross-platform P2P video streaming application! 🎉
