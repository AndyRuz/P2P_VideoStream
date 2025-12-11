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
        self.light_mode_btn = Button(text='Light Mode')
        self.dark_mode_btn = Button(text='Dark Mode')
        self.light_mode_btn.bind(on_release=self.set_light_mode)
        self.dark_mode_btn.bind(on_release=self.set_dark_mode)
        theme_box.add_widget(self.light_mode_btn)
        theme_box.add_widget(self.dark_mode_btn)
        content.add_widget(theme_box)
        
        # Resolution/Format setting
        content.add_widget(Label(text='Display Format:', size_hint_y=0.2, font_size='18sp', bold=True))
        
        format_box = BoxLayout(size_hint_y=0.2, spacing=10)
        self.pc_btn = Button(text='PC')
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
        app.update_theme_colors()
        self.update_display()
    
    def set_dark_mode(self, instance):
        """Set dark mode theme"""
        app = App.get_running_app()
        app.theme_mode = 'dark'
        Window.clearcolor = (0.1, 0.1, 0.1, 1)
        app.update_theme_colors()
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
        self.on_load_profile: Optional[Callable] = None
        
    def on_enter(self):
        """Called when screen is displayed"""
        self.load_profiles()
    
    def load_profiles(self):
        """Load existing profiles"""
        from Server import load_all_profiles
        
        self.ids.profiles_list.clear_widgets()
        profiles = load_all_profiles()
        
        for profile in profiles:
            self.add_profile_button(profile)
    
    def add_profile_button(self, profile):
        """Add a profile selection button"""
        peer_id = profile['peer_id']
        port = profile['port']
        
        btn = Button(
            text=f"{peer_id}\nPort: {port}",
            size_hint_y=None,
            height=60,
            on_release=lambda x: self.select_profile(profile)
        )
        self.ids.profiles_list.add_widget(btn)
    
    def select_profile(self, profile):
        """Select an existing profile"""
        if self.on_load_profile:
            self.on_load_profile(
                profile['peer_id'],
                profile['port'],
                profile['tracker_host'],
                profile['tracker_port']
            )
    
    def start_peer(self):
        """Handle start peer button with new profile"""
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
        self.ids.status_label.text = "Peer running"
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
        self.on_delete_video: Optional[Callable] = None
        self.on_edit_video: Optional[Callable] = None
        self.on_upload_to_network: Optional[Callable] = None
        self.on_download_to_device: Optional[Callable] = None
    
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
    
    def add_uploaded_video(self, video_id, video_name, size, is_on_network=False):
        """Add a video to the uploaded videos list"""
        container = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            height=120,
            padding=10,
            spacing=5
        )
    
        # Video info section
        info_section = BoxLayout(
            orientation='horizontal',
            size_hint_y=0.7,
            spacing=10
        )
    
        # Video details
        info_label = Label(
            text=f"🎬 {video_name}\nSize: {self._format_size(size)}\nID: {video_id[:8]}...",
            size_hint_x=0.6,
            halign='left',
            valign='middle',
            font_size='14sp'
        )
        info_label.bind(size=info_label.setter('text_size'))
        info_section.add_widget(info_label)
    
        # Status indicator
        status = "On Network" if is_on_network else "Local Only"
        status_label = Label(
            text=status,
            size_hint_x=0.4,
            font_size='12sp',
            color=(0.4, 1, 0.4, 1) if is_on_network else (1, 1, 0.4, 1)
        )
        info_section.add_widget(status_label)
    
        # Button to open options
        options_btn = Button(
            text='⋮ Options',
            size_hint_y=0.3,
            on_release=lambda x: self.show_uploaded_video_options(video_id, video_name, size, is_on_network)
        )
    
        container.add_widget(info_section)
        container.add_widget(options_btn)
    
        # Add border styling
        from kivy.graphics import Color, Line
        with container.canvas.before:
            Color(0.3, 0.3, 0.3, 1)
            Line(rectangle=(container.x, container.y, container.width, container.height), width=1.2)
    
        self.ids.uploaded_videos_list.add_widget(container)
    
    def add_downloaded_video(self, video_id, video_name, size, peer_info):
        """Add a video to the downloaded videos list"""
        container = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            height=120,
            padding=10,
            spacing=5
        )
    
        # Video info section
        info_section = BoxLayout(
            orientation='vertical',
            size_hint_y=0.7,
            spacing=5
        )
    
        # Video name
        name_label = Label(
            text=f"{video_name}",
            size_hint_y=0.4,
            halign='left',
            valign='middle',
            font_size='14sp',
            bold=True
        )
        name_label.bind(size=name_label.setter('text_size'))
        info_section.add_widget(name_label)
    
        # Details
        details_label = Label(
            text=f"Size: {self._format_size(size)} | From: {peer_info}",
            size_hint_y=0.6,
            halign='left',
            valign='middle',
            font_size='12sp'
        )
        details_label.bind(size=details_label.setter('text_size'))
        info_section.add_widget(details_label)
    
        # Button to open options
        options_btn = Button(
            text='⋮ Options',
            size_hint_y=0.3,
            on_release=lambda x: self.show_downloaded_video_options(video_id, video_name)
        )
    
        container.add_widget(info_section)
        container.add_widget(options_btn)
    
        # Add border styling
        from kivy.graphics import Color, Line
        with container.canvas.before:
            Color(0.3, 0.3, 0.3, 1)
            Line(rectangle=(container.x, container.y, container.width, container.height), width=1.2)
    
        self.ids.downloaded_videos_list.add_widget(container)
    
    def show_uploaded_video_options(self, video_id, video_name, size, is_on_network):
        """Show options popup for uploaded videos"""
        content = BoxLayout(orientation='vertical', padding=20, spacing=15)
    
        content.add_widget(Label(
            text=f'Options for:\n{video_name}',
            size_hint_y=0.25,
            font_size='18sp',
            bold=True
        ))
    
        # Play button
        play_btn = Button(text='Play Video', size_hint_y=0.15)
        play_btn.bind(on_release=lambda x: self.play_video(video_id, popup))
        content.add_widget(play_btn)
    
        # Edit button
        edit_btn = Button(text='Edit Info', size_hint_y=0.15)
        edit_btn.bind(on_release=lambda x: self.edit_video_info(video_id, video_name, popup))
        content.add_widget(edit_btn)
    
        # Upload to network button (only if not already on network)
        if not is_on_network:
            upload_network_btn = Button(text='Upload to Network', size_hint_y=0.15)
            upload_network_btn.bind(on_release=lambda x: self.upload_to_network(video_id, popup))
            content.add_widget(upload_network_btn)
        else:
            content.add_widget(Label(text='Already on Network', size_hint_y=0.15, color=(0.4, 1, 0.4, 1)))
    
        # Delete button
        delete_btn = Button(text='Delete', size_hint_y=0.15, background_color=(0.8, 0.2, 0.2, 1))
        delete_btn.bind(on_release=lambda x: self.confirm_delete_video(video_id, video_name, popup))
        content.add_widget(delete_btn)
    
        # Cancel button
        cancel_btn = Button(text='Cancel', size_hint_y=0.15)
        content.add_widget(cancel_btn)
    
        popup = Popup(title='Video Options', content=content, size_hint=(0.7, 0.8))
        cancel_btn.bind(on_release=popup.dismiss)
        popup.open()
    
    def show_downloaded_video_options(self, video_id, video_name):
        """Show options popup for downloaded videos"""
        content = BoxLayout(orientation='vertical', padding=20, spacing=15)
    
        content.add_widget(Label(
            text=f'Options for:\n{video_name}',
            size_hint_y=0.3,
            font_size='18sp',
            bold=True
        ))
    
        # Play button
        play_btn = Button(text='▶Play Video', size_hint_y=0.2)
        play_btn.bind(on_release=lambda x: self.play_video(video_id, popup))
        content.add_widget(play_btn)
    
        # Download to device button
        download_btn = Button(text='Download to Device', size_hint_y=0.2)
        download_btn.bind(on_release=lambda x: self.download_to_device(video_id, video_name, popup))
        content.add_widget(download_btn)
    
        # Delete button
        delete_btn = Button(text='Remove from Library', size_hint_y=0.2, background_color=(0.8, 0.2, 0.2, 1))
        delete_btn.bind(on_release=lambda x: self.confirm_delete_downloaded_video(video_id, video_name, popup))
        content.add_widget(delete_btn)
    
        # Cancel button
        cancel_btn = Button(text='Cancel', size_hint_y=0.1)
        content.add_widget(cancel_btn)
    
        popup = Popup(title='Video Options', content=content, size_hint=(0.7, 0.7))
        cancel_btn.bind(on_release=popup.dismiss)
        popup.open()
    
    def edit_video_info(self, video_id, current_name, parent_popup):
        """Show dialog to edit video information"""
        parent_popup.dismiss()
        
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        content.add_widget(Label(text='Edit Video Information', size_hint_y=0.2, font_size='18sp'))
        
        name_input = TextInput(hint_text='Video Name', text=current_name, multiline=False, size_hint_y=0.2)
        content.add_widget(name_input)
        
        desc_input = TextInput(hint_text='Description', multiline=True, size_hint_y=0.3)
        content.add_widget(desc_input)
        
        button_box = BoxLayout(size_hint_y=0.2, spacing=10)
        save_btn = Button(text='Save')
        cancel_btn = Button(text='Cancel')
        button_box.add_widget(save_btn)
        button_box.add_widget(cancel_btn)
        content.add_widget(button_box)
        
        popup = Popup(title='Edit Video', content=content, size_hint=(0.8, 0.6))
        
        def on_save(instance):
            new_name = name_input.text
            new_desc = desc_input.text
            if self.on_edit_video:
                self.on_edit_video(video_id, new_name, new_desc)
            popup.dismiss()
            self.refresh_video_lists()
        
        save_btn.bind(on_release=on_save)
        cancel_btn.bind(on_release=popup.dismiss)
        popup.open()
    
    def upload_to_network(self, video_id, parent_popup):
        """Upload video to network"""
        if self.on_upload_to_network:
            self.on_upload_to_network(video_id)
        parent_popup.dismiss()
        self.refresh_video_lists()
    
    def confirm_delete_video(self, video_id, video_name, parent_popup):
        """Show confirmation dialog before deleting"""
        parent_popup.dismiss()
        
        content = BoxLayout(orientation='vertical', padding=20, spacing=15)
        
        content.add_widget(Label(
            text=f'Are you sure you want to delete:\n\n{video_name}\n\nThis cannot be undone.',
            size_hint_y=0.6
        ))
        
        button_box = BoxLayout(size_hint_y=0.4, spacing=10)
        confirm_btn = Button(text='Delete', background_color=(0.8, 0.2, 0.2, 1))
        cancel_btn = Button(text='Cancel')
        button_box.add_widget(confirm_btn)
        button_box.add_widget(cancel_btn)
        content.add_widget(button_box)
        
        popup = Popup(title='Confirm Delete', content=content, size_hint=(0.7, 0.5))
        
        def on_confirm(instance):
            if self.on_delete_video:
                self.on_delete_video(video_id, is_uploaded=True)
            popup.dismiss()
            self.refresh_video_lists()
        
        confirm_btn.bind(on_release=on_confirm)
        cancel_btn.bind(on_release=popup.dismiss)
        popup.open()
    
    def confirm_delete_downloaded_video(self, video_id, video_name, parent_popup):
        """Show confirmation dialog before deleting downloaded video"""
        parent_popup.dismiss()
        
        content = BoxLayout(orientation='vertical', padding=20, spacing=15)
        
        content.add_widget(Label(
            text=f'Remove this video from your library?\n\n{video_name}\n\nYou can download it again later.',
            size_hint_y=0.6
        ))
        
        button_box = BoxLayout(size_hint_y=0.4, spacing=10)
        confirm_btn = Button(text='Remove', background_color=(0.8, 0.2, 0.2, 1))
        cancel_btn = Button(text='Cancel')
        button_box.add_widget(confirm_btn)
        button_box.add_widget(cancel_btn)
        content.add_widget(button_box)
        
        popup = Popup(title='Confirm Remove', content=content, size_hint=(0.7, 0.5))
        
        def on_confirm(instance):
            if self.on_delete_video:
                self.on_delete_video(video_id, is_uploaded=False)
            popup.dismiss()
            self.refresh_video_lists()
        
        confirm_btn.bind(on_release=on_confirm)
        cancel_btn.bind(on_release=popup.dismiss)
        popup.open()
    
    def download_to_device(self, video_id, video_name, parent_popup):
        """Download video to device's storage"""
        if self.on_download_to_device:
            self.on_download_to_device(video_id, video_name)
        parent_popup.dismiss()

    def play_video(self, video_id, parent_popup):
        """Play the video using system default player or Kivy video player"""
        parent_popup.dismiss()
    
        app = App.get_running_app()
        if not app.peer or video_id not in app.peer.video_library:
            return
    
        video_info = app.peer.video_library[video_id]
        video_path = video_info['path']
    
        # Try to open with system default player
        try:
            import subprocess
            import platform
        
            system = platform.system()
            if system == 'Windows':
                os.startfile(video_path)
            elif system == 'Darwin':  # macOS
                subprocess.call(['open', video_path])
            else:  # Linux and others
                subprocess.call(['xdg-open', video_path])
        
            print(f"Opening video: {video_path}")
        except Exception as e:
            print(f"Error opening video: {e}")
            # Fallback: show path to user
            self.show_video_path_popup(video_path, video_info['name'])

    def show_video_path_popup(self, video_path, video_name):
        """Show popup with video path if can't open automatically"""
        content = BoxLayout(orientation='vertical', padding=20, spacing=15)
    
        content.add_widget(Label(
            text=f'Video Location:\n\n{video_path}',
            size_hint_y=0.7,
            halign='center',
            valign='middle'
        ))
    
        copy_btn = Button(text='Copy Path', size_hint_y=0.15)
        close_btn = Button(text='Close', size_hint_y=0.15)
    
        content.add_widget(copy_btn)
        content.add_widget(close_btn)
    
        popup = Popup(
            title=f'Cannot Auto-Open: {video_name}',
            content=content,
            size_hint=(0.8, 0.5)
        )
    
        def copy_path(instance):
            try:
                from kivy.core.clipboard import Clipboard
                Clipboard.copy(video_path)
                copy_btn.text = 'Copied!'
            except:
                pass
    
        copy_btn.bind(on_release=copy_path)
        close_btn.bind(on_release=popup.dismiss)
        popup.open()
    
    def clear_videos(self):
        """Clear all videos from both lists"""
        self.ids.uploaded_videos_list.clear_widgets()
        self.ids.downloaded_videos_list.clear_widgets()
    
    def refresh_video_lists(self):
        """Refresh the video lists"""
        app = App.get_running_app()
        if hasattr(app, '_load_existing_videos'):
            self.clear_videos()
            app._load_existing_videos()
    
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
    
    def show_user_menu(self):
        """Show user menu popup"""
        app = App.get_running_app()
        if hasattr(app, 'show_user_menu'):
            app.show_user_menu()


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
            text=f"{video_name}\nSize: {self._format_size(size)}\nFrom: {peer_host}:{peer_port}",
            halign='left',
            valign='middle'
        )
        info_label.bind(size=info_label.setter('text_size'))
        
        download_btn = Button(
            text="Download",
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
    
    def show_user_menu(self):
        """Show user menu popup"""
        app = App.get_running_app()
        if hasattr(app, 'show_user_menu'):
            app.show_user_menu()


class PeersScreen(Screen):
    """Screen for displaying connected peers and friends"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.on_refresh_peers: Optional[Callable] = None
        self.on_add_friend: Optional[Callable] = None
        self.on_remove_friend: Optional[Callable] = None
        self.on_connect_to_peer: Optional[Callable] = None
    
    def refresh_connected_users(self):
        """Refresh the list of connected users"""
        if self.on_refresh_peers:
            self.on_refresh_peers()
    
    def add_connected_user(self, peer_id, host, port):
        """Add a connected user to the list"""
        container = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            height=90,
            padding=8,
            spacing=5
        )
    
        info_label = Label(
            text=f" {peer_id}\n {host}:{port}",
            size_hint_y=0.65,
            halign='left',
            valign='middle',
            font_size='15sp'
        )
        info_label.bind(size=info_label.setter('text_size'))
    
        options_btn = Button(
            text='⋮ Options',
            size_hint_y=0.35,
            on_release=lambda x: self.show_user_options(peer_id, host, port, is_friend=False)
        )
    
        container.add_widget(info_label)
        container.add_widget(options_btn)
    
        from kivy.graphics import Color, Line
        with container.canvas.before:
            Color(0.3, 0.3, 0.3, 1)
            Line(rectangle=(container.x, container.y, container.width, container.height), width=1.2)
    
        self.ids.connected_users_list.add_widget(container)
    
    def add_friend(self, peer_id, host, port):
        """Add a friend to the friends list"""
        container = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            height=90,
            padding=8,
            spacing=5
        )
    
        # Friend info with better formatting
        info_label = Label(
            text=f" {peer_id}\n {host}:{port}",
            halign='left',
            valign='middle',
            font_size='15sp',
            color=(1, 0.9, 0.3, 1)
        )
        info_label.bind(size=info_label.setter('text_size'))
    
        # Options button
        options_btn = Button(
            text='⋮ Options',
            size_hint_y=0.35,
            on_release=lambda x: self.show_user_options(peer_id, host, port, is_friend=True)
        )
    
        container.add_widget(info_label)
        container.add_widget(options_btn)
    
        # Add border
        from kivy.graphics import Color, Line
        with container.canvas.before:
            Color(0.3, 0.3, 0.3, 1)
            Line(rectangle=(container.x, container.y, container.width, container.height), width=1.2)
    
        self.ids.friends_list.add_widget(container)
    
    def show_user_options(self, peer_id, host, port, is_friend=False):
        """Show options for a user"""
        content = BoxLayout(orientation='vertical', padding=20, spacing=15)
        
        content.add_widget(Label(
            text=f'Options for:\n{peer_id}',
            size_hint_y=0.3,
            font_size='18sp',
            bold=True
        ))
        
        # Connect manually button
        connect_btn = Button(text=' Connect Manually', size_hint_y=0.2)
        connect_btn.bind(on_release=lambda x: self.connect_to_user(peer_id, host, port, popup))
        content.add_widget(connect_btn)
        
        if is_friend:
            # Remove from friends
            remove_btn = Button(
                text=' Remove from Friends',
                size_hint_y=0.2,
                background_color=(0.8, 0.2, 0.2, 1)
            )
            remove_btn.bind(on_release=lambda x: self.remove_from_friends(peer_id, popup))
            content.add_widget(remove_btn)
        else:
            # Add to friends
            add_friend_btn = Button(text='Add to Friends', size_hint_y=0.2)
            add_friend_btn.bind(on_release=lambda x: self.add_to_friends(peer_id, host, port, popup))
            content.add_widget(add_friend_btn)
        
        # Cancel button
        cancel_btn = Button(text='Cancel', size_hint_y=0.3)
        content.add_widget(cancel_btn)
        
        popup = Popup(title='User Options', content=content, size_hint=(0.7, 0.6))
        cancel_btn.bind(on_release=popup.dismiss)
        popup.open()
    
    def connect_to_user(self, peer_id, host, port, parent_popup):
        """Connect to a user manually"""
        parent_popup.dismiss()
        if self.on_connect_to_peer:
            self.on_connect_to_peer(host, port)
    
    def add_to_friends(self, peer_id, host, port, parent_popup):
        """Add user to friends list"""
        parent_popup.dismiss()
        if self.on_add_friend:
            self.on_add_friend(peer_id, host, port)
    
    def remove_from_friends(self, peer_id, parent_popup):
        """Remove user from friends list"""
        parent_popup.dismiss()
        if self.on_remove_friend:
            self.on_remove_friend(peer_id)
    
    def clear_connected_users(self):
        """Clear connected users list"""
        self.ids.connected_users_list.clear_widgets()
    
    def clear_friends(self):
        """Clear friends list"""
        self.ids.friends_list.clear_widgets()
    
    def set_my_peer_info(self, peer_id, host, port):
        """Set current user's peer information"""
        self.ids.my_peer_info.text = f" Your Info:\n\nPeer ID: {peer_id}\nHost: {host}\nPort: {port}"
    
    def show_settings(self):
        """Show settings popup"""
        settings = SettingsPopup()
        settings.open()
    
    def show_user_menu(self):
        """Show user menu popup"""
        app = App.get_running_app()
        if hasattr(app, 'show_user_menu'):
            app.show_user_menu()

    def show_manual_connection(self, peer_id, host, port):
        """Show manual connection indicator"""
        self.ids.manual_connection_box.height = 60
        self.ids.manual_connection_label.text = f" Currently Connected to:\n👤 {peer_id} ({host}:{port})"

    def hide_manual_connection(self):
        """Hide manual connection indicator"""
        self.ids.manual_connection_box.height = 0
        self.ids.manual_connection_label.text = ""

    def disconnect_manual(self):
        """Disconnect from manual connection"""
        app = App.get_running_app()
        if hasattr(app, 'disconnect_from_peer'):
            app.disconnect_from_peer()


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
        self.uploaded_videos = set()  # Videos user uploaded
        self.downloaded_videos = {}  # Videos downloaded from network: {video_id: peer_info}
        self.network_videos = set()  # Videos announced to tracker
        # Track manual connection
        self.manual_connection = None
    
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
        self.config_screen.on_load_profile = self.load_profile
        self.my_videos_screen.on_upload_video = self.upload_video
        self.my_videos_screen.on_delete_video = self.delete_video
        self.my_videos_screen.on_edit_video = self.edit_video
        self.my_videos_screen.on_upload_to_network = self.upload_to_network
        self.my_videos_screen.on_download_to_device = self.download_to_device
        self.network_screen.on_browse_network = self.browse_network
        self.network_screen.on_download_video = self.download_video
        self.peers_screen.on_refresh_peers = self.refresh_peers
        self.peers_screen.on_add_friend = self.add_friend
        self.peers_screen.on_remove_friend = self.remove_friend
        self.peers_screen.on_connect_to_peer = self.connect_to_peer

        # Initialize theme colors
        from kivy.clock import Clock
        Clock.schedule_once(lambda dt: self.update_theme_colors(), 0.1)
        
        return sm
    
    def load_profile(self, peer_id, port, tracker_host, tracker_port):
        """Load an existing profile and start peer"""
        from Server import load_profile
    
        profile = load_profile(peer_id)
        if profile:
            # Load friends
            friends = profile.get('friends', [])
        
            # Start peer with profile data
            self.start_peer(peer_id, port, tracker_host, tracker_port, friends=friends)

    def show_user_menu(self):
        """Show user menu popup"""
        content = BoxLayout(orientation='vertical', padding=20, spacing=15)
    
        if self.peer_id:
            content.add_widget(Label(
                text=f'User: {self.peer_id}',
                size_hint_y=0.3,
                font_size='18sp',
                bold=True
            ))
    
        # Edit details button
        edit_btn = Button(text=' Edit User Details', size_hint_y=0.25)
        edit_btn.bind(on_release=lambda x: self.show_edit_user_dialog(popup))
        content.add_widget(edit_btn)
    
        # Delete user button
        delete_btn = Button(
            text=' Delete User',
            size_hint_y=0.25,
            background_color=(0.8, 0.2, 0.2, 1)
        )
        delete_btn.bind(on_release=lambda x: self.confirm_delete_user(popup))
        content.add_widget(delete_btn)
    
        # Cancel button
        cancel_btn = Button(text='Cancel', size_hint_y=0.2)
        content.add_widget(cancel_btn)
    
        popup = Popup(title='User Menu', content=content, size_hint=(0.7, 0.6))
        cancel_btn.bind(on_release=popup.dismiss)
        popup.open()

    def show_edit_user_dialog(self, parent_popup):
        """Show dialog to edit user details"""
        parent_popup.dismiss()
    
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
    
        content.add_widget(Label(text='Edit User Details', size_hint_y=0.15, font_size='18sp'))
    
        peer_id_input = TextInput(
            hint_text='Peer ID',
            text=self.peer_id or '',
            multiline=False,
            size_hint_y=0.15
        )
        content.add_widget(peer_id_input)
    
        port_input = TextInput(
            hint_text='Port',
            text=str(self.peer_port) if self.peer_port else '5000',
            multiline=False,
            size_hint_y=0.15
        )
        content.add_widget(port_input)
    
        tracker_host_input = TextInput(
            hint_text='Tracker Host',
            text=self.tracker_host or 'localhost',
            multiline=False,
            size_hint_y=0.15
        )
        content.add_widget(tracker_host_input)
    
        tracker_port_input = TextInput(
            hint_text='Tracker Port',
            text=str(self.tracker_port) if self.tracker_port else '6000',
            multiline=False,
            size_hint_y=0.15
        )
        content.add_widget(tracker_port_input)
    
        button_box = BoxLayout(size_hint_y=0.15, spacing=10)
        save_btn = Button(text=' Save')
        cancel_btn = Button(text='Cancel')
        button_box.add_widget(save_btn)
        button_box.add_widget(cancel_btn)
        content.add_widget(button_box)
    
        popup = Popup(title='Edit User', content=content, size_hint=(0.8, 0.7))
    
        def on_save(instance):
            # Note: Editing requires restart
            new_peer_id = peer_id_input.text
            new_port = int(port_input.text)
            new_tracker_host = tracker_host_input.text
            new_tracker_port = int(tracker_port_input.text)
        
            # Save profile
            from Server import save_profile, get_friends
            friends = get_friends(self.peer_id) if self.peer_id else []
            save_profile(new_peer_id, new_port, new_tracker_host, new_tracker_port, friends)
        
            popup.dismiss()
            self.show_restart_message()
    
        save_btn.bind(on_release=on_save)
        cancel_btn.bind(on_release=popup.dismiss)
        popup.open()

    def show_restart_message(self):
        """Show message that restart is required"""
        content = BoxLayout(orientation='vertical', padding=20, spacing=15)
    
        content.add_widget(Label(
            text='Changes saved!\n\nPlease restart the application\nfor changes to take effect.',
            size_hint_y=0.7
        ))
    
        ok_btn = Button(text='OK', size_hint_y=0.3)
        content.add_widget(ok_btn)
    
        popup = Popup(title='Restart Required', content=content, size_hint=(0.6, 0.4))
        ok_btn.bind(on_release=popup.dismiss)
        popup.open()

    def confirm_delete_user(self, parent_popup):
        """Confirm user deletion"""
        parent_popup.dismiss()
    
        content = BoxLayout(orientation='vertical', padding=20, spacing=15)
    
        content.add_widget(Label(
            text=f'Delete user "{self.peer_id}"?\n\nThis will delete:\n- All uploaded videos\n- All settings\n- Friend list\n\nThis cannot be undone!',
            size_hint_y=0.7
        ))
    
        button_box = BoxLayout(size_hint_y=0.3, spacing=10)
        confirm_btn = Button(text=' Delete', background_color=(0.8, 0.2, 0.2, 1))
        cancel_btn = Button(text='Cancel')
        button_box.add_widget(confirm_btn)
        button_box.add_widget(cancel_btn)
        content.add_widget(button_box)
    
        popup = Popup(title='Confirm Delete', content=content, size_hint=(0.7, 0.6))
    
        def on_confirm(instance):
            from Server import delete_profile
            delete_profile(self.peer_id)
            popup.dismiss()
        
            # Stop peer and return to config screen
            if self.peer:
                self.peer.stop()
            self.root.current = 'config'
            self.config_screen.load_profiles()
    
        confirm_btn.bind(on_release=on_confirm)
        cancel_btn.bind(on_release=popup.dismiss)
        popup.open()
    
    def start_peer(self, peer_id, port, tracker_host, tracker_port, friends=None):
        """Start the peer node"""
        try:
            from Server import Peer, register_with_tracker, save_profile
        
            self.tracker_host = tracker_host
            self.tracker_port = tracker_port
            self.peer_id = peer_id
            self.peer_host = 'localhost'
            self.peer_port = port
        
            # Save profile
            save_profile(peer_id, port, tracker_host, tracker_port, friends or [])
        
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
                    Clock.schedule_once(lambda dt: self.refresh_peers(), 1.0)
                    Clock.schedule_once(lambda dt: self._set_my_peer_info(), 0.3)
                    Clock.schedule_once(lambda dt: self._load_friends(), 0.4)
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

    def update_theme_colors(self):
        """Update text colors based on current theme"""
        # Define colors based on theme
        if self.theme_mode == 'light':
            text_color = (0, 0, 0, 1)  # Black text
            button_color = (0.2, 0.2, 0.2, 1)  # Dark gray for buttons
            hint_color = (0.5, 0.5, 0.5, 1)  # Gray for hints
        else:
            text_color = (1, 1, 1, 1)  # White text
            button_color = (1, 1, 1, 1)  # White for buttons
            hint_color = (0.7, 0.7, 0.7, 1)  # Light gray for hints
    
        # Update all screens
        for screen_name in ['config', 'my_videos', 'network', 'peers']:
            screen = self.root.get_screen(screen_name)
            self._update_widget_colors(screen, text_color, button_color, hint_color)

    def _update_widget_colors(self, widget, text_color, button_color, hint_color):
        """Recursively update colors for all widgets"""
        from kivy.uix.label import Label
        from kivy.uix.button import Button
        from kivy.uix.textinput import TextInput
    
        # Update current widget if it's a text widget
        if isinstance(widget, Label):
            # Don't change color if it's a status label with specific colors
            if not hasattr(widget, 'id') or widget.id != 'status_label':
                widget.color = text_color
        elif isinstance(widget, Button):
            widget.color = button_color
        elif isinstance(widget, TextInput):
            widget.foreground_color = text_color
            widget.hint_text_color = hint_color
    
        # Recursively update children
        if hasattr(widget, 'children'):
            for child in widget.children:
                self._update_widget_colors(child, text_color, button_color, hint_color)
    
    def upload_video(self, file_path, video_name, description):
        """Handle video upload"""
        if not self.peer:
            return
    
        def do_upload():
            video_id = self.peer.add_video(file_path, video_name, description)
        
            if video_id:
                # Mark as uploaded video
                self.uploaded_videos.add(video_id)
            
                # Update UI
                video_info = self.peer.video_library[video_id]
                Clock.schedule_once(
                    lambda dt: self.my_videos_screen.add_uploaded_video(
                        video_id, video_name, video_info['size'], is_on_network=False
                    ), 0
                )
    
        threading.Thread(target=do_upload, daemon=True).start()

    def delete_video(self, video_id, is_uploaded=True):
        """Delete a video from the library"""
        if not self.peer:
            return
    
        def do_delete():
            try:
                # Remove from peer's library and delete file
                if video_id in self.peer.video_library:
                    video_path = self.peer.video_library[video_id]['path']
                    if os.path.exists(video_path):
                        os.remove(video_path)
                    del self.peer.video_library[video_id]
            
                # Remove from tracking sets
                if is_uploaded:
                    self.uploaded_videos.discard(video_id)
                else:
                    self.downloaded_videos.pop(video_id, None)
                self.network_videos.discard(video_id)
            
                print(f"Deleted video: {video_id}")
            except Exception as e:
                print(f"Error deleting video: {e}")
    
        threading.Thread(target=do_delete, daemon=True).start()

    def edit_video(self, video_id, new_name, new_description):
        """Edit video information"""
        if not self.peer or video_id not in self.peer.video_library:
            return
    
        with self.peer.lock:
            self.peer.video_library[video_id]['name'] = new_name
            self.peer.video_library[video_id]['description'] = new_description
    
        print(f"Updated video info for {video_id}")

    def upload_to_network(self, video_id):
        """Announce video to tracker (upload to network)"""
        if not self.peer:
            return
    
        def do_announce():
            from Server import announce_video_to_tracker
        
            success = announce_video_to_tracker(
                peer_id=self.peer.peer_id,
                video_id=video_id,
                tracker_host=self.tracker_host,
                tracker_port=self.tracker_port
            )
        
            if success:
                self.network_videos.add(video_id)
                print(f"Video {video_id} announced to network")
                # Refresh the video list to show updated network status
                Clock.schedule_once(lambda dt: self.my_videos_screen.refresh_video_lists(), 0.5)
    
        threading.Thread(target=do_announce, daemon=True).start()

    def download_to_device(self, video_id, video_name):
        """Download video file to user's device storage"""
        if not self.peer or video_id not in self.peer.video_library:
            return
    
        def do_save():
            try:
                video_info = self.peer.video_library[video_id]
                source_path = video_info['path']
            
                # Use file chooser to select save location
                if HAS_PLYER:
                    from plyer import filechooser
                    save_path = filechooser.save_file(
                        title=f"Save {video_name}",
                        filters=[("Video files", "*.mp4")]
                    )
                    if save_path:
                        # Handle list return
                        if isinstance(save_path, list):
                            save_path = save_path[0]
                    
                        # Copy file to selected location
                        import shutil
                        shutil.copy2(source_path, save_path)
                        print(f"Video saved to: {save_path}")
                else:
                    # Fallback: save to Downloads or current directory
                    import shutil
                    downloads_path = os.path.expanduser("~/Downloads")
                    if not os.path.exists(downloads_path):
                        downloads_path = os.path.expanduser("~")
                
                    save_path = os.path.join(downloads_path, f"{video_name}.mp4")
                    shutil.copy2(source_path, save_path)
                    print(f"Video saved to: {save_path}")
                
            except Exception as e:
                print(f"Error saving video: {e}")
    
        threading.Thread(target=do_save, daemon=True).start()
    
    def browse_network(self):
        """Browse videos on the network"""
        if not self.peer:
            return
    
        def do_browse():
            try:
                from Server import get_peers_from_tracker
            
                self.network_screen.clear_network_videos()
            
                # Get all peers from tracker
                peers = get_peers_from_tracker(
                    tracker_host=self.tracker_host,
                    tracker_port=self.tracker_port
                )
            
                # Query each peer for their videos
                for peer_info in peers:
                    peer_id = peer_info['peer_id']
                    peer_host = peer_info['host']
                    peer_port = peer_info['port']
                
                    # Skip our own peer
                    if peer_id == self.peer_id:
                        continue
                
                    try:
                        # Request video list from this peer
                        videos = self.peer.request_video_list(peer_host, peer_port)
                    
                        for video in videos:
                            Clock.schedule_once(
                                lambda dt, v=video, h=peer_host, p=peer_port:
                                self.network_screen.add_network_video(
                                    v['id'], v['name'], v['size'], h, p
                                ), 0
                            )
                    except Exception as e:
                        print(f"Error getting videos from {peer_id}: {e}")
                    
            except Exception as e:
                print(f"Error browsing network: {e}")
    
        threading.Thread(target=do_browse, daemon=True).start()
    
    def download_video(self, video_id, peer_host, peer_port):
        """Download a video from another peer"""
        if not self.peer:
            return
    
        def do_download():
            from Server import announce_video_to_tracker
        
            success = self.peer.download_video(peer_host, peer_port, video_id)
        
            if success:
                # Mark as downloaded video with source peer info
                peer_info = f"{peer_host}:{peer_port}"
                self.downloaded_videos[video_id] = peer_info
            
                # Announce to tracker
                announce_video_to_tracker(
                    peer_id=self.peer.peer_id,
                    video_id=video_id,
                    tracker_host=self.tracker_host,
                    tracker_port=self.tracker_port
                )
                self.network_videos.add(video_id)
            
                # Update UI
                video_info = self.peer.video_library[video_id]
                Clock.schedule_once(
                    lambda dt: self.my_videos_screen.add_downloaded_video(
                        video_id, video_info['name'], video_info['size'], peer_info
                    ), 0
                )
    
        threading.Thread(target=do_download, daemon=True).start()
    
    def connect_to_peer(self, peer_host, peer_port):
        """Connect to a peer manually"""
        if not self.peer:
            return
    
        self.peer.add_known_peer(peer_host, peer_port)
    
        def do_connect():
            from Server import get_peers_from_tracker
        
            peers = get_peers_from_tracker(
                tracker_host=self.tracker_host,
                tracker_port=self.tracker_port
            )
        
            peer_id = "Unknown"
            for peer_info in peers:
                if peer_info['host'] == peer_host and peer_info['port'] == peer_port:
                    peer_id = peer_info['peer_id']
                    break
        
            self.manual_connection = {
                'peer_id': peer_id,
                'host': peer_host,
                'port': peer_port
            }
        
            Clock.schedule_once(
                lambda dt: self.peers_screen.show_manual_connection(peer_id, peer_host, peer_port), 0
            )
    
        threading.Thread(target=do_connect, daemon=True).start()

    def disconnect_from_peer(self):
        """Disconnect from manually connected peer"""
        if self.manual_connection:
            self.manual_connection = None
            self.peers_screen.hide_manual_connection()
    
    def _load_existing_videos(self):
        """Load existing videos from peer library"""
        if not self.peer:
            return
    
        for video_id, video_info in self.peer.video_library.items():
            # Check if it's an uploaded or downloaded video
            if video_id in self.uploaded_videos:
                # Uploaded video
                is_on_network = video_id in self.network_videos
                self.my_videos_screen.add_uploaded_video(
                    video_id, video_info['name'], video_info['size'], is_on_network
                )
            elif video_id in self.downloaded_videos:
                # Downloaded video
                peer_info = self.downloaded_videos[video_id]
                self.my_videos_screen.add_downloaded_video(
                    video_id, video_info['name'], video_info['size'], peer_info
                )
            else:
                # Default to uploaded if not tracked
                self.uploaded_videos.add(video_id)
                self.my_videos_screen.add_uploaded_video(
                    video_id, video_info['name'], video_info['size'], is_on_network=False
                )
    
    def _set_my_peer_info(self):
        """Set current user's peer information in Peers screen"""
        if self.peer:
            print(f"Setting peer info: ID={self.peer_id}, Host={self.peer_host}, Port={self.peer_port}")
            self.peers_screen.set_my_peer_info(
                self.peer_id, self.peer_host, self.peer_port
            )

    def refresh_peers(self):
        """Refresh list of connected peers"""
        if not self.peer:
            return
    
        from Server import get_peers_from_tracker
    
        def do_refresh():
            peers = get_peers_from_tracker(
                tracker_host=self.tracker_host,
                tracker_port=self.tracker_port
            )
        
            Clock.schedule_once(lambda dt: self.peers_screen.clear_connected_users(), 0)
        
            if peers:
                for peer_info in peers:
                    p_id = str(peer_info['peer_id'])
                    p_host = str(peer_info['host'])
                    p_port = int(peer_info['port'])
                
                    if p_id != self.peer.peer_id:
                        self.peer.add_known_peer(p_host, p_port)
                    
                        def add_user(peer_id, peer_host, peer_port):
                            self.peers_screen.add_connected_user(peer_id, peer_host, peer_port)
                    
                        Clock.schedule_once(lambda dt, a=p_id, b=p_host, c=p_port: add_user(a, b, c), 0)
    
        threading.Thread(target=do_refresh, daemon=True).start()

    def add_friend(self, peer_id, host, port):
        """Add a peer to friends list"""
        if not self.peer_id:
            return
    
        from Server import add_friend
        success = add_friend(self.peer_id, peer_id, host, port)
    
        if success:
            # Refresh friends display
            self._load_friends()

    def remove_friend(self, peer_id):
        """Remove a peer from friends list"""
        if not self.peer_id:
            return
    
        from Server import remove_friend
        success = remove_friend(self.peer_id, peer_id)
    
        if success:
            # Refresh friends display
            self._load_friends()

    def _load_friends(self):
        """Load friends list"""
        if not self.peer_id:
            return
    
        from Server import get_friends
        friends = get_friends(self.peer_id)
    
        self.peers_screen.clear_friends()
    
        for friend in friends:
            self.peers_screen.add_friend(
                friend['peer_id'],
                friend['host'],
                friend['port']
            )
