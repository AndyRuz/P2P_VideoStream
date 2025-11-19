"""
Peer class for P2P Video Streaming Application
Handles peer connections, video sharing, and network communication
"""

import socket
import threading
import json
import os
import hashlib
from typing import Dict, List, Tuple, Optional
import time


class Peer:
    """
    Represents a peer in the P2P network.
    Handles both server (receiving) and client (sending) functionalities.
    """
    
    def __init__(self, peer_id: str, host: str = 'localhost', port: int = 5000):
        """
        Initialize a peer node
        
        Args:
            peer_id: Unique identifier for this peer
            host: IP address to bind to
            port: Port number to listen on
        """
        self.peer_id = peer_id
        self.host = host
        self.port = port
        
        # Storage for videos this peer has
        self.video_library: Dict[str, dict] = {}
        self.video_directory = f"peer_videos_{peer_id}"
        
        # Connected peers in the network
        self.known_peers: List[Tuple[str, int]] = []
        
        # Server socket for receiving connections
        self.server_socket = None
        self.running = False
        
        # Lock for thread-safe operations
        self.lock = threading.Lock()
        
        # Create video directory if it doesn't exist
        os.makedirs(self.video_directory, exist_ok=True)
        
    def start(self):
        """Start the peer server to accept incoming connections"""
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        try:
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(5)
            self.running = True
            
            print(f"[PEER {self.peer_id}] Started on {self.host}:{self.port}")
            
            # Start listening for connections in a separate thread
            listener_thread = threading.Thread(target=self._listen_for_connections, daemon=True)
            listener_thread.start()
            
            return True
        except Exception as e:
            print(f"[PEER {self.peer_id}] Error starting server: {e}")
            return False
    
    def stop(self):
        """Stop the peer server"""
        self.running = False
        if self.server_socket:
            try:
                self.server_socket.close()
            except:
                pass
        print(f"[PEER {self.peer_id}] Stopped")
    
    def _listen_for_connections(self):
        """Listen for incoming peer connections"""
        while self.running:
            try:
                self.server_socket.settimeout(1.0)
                client_socket, address = self.server_socket.accept()
                
                # Handle each connection in a separate thread
                handler_thread = threading.Thread(
                    target=self._handle_peer_request,
                    args=(client_socket, address),
                    daemon=True
                )
                handler_thread.start()
                
            except socket.timeout:
                continue
            except Exception as e:
                if self.running:
                    print(f"[PEER {self.peer_id}] Error accepting connection: {e}")
    
    def _handle_peer_request(self, client_socket: socket.socket, address):
        """
        Handle requests from other peers
        
        Args:
            client_socket: Socket connection to the requesting peer
            address: Address of the requesting peer
        """
        try:
            # Receive request
            request_data = client_socket.recv(4096).decode('utf-8')
            request = json.loads(request_data)
            
            request_type = request.get('type')
            
            if request_type == 'LIST_VIDEOS':
                # Send list of available videos
                response = {
                    'status': 'success',
                    'videos': self._get_video_list()
                }
                client_socket.send(json.dumps(response).encode('utf-8'))
                
            elif request_type == 'DOWNLOAD_VIDEO':
                # Send requested video file
                video_id = request.get('video_id')
                self._send_video_file(client_socket, video_id)
                
            elif request_type == 'GET_VIDEO_INFO':
                # Send video metadata
                video_id = request.get('video_id')
                video_info = self.video_library.get(video_id, {})
                response = {
                    'status': 'success' if video_info else 'not_found',
                    'video_info': video_info
                }
                client_socket.send(json.dumps(response).encode('utf-8'))
            
        except Exception as e:
            print(f"[PEER {self.peer_id}] Error handling request: {e}")
        finally:
            client_socket.close()
    
    def add_video(self, video_path: str, video_name: str, description: str = "") -> Optional[str]:
        """
        Add a video to this peer's library
        
        Args:
            video_path: Path to the video file
            video_name: Display name for the video
            description: Optional description
            
        Returns:
            Video ID if successful, None otherwise
        """
        try:
            # Generate unique video ID based on file hash
            video_id = self._generate_video_id(video_path)
            
            # Get file size
            file_size = os.path.getsize(video_path)
            
            # Copy video to peer's directory
            new_path = os.path.join(self.video_directory, f"{video_id}.mp4")
            
            with open(video_path, 'rb') as src, open(new_path, 'wb') as dst:
                dst.write(src.read())
            
            # Add to video library
            with self.lock:
                self.video_library[video_id] = {
                    'id': video_id,
                    'name': video_name,
                    'description': description,
                    'size': file_size,
                    'path': new_path,
                    'added_time': time.time()
                }
            
            print(f"[PEER {self.peer_id}] Added video: {video_name} (ID: {video_id})")
            return video_id
            
        except Exception as e:
            print(f"[PEER {self.peer_id}] Error adding video: {e}")
            return None
    
    def _generate_video_id(self, video_path: str) -> str:
        """Generate a unique ID for a video file"""
        hasher = hashlib.md5()
        with open(video_path, 'rb') as f:
            # Read first 1MB for hash (faster for large files)
            hasher.update(f.read(1024 * 1024))
        return hasher.hexdigest()[:16]
    
    def _get_video_list(self) -> List[dict]:
        """Get list of videos available on this peer"""
        with self.lock:
            return [
                {
                    'id': vid_id,
                    'name': info['name'],
                    'description': info['description'],
                    'size': info['size']
                }
                for vid_id, info in self.video_library.items()
            ]
    
    def _send_video_file(self, client_socket: socket.socket, video_id: str):
        """
        Send a video file to a requesting peer
        
        Args:
            client_socket: Socket to send the video through
            video_id: ID of the video to send
        """
        try:
            video_info = self.video_library.get(video_id)
            
            if not video_info:
                # Send error response
                response = {'status': 'not_found'}
                client_socket.send(json.dumps(response).encode('utf-8'))
                return
            
            # Send success response with file size
            response = {
                'status': 'success',
                'size': video_info['size'],
                'name': video_info['name']
            }
            client_socket.send(json.dumps(response).encode('utf-8'))
            
            # Wait for acknowledgment
            ack = client_socket.recv(1024)
            
            # Send video file in chunks
            with open(video_info['path'], 'rb') as video_file:
                while True:
                    chunk = video_file.read(8192)  # 8KB chunks
                    if not chunk:
                        break
                    client_socket.send(chunk)
            
            print(f"[PEER {self.peer_id}] Sent video {video_id} to peer")
            
        except Exception as e:
            print(f"[PEER {self.peer_id}] Error sending video: {e}")
    
    def request_video_list(self, peer_host: str, peer_port: int) -> List[dict]:
        """
        Request list of videos from another peer
        
        Args:
            peer_host: Host address of the peer
            peer_port: Port of the peer
            
        Returns:
            List of available videos
        """
        try:
            # Connect to peer
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect((peer_host, peer_port))
            
            # Send request
            request = {'type': 'LIST_VIDEOS'}
            client_socket.send(json.dumps(request).encode('utf-8'))
            
            # Receive response
            response_data = client_socket.recv(4096).decode('utf-8')
            response = json.loads(response_data)
            
            client_socket.close()
            
            if response['status'] == 'success':
                return response['videos']
            else:
                return []
                
        except Exception as e:
            print(f"[PEER {self.peer_id}] Error requesting video list: {e}")
            return []
    
    def download_video(self, peer_host: str, peer_port: int, video_id: str, 
                       save_path: str = None) -> bool:
        """
        Download a video from another peer
        
        Args:
            peer_host: Host address of the peer
            peer_port: Port of the peer
            video_id: ID of the video to download
            save_path: Optional path to save the video
            
        Returns:
            True if download successful, False otherwise
        """
        try:
            # Connect to peer
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect((peer_host, peer_port))
            
            # Send download request
            request = {
                'type': 'DOWNLOAD_VIDEO',
                'video_id': video_id
            }
            client_socket.send(json.dumps(request).encode('utf-8'))
            
            # Receive response header
            response_data = client_socket.recv(4096).decode('utf-8')
            response = json.loads(response_data)
            
            if response['status'] != 'success':
                print(f"[PEER {self.peer_id}] Video not found on peer")
                client_socket.close()
                return False
            
            # Determine save path
            if not save_path:
                save_path = os.path.join(
                    self.video_directory,
                    f"{video_id}.mp4"
                )
            
            # Send acknowledgment
            client_socket.send(b'ACK')
            
            # Receive video file
            file_size = response['size']
            received = 0
            
            with open(save_path, 'wb') as video_file:
                while received < file_size:
                    chunk = client_socket.recv(8192)
                    if not chunk:
                        break
                    video_file.write(chunk)
                    received += len(chunk)
            
            client_socket.close()
            
            # Add to local library
            with self.lock:
                self.video_library[video_id] = {
                    'id': video_id,
                    'name': response['name'],
                    'description': '',
                    'size': file_size,
                    'path': save_path,
                    'added_time': time.time()
                }
            
            print(f"[PEER {self.peer_id}] Downloaded video {video_id}")
            return True
            
        except Exception as e:
            print(f"[PEER {self.peer_id}] Error downloading video: {e}")
            return False
    
    def add_known_peer(self, peer_host: str, peer_port: int):
        """
        Add a peer to the known peers list
        
        Args:
            peer_host: Host address of the peer
            peer_port: Port of the peer
        """
        peer_address = (peer_host, peer_port)
        if peer_address not in self.known_peers:
            self.known_peers.append(peer_address)
            print(f"[PEER {self.peer_id}] Added peer: {peer_host}:{peer_port}")
    
    def get_all_network_videos(self) -> Dict[Tuple[str, int], List[dict]]:
        """
        Get videos from all known peers in the network
        
        Returns:
            Dictionary mapping peer addresses to their video lists
        """
        network_videos = {}
        
        for peer_host, peer_port in self.known_peers:
            videos = self.request_video_list(peer_host, peer_port)
            if videos:
                network_videos[(peer_host, peer_port)] = videos
        
        return network_videos
    
    def get_peer_info(self) -> dict:
        """Get information about this peer"""
        return {
            'peer_id': self.peer_id,
            'host': self.host,
            'port': self.port,
            'video_count': len(self.video_library),
            'known_peers': len(self.known_peers)
        }
