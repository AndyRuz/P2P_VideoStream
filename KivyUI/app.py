"""
Kivy UI for P2P Video Streaming Application
Main interface controller using Kivy framework
"""

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.popup import Popup
from kivy.properties import StringProperty, BooleanProperty, ObjectProperty
from kivy.clock import Clock
from kivy.core.window import Window
from typing import Optional, Callable
import threading
import os

# Try to import filechooser
try:
    from plyer import filechooser
    HAS_PLYER = True
except ImportError:
    HAS_PLYER = False
    from kivy.uix.filechooser import FileChooserIconView


class SettingsPopup(Popup):
    """Settings popup for theme and display options"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.title = "⚙️ Settings"
        self.size_hint = (0.8, 0.7)
        
        content = BoxLayout(orientation='vertical', padding=20, spacing=15)
        
        # Theme setting
        content.add_widget(Label(text='Color Theme:', size_hint_y=0.2, font_size='18sp', bold=True))
        
        theme_box = BoxLayout(size_hint_y=0.2, spacing=10)
        self.light_mode_btn = Button(text='☀️ Light Mode')
        self.dark_mode_btn = Button(text='🌙 Dark Mode')
        self.light_mode_btn.bind(on_release=self.set_light_mode)
        self.dark_mode_btn.bind(on_release=self.set_dark_mode)
        theme_box.add_widget(self.light_mode_btn)
        theme_box.add_widget(self.dark_mode_btn)
        content.add_widget(theme_box)
        
        # Resolution/Format setting
        content.add_widget(Label(text='Display Format:', size_hint_y=0.2, font_size='18sp', bold=True))
        
        format_box = BoxLayout(size_hint_y=0.2, spacing=10)
        self.pc_btn = Button(text='💻 PC')
        self.mobile_btn = Button(text='📱 Mobile')
        self.pc_btn.bind(on_release=self.set_pc_format)
        self.mobile_btn.bind(on_release=self.set_mobile_format)
        format_box.add_widget(self.pc_btn)
        format_box.add_widget(self.mobile_btn)
        content.add_widget(format_box)
        
        # Current settings display
        self.current_settings = Label(text='', size_hint_y=0.3)
        content.add_widget(self.current_settings)
        
        # Close button
        close_btn = Button(text='Close', size_hint_y=0.2)
        close_btn.bind(on_release=self.dismiss)
        content.add_widget(close_btn)
        
        self.content = content
        self.update_display()
    
    def set_light_mode(self, instance):
        """Set light mode theme"""
        app = App.get_running_app()
        app.theme_mode = 'light'
        Window.clearcolor = (1, 1, 1, 1)
        self.update_display()
    
    def set_dark_mode(self, instance):
        """Set dark mode theme"""
        app = App.get_running_app()
        app.theme_mode = 'dark'
        Window.clearcolor = (0.1, 0.1, 0.1, 1)
        self.update_display()
    
    def set_pc_format(self, instance):
        """Set PC display format"""
        app = App.get_running_app()
        app.display_format = 'pc'
        Window.size = (900, 700)
        self.update_display()
    
    def set_mobile_format(self, instance):
        """Set mobile display format"""
        app = App.get_running_app()
        app.display_format = 'mobile'
        Window.size = (400, 700)
        self.update_display()
    
    def update_display(self):
        """Update the current settings display"""
        app = App.get_running_app()
        theme = app.theme_mode.title()
        format_type = app.display_format.upper()
        self.current_settings.text = f'Current: {theme} Mode | {format_type} Format'


class PeerConfigScreen(Screen):
    """Screen for peer configuration"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.peer_started = False
        self.on_start_peer: Optional[Callable] = None
        
    def start_peer(self):
        """Handle start peer button"""
        peer_id = self.ids.peer_id_input.text
        port = self.ids.port_input.text
        tracker_host = self.ids.tracker_host_input.text
        tracker_port = self.ids.tracker_port_input.text
        
        if not peer_id:
            self.show_message("Please enter a Peer ID", error=True)
            return
        
        try:
            port = int(port)
            tracker_port = int(tracker_port)
        except ValueError:
            self.show_message("Port numbers must be integers", error=True)
            return
        
        if self.on_start_peer:
            self.on_start_peer(peer_id, port, tracker_host, tracker_port)
    
    def set_peer_started(self):
        """Update UI when peer starts"""
        self.peer_started = True
        self.ids.status_label.text = "🟢 Peer running"
        self.ids.start_button.disabled = True
        self.ids.peer_id_input.disabled = True
        self.ids.port_input.disabled = True
        
        # Switch to my videos screen
        app = App.get_running_app()
        app.root.current = 'my_videos'
    
    def show_message(self, message, error=False):
        """Show status message"""
        self.ids.status_label.text = message
        if error:
            self.ids.status_label.color = (1, 0, 0, 1)
        else:
            self.ids.status_label.color = (0, 1, 0, 1)
    
    def show_settings(self):
        """Show settings popup"""
        settings = SettingsPopup()
        settings.open()


