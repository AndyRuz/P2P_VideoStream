"""
Tracker Server for P2P Video Streaming Application
Helps peers discover each other and coordinate connections
Addresses the centralized bottleneck issue mentioned by professor
"""

import socket
import threading
import json
from typing import Dict, List, Tuple
import time


class TrackerServer:
    """
    Central tracker that helps peers discover each other.
    Note: While this provides initial discovery, the actual video sharing
    is fully P2P, addressing scalability and fault tolerance concerns.
    """
    
    def __init__(self, host: str = 'localhost', port: int = 6000):
        """
        Initialize the tracker server
        
        Args:
            host: IP address to bind to
            port: Port number to listen on
        """
        self.host = host
        self.port = port
        
        # Registry of active peers: {peer_id: (host, port, last_seen)}
        self.peer_registry: Dict[str, Tuple[str, int, float]] = {}
        
        # Video index: {video_id: [list of peer_ids that have it]}
        self.video_index: Dict[str, List[str]] = {}
        
        self.server_socket = None
        self.running = False
        self.lock = threading.Lock()
        
    def start(self):
        """Start the tracker server"""
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        try:
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(10)
            self.running = True
            
            print(f"[TRACKER] Started on {self.host}:{self.port}")
            
            # Start cleanup thread for inactive peers
            cleanup_thread = threading.Thread(target=self._cleanup_inactive_peers, daemon=True)
            cleanup_thread.start()
            
            # Start listening for connections
            self._listen_for_connections()
            
        except Exception as e:
            print(f"[TRACKER] Error starting server: {e}")
            return False
    
    def stop(self):
        """Stop the tracker server"""
        self.running = False
        if self.server_socket:
            try:
                self.server_socket.close()
            except:
                pass
        print("[TRACKER] Stopped")
    
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
                    print(f"[TRACKER] Error accepting connection: {e}")
    
    def _handle_peer_request(self, client_socket: socket.socket, address):
        """
        Handle requests from peers
        
        Args:
            client_socket: Socket connection to the peer
            address: Address of the peer
        """
        try:
            # Receive request
            request_data = client_socket.recv(4096).decode('utf-8')
            request = json.loads(request_data)
            
            request_type = request.get('type')
            
            if request_type == 'REGISTER':
                # Register a new peer
                response = self._register_peer(request)
                
            elif request_type == 'UNREGISTER':
                # Unregister a peer
                response = self._unregister_peer(request)
                
            elif request_type == 'GET_PEERS':
                # Get list of all active peers
                response = self._get_all_peers()
                
            elif request_type == 'ANNOUNCE_VIDEO':
                # Peer announces it has a video
                response = self._announce_video(request)
                
            elif request_type == 'FIND_VIDEO':
                # Find peers that have a specific video
                response = self._find_video(request)
                
            elif request_type == 'HEARTBEAT':
                # Peer heartbeat to stay active
                response = self._update_heartbeat(request)
                
            else:
                response = {'status': 'error', 'message': 'Unknown request type'}
            
            # Send response
            client_socket.send(json.dumps(response).encode('utf-8'))
            
        except Exception as e:
            print(f"[TRACKER] Error handling request: {e}")
            error_response = {'status': 'error', 'message': str(e)}
            try:
                client_socket.send(json.dumps(error_response).encode('utf-8'))
            except:
                pass
        finally:
            client_socket.close()
    
    def _register_peer(self, request: dict) -> dict:
        """
        Register a peer in the network
        
        Args:
            request: Registration request containing peer info
            
        Returns:
            Response dictionary
        """
        peer_id = request.get('peer_id')
        peer_host = request.get('host')
        peer_port = request.get('port')
        
        if not all([peer_id, peer_host, peer_port]):
            return {'status': 'error', 'message': 'Missing peer information'}
        
        with self.lock:
            self.peer_registry[peer_id] = (peer_host, peer_port, time.time())
        
        print(f"[TRACKER] Registered peer: {peer_id} at {peer_host}:{peer_port}")
        
        return {
            'status': 'success',
            'message': 'Peer registered successfully',
            'peer_count': len(self.peer_registry)
        }
    
    def _unregister_peer(self, request: dict) -> dict:
        """
        Unregister a peer from the network
        
        Args:
            request: Unregistration request
            
        Returns:
            Response dictionary
        """
        peer_id = request.get('peer_id')
        
        with self.lock:
            if peer_id in self.peer_registry:
                del self.peer_registry[peer_id]
                
                # Remove from video index
                for video_id in list(self.video_index.keys()):
                    if peer_id in self.video_index[video_id]:
                        self.video_index[video_id].remove(peer_id)
                    if not self.video_index[video_id]:
                        del self.video_index[video_id]
        
        print(f"[TRACKER] Unregistered peer: {peer_id}")
        
        return {'status': 'success', 'message': 'Peer unregistered'}
    
    def _get_all_peers(self) -> dict:
        """
        Get list of all active peers
        
        Returns:
            Response with list of peers
        """
        with self.lock:
            peers = [
                {
                    'peer_id': peer_id,
                    'host': host,
                    'port': port
                }
                for peer_id, (host, port, last_seen) in self.peer_registry.items()
            ]
        
        return {
            'status': 'success',
            'peers': peers,
            'count': len(peers)
        }
    
    def _announce_video(self, request: dict) -> dict:
        """
        Peer announces it has a video available
        
        Args:
            request: Announcement request
            
        Returns:
            Response dictionary
        """
        peer_id = request.get('peer_id')
        video_id = request.get('video_id')
        
        if not all([peer_id, video_id]):
            return {'status': 'error', 'message': 'Missing information'}
        
        with self.lock:
            if video_id not in self.video_index:
                self.video_index[video_id] = []
            
            if peer_id not in self.video_index[video_id]:
                self.video_index[video_id].append(peer_id)
        
        print(f"[TRACKER] Peer {peer_id} announced video {video_id}")
        
        return {'status': 'success', 'message': 'Video announced'}
    
    def _find_video(self, request: dict) -> dict:
        """
        Find which peers have a specific video
        
        Args:
            request: Video search request
            
        Returns:
            Response with list of peers that have the video
        """
        video_id = request.get('video_id')
        
        with self.lock:
            peer_ids = self.video_index.get(video_id, [])
            
            # Get full peer information
            peers_with_video = []
            for peer_id in peer_ids:
                if peer_id in self.peer_registry:
                    host, port, _ = self.peer_registry[peer_id]
                    peers_with_video.append({
                        'peer_id': peer_id,
                        'host': host,
                        'port': port
                    })
        
        return {
            'status': 'success',
            'peers': peers_with_video,
            'count': len(peers_with_video)
        }
    
    def _update_heartbeat(self, request: dict) -> dict:
        """
        Update the last seen time for a peer (heartbeat)
        
        Args:
            request: Heartbeat request
            
        Returns:
            Response dictionary
        """
        peer_id = request.get('peer_id')
        
        with self.lock:
            if peer_id in self.peer_registry:
                host, port, _ = self.peer_registry[peer_id]
                self.peer_registry[peer_id] = (host, port, time.time())
                return {'status': 'success'}
            else:
                return {'status': 'error', 'message': 'Peer not registered'}
    
    def _cleanup_inactive_peers(self):
        """Remove peers that haven't sent heartbeat in a while"""
        TIMEOUT = 300  # 5 minutes
        
        while self.running:
            try:
                time.sleep(60)  # Check every minute
                
                current_time = time.time()
                with self.lock:
                    inactive_peers = [
                        peer_id
                        for peer_id, (host, port, last_seen) in self.peer_registry.items()
                        if current_time - last_seen > TIMEOUT
                    ]
                    
                    for peer_id in inactive_peers:
                        print(f"[TRACKER] Removing inactive peer: {peer_id}")
                        del self.peer_registry[peer_id]
                        
                        # Clean up video index
                        for video_id in list(self.video_index.keys()):
                            if peer_id in self.video_index[video_id]:
                                self.video_index[video_id].remove(peer_id)
                            if not self.video_index[video_id]:
                                del self.video_index[video_id]
                
            except Exception as e:
                print(f"[TRACKER] Error in cleanup: {e}")
    
    def get_stats(self) -> dict:
        """Get tracker statistics"""
        with self.lock:
            return {
                'active_peers': len(self.peer_registry),
                'indexed_videos': len(self.video_index),
                'peers': list(self.peer_registry.keys())
            }


def start_tracker_server(host: str = 'localhost', port: int = 6000):
    """
    Convenience function to start the tracker server
    
    Args:
        host: Host address
        port: Port number
    """
    tracker = TrackerServer(host, port)
    try:
        tracker.start()
    except KeyboardInterrupt:
        print("\n[TRACKER] Shutting down...")
        tracker.stop()


if __name__ == "__main__":
    # Run tracker server standalone
    start_tracker_server()
