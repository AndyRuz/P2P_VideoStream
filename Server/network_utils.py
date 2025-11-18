"""
Network Utilities for P2P Video Streaming Application
Helper functions for network communication and peer management
"""

import socket
import json
from typing import Optional, Tuple


def send_json_message(sock: socket.socket, data: dict) -> bool:
    """
    Send a JSON message through a socket
    
    Args:
        sock: Socket to send through
        data: Dictionary to send as JSON
        
    Returns:
        True if successful, False otherwise
    """
    try:
        message = json.dumps(data).encode('utf-8')
        sock.send(message)
        return True
    except Exception as e:
        print(f"Error sending JSON message: {e}")
        return False


def receive_json_message(sock: socket.socket, buffer_size: int = 4096) -> Optional[dict]:
    """
    Receive a JSON message from a socket
    
    Args:
        sock: Socket to receive from
        buffer_size: Size of receive buffer
        
    Returns:
        Parsed JSON dictionary or None if error
    """
    try:
        data = sock.recv(buffer_size).decode('utf-8')
        return json.loads(data)
    except Exception as e:
        print(f"Error receiving JSON message: {e}")
        return None


def connect_to_tracker(tracker_host: str, tracker_port: int, 
                       request: dict) -> Optional[dict]:
    """
    Connect to tracker and send a request
    
    Args:
        tracker_host: Tracker server host
        tracker_port: Tracker server port
        request: Request dictionary
        
    Returns:
        Response dictionary or None if error
    """
    try:
        # Create socket and connect
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((tracker_host, tracker_port))
        
        # Send request
        send_json_message(sock, request)
        
        # Receive response
        response = receive_json_message(sock)
        
        sock.close()
        return response
        
    except Exception as e:
        print(f"Error connecting to tracker: {e}")
        return None


def register_with_tracker(peer_id: str, peer_host: str, peer_port: int,
                         tracker_host: str = 'localhost',
                         tracker_port: int = 6000) -> bool:
    """
    Register a peer with the tracker server
    
    Args:
        peer_id: Unique peer identifier
        peer_host: Peer's host address
        peer_port: Peer's port
        tracker_host: Tracker server host
        tracker_port: Tracker server port
        
    Returns:
        True if registration successful
    """
    request = {
        'type': 'REGISTER',
        'peer_id': peer_id,
        'host': peer_host,
        'port': peer_port
    }
    
    response = connect_to_tracker(tracker_host, tracker_port, request)
    
    if response and response.get('status') == 'success':
        print(f"Successfully registered peer {peer_id} with tracker")
        return True
    else:
        print(f"Failed to register with tracker")
        return False


def get_peers_from_tracker(tracker_host: str = 'localhost',
                           tracker_port: int = 6000) -> list:
    """
    Get list of all peers from tracker
    
    Args:
        tracker_host: Tracker server host
        tracker_port: Tracker server port
        
    Returns:
        List of peer dictionaries
    """
    request = {'type': 'GET_PEERS'}
    response = connect_to_tracker(tracker_host, tracker_port, request)
    
    if response and response.get('status') == 'success':
        return response.get('peers', [])
    else:
        return []


def announce_video_to_tracker(peer_id: str, video_id: str,
                              tracker_host: str = 'localhost',
                              tracker_port: int = 6000) -> bool:
    """
    Announce that a peer has a video
    
    Args:
        peer_id: Peer identifier
        video_id: Video identifier
        tracker_host: Tracker server host
        tracker_port: Tracker server port
        
    Returns:
        True if announcement successful
    """
    request = {
        'type': 'ANNOUNCE_VIDEO',
        'peer_id': peer_id,
        'video_id': video_id
    }
    
    response = connect_to_tracker(tracker_host, tracker_port, request)
    return response and response.get('status') == 'success'


def find_video_peers(video_id: str, tracker_host: str = 'localhost',
                    tracker_port: int = 6000) -> list:
    """
    Find which peers have a specific video
    
    Args:
        video_id: Video identifier
        tracker_host: Tracker server host
        tracker_port: Tracker server port
        
    Returns:
        List of peers that have the video
    """
    request = {
        'type': 'FIND_VIDEO',
        'video_id': video_id
    }
    
    response = connect_to_tracker(tracker_host, tracker_port, request)
    
    if response and response.get('status') == 'success':
        return response.get('peers', [])
    else:
        return []


def send_heartbeat(peer_id: str, tracker_host: str = 'localhost',
                  tracker_port: int = 6000) -> bool:
    """
    Send heartbeat to tracker to stay active
    
    Args:
        peer_id: Peer identifier
        tracker_host: Tracker server host
        tracker_port: Tracker server port
        
    Returns:
        True if heartbeat successful
    """
    request = {
        'type': 'HEARTBEAT',
        'peer_id': peer_id
    }
    
    response = connect_to_tracker(tracker_host, tracker_port, request)
    return response and response.get('status') == 'success'


def format_file_size(size_bytes: int) -> str:
    """
    Format file size in human-readable format
    
    Args:
        size_bytes: Size in bytes
        
    Returns:
        Formatted string (e.g., "1.5 MB")
    """
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} PB"


def validate_port(port: int) -> bool:
    """
    Validate if a port number is valid
    
    Args:
        port: Port number to validate
        
    Returns:
        True if valid
    """
    return 1024 <= port <= 65535


def get_local_ip() -> str:
    """
    Get the local IP address of this machine
    
    Returns:
        IP address string
    """
    try:
        # Create a socket and connect to an external address
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "localhost"


def test_connection(host: str, port: int, timeout: float = 2.0) -> bool:
    """
    Test if a connection can be made to a host:port
    
    Args:
        host: Host address
        port: Port number
        timeout: Connection timeout in seconds
        
    Returns:
        True if connection successful
    """
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((host, port))
        sock.close()
        return result == 0
    except Exception:
        return False