class MyVideosScreen(Screen):
    """Screen for displaying user's videos"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.on_upload_video: Optional[Callable] = None
    
    def upload_video(self):
        """Handle upload video button - open file chooser"""
        if HAS_PLYER:
            # Use plyer for cross-platform file chooser
            try:
                filechooser.open_file(
                    on_selection=self.handle_file_selection,
                    filters=[("Video files", "*.mp4;*.avi;*.mov;*.mkv;*.flv")]
                )
            except Exception as e:
                print(f"Plyer file chooser error: {e}")
                self.show_kivy_file_chooser()
        else:
            # Fallback to Kivy's built-in file chooser
            self.show_kivy_file_chooser()
    
    def show_kivy_file_chooser(self):
        """Show Kivy's built-in file chooser"""
        content = BoxLayout(orientation='vertical')
        
        file_chooser = FileChooserIconView(
            filters=['*.mp4', '*.avi', '*.mov', '*.mkv', '*.flv']
        )
        content.add_widget(file_chooser)
        
        button_box = BoxLayout(size_hint_y=0.1, spacing=10)
        select_btn = Button(text='Select')
        cancel_btn = Button(text='Cancel')
        button_box.add_widget(select_btn)
        button_box.add_widget(cancel_btn)
        content.add_widget(button_box)
        
        popup = Popup(title='Choose Video File', content=content, size_hint=(0.9, 0.9))
        
        def on_select(instance):
            if file_chooser.selection:
                self.handle_file_selection(file_chooser.selection)
            popup.dismiss()
        
        select_btn.bind(on_release=on_select)
        cancel_btn.bind(on_release=popup.dismiss)
        
        popup.open()
    
    def handle_file_selection(self, selection):
        """Handle selected file"""
        if not selection:
            return
        
        file_path = selection[0] if isinstance(selection, list) else selection
        
        # Show dialog to get video name and description
        self.show_video_info_dialog(file_path)
    
    def show_video_info_dialog(self, file_path):
        """Show dialog to enter video information"""
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        file_name = os.path.basename(file_path)
        content.add_widget(Label(text=f'File: {file_name}', size_hint_y=0.2))
        
        name_input = TextInput(hint_text='Video Name', text=file_name, multiline=False, size_hint_y=0.2)
        content.add_widget(name_input)
        
        desc_input = TextInput(hint_text='Description (optional)', multiline=True, size_hint_y=0.3)
        content.add_widget(desc_input)
        
        button_box = BoxLayout(size_hint_y=0.2, spacing=10)
        upload_btn = Button(text='Upload')
        cancel_btn = Button(text='Cancel')
        button_box.add_widget(upload_btn)
        button_box.add_widget(cancel_btn)
        content.add_widget(button_box)
        
        popup = Popup(title='Video Information', content=content, size_hint=(0.8, 0.6))
        
        def on_upload(instance):
            video_name = name_input.text or file_name
            description = desc_input.text
            if self.on_upload_video:
                self.on_upload_video(file_path, video_name, description)
            popup.dismiss()
        
        upload_btn.bind(on_release=on_upload)
        cancel_btn.bind(on_release=popup.dismiss)
        
        popup.open()
    
    def add_video(self, video_id, video_name, size):
        """Add a video to the list"""
        video_label = Label(
            text=f"🎬 {video_name}\nSize: {self._format_size(size)}\nID: {video_id[:8]}...",
            size_hint_y=None,
            height=80,
            halign='left',
            valign='middle'
        )
        video_label.bind(size=video_label.setter('text_size'))
        self.ids.videos_list.add_widget(video_label)
    
    def clear_videos(self):
        """Clear all videos from list"""
        self.ids.videos_list.clear_widgets()
    
    def show_settings(self):
        """Show settings popup"""
        settings = SettingsPopup()
        settings.open()
    
    def _format_size(self, size_bytes):
        """Format file size"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} TB"


class NetworkBrowseScreen(Screen):
    """Screen for browsing network videos"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.on_browse_network: Optional[Callable] = None
        self.on_download_video: Optional[Callable] = None
    
    def refresh_network(self):
        """Handle refresh network button"""
        if self.on_browse_network:
            self.on_browse_network()
    
    def add_network_video(self, video_id, video_name, size, peer_host, peer_port):
        """Add a network video to the list"""
        container = BoxLayout(size_hint_y=None, height=80, spacing=10)
        
        info_label = Label(
            text=f"☁️ {video_name}\nSize: {self._format_size(size)}\nFrom: {peer_host}:{peer_port}",
            halign='left',
            valign='middle'
        )
        info_label.bind(size=info_label.setter('text_size'))
        
        download_btn = Button(
            text="⬇️ Download",
            size_hint_x=0.3,
            on_release=lambda x: self.download_video(video_id, peer_host, peer_port)
        )
        
        container.add_widget(info_label)
        container.add_widget(download_btn)
        self.ids.network_videos_list.add_widget(container)
    
    def download_video(self, video_id, peer_host, peer_port):
        """Handle download video"""
        if self.on_download_video:
            self.on_download_video(video_id, peer_host, peer_port)
    
    def clear_network_videos(self):
        """Clear all network videos"""
        self.ids.network_videos_list.clear_widgets()
    
    def show_settings(self):
        """Show settings popup"""
        settings = SettingsPopup()
        settings.open()
    
    def _format_size(self, size_bytes):
        """Format file size"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} TB"


class PeersScreen(Screen):
    """Screen for displaying connected peers"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.on_connect_to_peer: Optional[Callable] = None
    
    def connect_to_peer(self):
        """Handle connect to peer button"""
        host = self.ids.peer_host_input.text
        port = self.ids.peer_port_input.text
        
        if not host or not port:
            return
        
        try:
            port = int(port)
        except ValueError:
            return
        
        if self.on_connect_to_peer:
            self.on_connect_to_peer(host, port)
    
    def add_peer(self, peer_id, host, port):
        """Add a peer to the list"""
        peer_label = Label(
            text=f"💻 {peer_id}\n{host}:{port}",
            size_hint_y=None,
            height=60,
            halign='left',
            valign='middle'
        )
        peer_label.bind(size=peer_label.setter('text_size'))
        self.ids.peers_list.add_widget(peer_label)
    
    def clear_peers(self):
        """Clear all peers"""
        self.ids.peers_list.clear_widgets()
    
    def set_my_peer_info(self, peer_id, host, port):
        """Set current user's peer information"""
        self.ids.my_peer_info.text = f"📍 Your Info:\nPeer ID: {peer_id}\nHost: {host}\nPort: {port}"
    
    def show_settings(self):
        """Show settings popup"""
        settings = SettingsPopup()
        settings.open()


