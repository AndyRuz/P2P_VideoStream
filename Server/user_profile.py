"""
User Profile Management for P2P Video Streaming
Handles saving and loading user profiles
"""

import json
import os
from typing import Optional, List, Dict

PROFILES_DIR = "user_profiles"
PROFILES_FILE = os.path.join(PROFILES_DIR, "profiles.json")

def ensure_profiles_directory():
    """Ensure the profiles directory exists"""
    if not os.path.exists(PROFILES_DIR):
        os.makedirs(PROFILES_DIR)

def load_all_profiles() -> List[Dict]:
    """
    Load all user profiles
    
    Returns:
        List of profile dictionaries
    """
    ensure_profiles_directory()
    
    if not os.path.exists(PROFILES_FILE):
        return []
    
    try:
        with open(PROFILES_FILE, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading profiles: {e}")
        return []

def save_profile(peer_id: str, port: int, tracker_host: str, tracker_port: int, 
                friends: List[Dict] = None) -> bool:
    """
    Save or update a user profile
    
    Args:
        peer_id: Peer ID
        port: Port number
        tracker_host: Tracker host
        tracker_port: Tracker port
        friends: List of friend dictionaries
        
    Returns:
        True if successful
    """
    ensure_profiles_directory()
    
    profiles = load_all_profiles()
    
    # Check if profile exists
    profile_exists = False
    for i, profile in enumerate(profiles):
        if profile['peer_id'] == peer_id:
            # Update existing profile
            profiles[i] = {
                'peer_id': peer_id,
                'port': port,
                'tracker_host': tracker_host,
                'tracker_port': tracker_port,
                'friends': friends or []
            }
            profile_exists = True
            break
    
    if not profile_exists:
        # Add new profile
        profiles.append({
            'peer_id': peer_id,
            'port': port,
            'tracker_host': tracker_host,
            'tracker_port': tracker_port,
            'friends': friends or []
        })
    
    try:
        with open(PROFILES_FILE, 'w') as f:
            json.dump(profiles, f, indent=2)
        return True
    except Exception as e:
        print(f"Error saving profile: {e}")
        return False

def load_profile(peer_id: str) -> Optional[Dict]:
    """
    Load a specific user profile
    
    Args:
        peer_id: Peer ID to load
        
    Returns:
        Profile dictionary or None
    """
    profiles = load_all_profiles()
    
    for profile in profiles:
        if profile['peer_id'] == peer_id:
            return profile
    
    return None

def delete_profile(peer_id: str) -> bool:
    """
    Delete a user profile
    
    Args:
        peer_id: Peer ID to delete
        
    Returns:
        True if successful
    """
    ensure_profiles_directory()
    
    profiles = load_all_profiles()
    profiles = [p for p in profiles if p['peer_id'] != peer_id]
    
    try:
        with open(PROFILES_FILE, 'w') as f:
            json.dump(profiles, f, indent=2)
        
        # Also delete the peer's video directory
        video_dir = f"peer_videos_{peer_id}"
        if os.path.exists(video_dir):
            import shutil
            shutil.rmtree(video_dir)
        
        return True
    except Exception as e:
        print(f"Error deleting profile: {e}")
        return False

def add_friend(peer_id: str, friend_peer_id: str, friend_host: str, friend_port: int) -> bool:
    """
    Add a friend to a user's profile
    
    Args:
        peer_id: User's peer ID
        friend_peer_id: Friend's peer ID
        friend_host: Friend's host
        friend_port: Friend's port
        
    Returns:
        True if successful
    """
    profile = load_profile(peer_id)
    if not profile:
        return False
    
    friends = profile.get('friends', [])
    
    # Check if friend already exists
    for friend in friends:
        if friend['peer_id'] == friend_peer_id:
            # Update existing friend
            friend['host'] = friend_host
            friend['port'] = friend_port
            return save_profile(
                peer_id, 
                profile['port'], 
                profile['tracker_host'], 
                profile['tracker_port'], 
                friends
            )
    
    # Add new friend
    friends.append({
        'peer_id': friend_peer_id,
        'host': friend_host,
        'port': friend_port
    })
    
    return save_profile(
        peer_id, 
        profile['port'], 
        profile['tracker_host'], 
        profile['tracker_port'], 
        friends
    )

def remove_friend(peer_id: str, friend_peer_id: str) -> bool:
    """
    Remove a friend from a user's profile
    
    Args:
        peer_id: User's peer ID
        friend_peer_id: Friend's peer ID to remove
        
    Returns:
        True if successful
    """
    profile = load_profile(peer_id)
    if not profile:
        return False
    
    friends = profile.get('friends', [])
    friends = [f for f in friends if f['peer_id'] != friend_peer_id]
    
    return save_profile(
        peer_id, 
        profile['port'], 
        profile['tracker_host'], 
        profile['tracker_port'], 
        friends
    )

def get_friends(peer_id: str) -> List[Dict]:
    """
    Get list of friends for a user
    
    Args:
        peer_id: User's peer ID
        
    Returns:
        List of friend dictionaries
    """
    profile = load_profile(peer_id)
    if not profile:
        return []
    
    return profile.get('friends', [])