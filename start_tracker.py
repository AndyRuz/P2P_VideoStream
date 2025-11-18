"""
Standalone Tracker Server Starter
Run this script to start the tracker server independently
"""

from Server.tracker import start_tracker_server

if __name__ == "__main__":
    print("=" * 60)
    print("P2P Video Streaming - Tracker Server")
    print("=" * 60)
    print("\nStarting tracker server...")
    print("Press Ctrl+C to stop the server\n")
    
    try:
        start_tracker_server(host='localhost', port=6000)
    except KeyboardInterrupt:
        print("\n\nTracker server stopped.")
    except Exception as e:
        print(f"\nError: {e}")