class P2PVideoStreamApp(App):
    """Main Kivy application"""
    
    theme_mode = StringProperty('light')
    display_format = StringProperty('pc')
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.peer = None
        self.tracker_host = "localhost"
        self.tracker_port = 6000
        self.peer_id = None
        self.peer_host = None
        self.peer_port = None
    
    def build(self):
        """Build the application"""
        self.title = "P2P Video Streaming"
        
        # Set initial window size
        Window.size = (900, 700)
        Window.clearcolor = (1, 1, 1, 1)
        
        # Create screen manager
        sm = ScreenManager()
        
        # Add screens
        self.config_screen = PeerConfigScreen(name='config')
        self.my_videos_screen = MyVideosScreen(name='my_videos')
        self.network_screen = NetworkBrowseScreen(name='network')
        self.peers_screen = PeersScreen(name='peers')
        
        sm.add_widget(self.config_screen)
        sm.add_widget(self.my_videos_screen)
        sm.add_widget(self.network_screen)
        sm.add_widget(self.peers_screen)
        
        # Set callbacks
        self.config_screen.on_start_peer = self.start_peer
        self.my_videos_screen.on_upload_video = self.upload_video
        self.network_screen.on_browse_network = self.browse_network
        self.network_screen.on_download_video = self.download_video
        self.peers_screen.on_connect_to_peer = self.connect_to_peer
        
        return sm
    
    def start_peer(self, peer_id, port, tracker_host, tracker_port):
        """Start the peer node"""
        try:
            from Server import Peer, register_with_tracker, get_peers_from_tracker
            
            self.tracker_host = tracker_host
            self.tracker_port = tracker_port
            self.peer_id = peer_id
            self.peer_host = 'localhost'
            self.peer_port = port
            
            # Create and start peer
            self.peer = Peer(peer_id=peer_id, host='localhost', port=port)
            
            if self.peer.start():
                # Register with tracker
                success = register_with_tracker(
                    peer_id=peer_id,
                    peer_host='localhost',
                    peer_port=port,
                    tracker_host=tracker_host,
                    tracker_port=tracker_port
                )
                
                if success:
                    Clock.schedule_once(lambda dt: self.config_screen.set_peer_started(), 0)
                    Clock.schedule_once(lambda dt: self._load_existing_videos(), 0.1)
                    Clock.schedule_once(lambda dt: self._refresh_peers(), 0.2)
                    Clock.schedule_once(lambda dt: self._set_my_peer_info(), 0.3)
                else:
                    Clock.schedule_once(
                        lambda dt: self.config_screen.show_message(
                            "Failed to register with tracker", error=True
                        ), 0
                    )
            else:
                Clock.schedule_once(
                    lambda dt: self.config_screen.show_message(
                        "Failed to start peer", error=True
                    ), 0
                )
        except Exception as e:
            Clock.schedule_once(
                lambda dt: self.config_screen.show_message(
                    f"Error: {str(e)}", error=True
                ), 0
            )
    
    def upload_video(self, file_path, video_name, description):
        """Handle video upload"""
        if not self.peer:
            return
        
        def do_upload():
            from Server import announce_video_to_tracker
            
            video_id = self.peer.add_video(file_path, video_name, description)
            
            if video_id:
                # Announce to tracker
                announce_video_to_tracker(
                    peer_id=self.peer.peer_id,
                    video_id=video_id,
                    tracker_host=self.tracker_host,
                    tracker_port=self.tracker_port
                )
                
                # Update UI
                video_info = self.peer.video_library[video_id]
                Clock.schedule_once(
                    lambda dt: self.my_videos_screen.add_video(
                        video_id, video_name, video_info['size']
                    ), 0
                )
        
        threading.Thread(target=do_upload, daemon=True).start()
    
    def browse_network(self):
        """Browse videos on the network"""
        if not self.peer:
            return
        
        def do_browse():
            self.network_screen.clear_network_videos()
            network_videos = self.peer.get_all_network_videos()
            
            for (peer_host, peer_port), videos in network_videos.items():
                for video in videos:
                    Clock.schedule_once(
                        lambda dt, v=video, h=peer_host, p=peer_port: 
                        self.network_screen.add_network_video(
                            v['id'], v['name'], v['size'], h, p
                        ), 0
                    )
        
        threading.Thread(target=do_browse, daemon=True).start()
    
    def download_video(self, video_id, peer_host, peer_port):
        """Download a video from another peer"""
        if not self.peer:
            return
        
        def do_download():
            from Server import announce_video_to_tracker
            
            success = self.peer.download_video(peer_host, peer_port, video_id)
            
            if success:
                # Announce to tracker
                announce_video_to_tracker(
                    peer_id=self.peer.peer_id,
                    video_id=video_id,
                    tracker_host=self.tracker_host,
                    tracker_port=self.tracker_port
                )
                
                # Update UI
                video_info = self.peer.video_library[video_id]
                Clock.schedule_once(
                    lambda dt: self.my_videos_screen.add_video(
                        video_id, video_info['name'], video_info['size']
                    ), 0
                )
        
        threading.Thread(target=do_download, daemon=True).start()
    
    def connect_to_peer(self, peer_host, peer_port):
        """Connect to a peer manually"""
        if not self.peer:
            return
        
        self.peer.add_known_peer(peer_host, peer_port)
        self.peers_screen.add_peer(f"Peer@{peer_host}:{peer_port}", peer_host, peer_port)
    
    def _load_existing_videos(self):
        """Load existing videos from peer library"""
        if not self.peer:
            return
        
        for video_id, video_info in self.peer.video_library.items():
            self.my_videos_screen.add_video(
                video_id, video_info['name'], video_info['size']
            )
    
    def _refresh_peers(self):
        """Refresh list of known peers"""
        if not self.peer:
            return
        
        from Server import get_peers_from_tracker
        
        peers = get_peers_from_tracker(
            tracker_host=self.tracker_host,
            tracker_port=self.tracker_port
        )
        
        self.peers_screen.clear_peers()
        
        for peer_info in peers:
            if peer_info['peer_id'] != self.peer.peer_id:
                peer_host = peer_info['host']
                peer_port = peer_info['port']
                
                self.peer.add_known_peer(peer_host, peer_port)
                self.peers_screen.add_peer(
                    peer_info['peer_id'], peer_host, peer_port
                )
    
    def _set_my_peer_info(self):
        """Set current user's peer information in Peers screen"""
        if self.peer:
            self.peers_screen.set_my_peer_info(
                self.peer_id, self.peer_host, self.peer_port
            )
