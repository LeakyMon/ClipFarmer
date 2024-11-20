import customtkinter as ctk
import yt_dlp
import os
import sys
import tempfile
import ffmpeg

# Add project root to Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

# Import Firebase functions
from backend.firebase import upload_file_to_storage, add_video_metadata, check_if_title_exists, get_video_duration,add_script_metadata, add_song_metadata,get_audio_duration

class UploadFrame(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.create_widgets()
        
    def create_widgets(self):
        # Title
        self.title_label = ctk.CTkLabel(self, text="Upload Media", font=ctk.CTkFont(size=24, weight="bold"))
        self.title_label.pack(pady=20)

        # Title Textbox
        self.title_entry = ctk.CTkEntry(self, width=400, placeholder_text="Enter Title")
        self.title_entry.pack(pady=10)

        # Folder Dropdown (Background/Overlay/Music/VoiceOvers/Scripts)
        self.folder_dropdown = ctk.CTkOptionMenu(self, values=["Background", "Overlay", "Music", "VoiceOvers", "Scripts"], command=self.update_placeholder)
        self.folder_dropdown.pack(pady=10)

        # Media Type Dropdown (Video or MP3)
        self.media_type_dropdown = ctk.CTkOptionMenu(self, values=["Video", "MP3"])
        self.media_type_dropdown.pack(pady=10)

        # YouTube URL or Script Textbox
        self.url_entry = ctk.CTkEntry(self, width=400, placeholder_text="Enter YouTube URL or Script Content")
        self.url_entry.pack(pady=20)

        # Submit Button
        self.submit_button = ctk.CTkButton(self, text="Submit", command=self.submit_url)
        self.submit_button.pack(pady=20)

    def update_placeholder(self, folder):
        """Updates the placeholder text for the URL entry based on folder selection."""
        if folder == "Scripts":
            self.url_entry.configure(placeholder_text="Enter Script Content")
            self.media_type_dropdown.configure(state="disabled")  # Disable media type dropdown when Scripts is selected
        else:
            self.url_entry.configure(placeholder_text="Enter YouTube URL")
            self.media_type_dropdown.configure(state="normal")  # Enable media type dropdown for other folder types

    def submit_url(self):
        # Get the title, folder, media type, and URL from the UI
        title = self.title_entry.get()
        folder = self.folder_dropdown.get()
        media_type = self.media_type_dropdown.get()  # Get the selected media type (Video or MP3)
        url_or_script = self.url_entry.get()

        if title and folder and url_or_script:
            print(f"Submitted URL or Script: {url_or_script}")
            print(f"Title: {title}, Folder: {folder}, Media Type: {media_type}")

            # Check if the title already exists in the database
            if check_if_title_exists(title):
                self.clear_widgets()
                error_label = ctk.CTkLabel(self, text="Error: Title already exists!", font=ctk.CTkFont(size=24, weight="bold"))
                error_label.pack(pady=50)
                return

            # Handle script upload when folder is "Scripts"
            if folder == "Scripts":
                self.upload_script(title, folder, url_or_script)
            else:
                # Detect if the URL is from YouTube and download accordingly
                if "youtube.com" in url_or_script or "youtu.be" in url_or_script:
                    if media_type == "Video":
                        self.download_video(url_or_script, title, folder)
                    elif media_type == "MP3":
                        self.download_mp3(url_or_script, title, folder)
                else:
                    print("Invalid or unsupported URL")
        else:
            print("Title, Folder, or URL/Script is empty")


    def download_video(self, url, title, folder):
        save_path = os.path.join(os.getcwd(), "videos")
        os.makedirs(save_path, exist_ok=True)  # Ensure the save path exists

        video_path = os.path.join(save_path, f"{title}.mp4")
        temp_video_path = os.path.join(save_path, f"{title}_temp_video.mp4")
        temp_audio_path = os.path.join(save_path, f"{title}_temp_audio.mp4")

        ydl_opts = {
            'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best',  # Download best video and best audio
            'outtmpl': temp_video_path,  # Temporary file for the video
            'merge_output_format': 'mp4',  # Ensure MP4 output format
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        # Merge video and audio using FFmpeg
        try:
            (
                ffmpeg
                .input(temp_video_path)
                .output(video_path, vcodec='copy', acodec='copy', movflags='faststart')
                .run(overwrite_output=True)
            )
            print(f"Video and audio merged successfully: {video_path}")
        except ffmpeg.Error as e:
            print(f"Error merging video and audio: {e}")

        # Cleanup temporary files
        if os.path.exists(temp_video_path):
            os.remove(temp_video_path)
        if os.path.exists(temp_audio_path):
            os.remove(temp_audio_path)

        # Proceed with thumbnail generation and Firebase upload
        thumbnail_path = self.generate_thumbnail(video_path)
        duration = get_video_duration(video_path)
        self.upload_to_firebase(title, folder, video_path, thumbnail_path, duration)



    def download_mp3(self, url, title, folder):
        save_path = os.path.join(os.getcwd(), "music")
        os.makedirs(save_path, exist_ok=True)  # Ensure the save path exists

        filename = f'{title}'

        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': f'{save_path}/{filename}',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'rm-cache-dir': True  # Clear the cache before downloading
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        mp3_path = f'{save_path}/{filename}.mp3'
        print(f"Downloaded MP3 to {mp3_path}")
        get_audio_duration(mp3_path)

        # Generate a thumbnail (optional)
        thumbnail_path = self.generate_thumbnail(mp3_path)

        # Upload MP3 and Thumbnail to Firebase Storage
        duration = get_video_duration(mp3_path)
        self.upload_song_to_firebase(title, folder, mp3_path, thumbnail_path, duration)


    def generate_thumbnail(self, video_path):
        """Generates a thumbnail for the video and returns the file path."""
        try:
            # Use a temporary directory for the thumbnail
            temp_dir = tempfile.gettempdir()
            thumbnail_path = os.path.join(temp_dir, f"{os.path.basename(video_path)}_thumbnail.jpg")

            # Use ffmpeg to capture a frame at 2 seconds for the thumbnail
            probe = ffmpeg.probe(video_path)
            video_duration = float(probe['streams'][0]['duration'])

            # Set the time to capture the thumbnail (2 seconds in this case)
            thumbnail_time = min(2, video_duration / 2)  # Ensures it won't exceed video length

            # Generate the thumbnail
            (
                ffmpeg
                .input(video_path, ss=thumbnail_time)
                .filter('scale', 320, -1)  # Resize to 320px wide, keeping aspect ratio
                .output(thumbnail_path, vframes=1)
                .overwrite_output()
                .run(capture_stdout=True, capture_stderr=True)
            )

            print(f"Thumbnail generated at: {thumbnail_path}")
            return thumbnail_path

        except ffmpeg.Error as e:
            print(f"Error generating thumbnail: {e}")
            return None

    def upload_to_firebase(self, title, folder, video_path, thumbnail_path,duration):
        """Uploads video and thumbnail to Firebase Storage and saves metadata to Firestore."""
        try:
            # Upload the video to Firebase Storage
            video_url = upload_file_to_storage(video_path, os.path.basename(video_path), folder, "videos")
            print(f"Video uploaded to: {video_url}")

            # Check if thumbnail was generated before attempting upload
            if thumbnail_path:
                thumbnail_url = upload_file_to_storage(thumbnail_path, os.path.basename(thumbnail_path), folder, "thumbnails")
                print(f"Thumbnail uploaded to: {thumbnail_url}")
            else:
                print("No thumbnail was generated.")
                thumbnail_url = "default_thumbnail_url"  # Set a default thumbnail URL if needed

            # Save metadata to Firestore
            add_video_metadata(title, video_url, thumbnail_url, folder,duration)
            print(f"Video metadata saved for '{title}'")

            # Delete the video file after uploading
            if os.path.exists(video_path):
                os.remove(video_path)
                print(f"Deleted local video file: {video_path}")

            # Clear widgets and display success message
            self.clear_widgets()
            self.display_success_message()

        except Exception as e:
            print(f"Error uploading to Firebase: {e}")

    def upload_song_to_firebase(self, title, folder, mp3_path, thumbnail_path, duration):
        """Uploads MP3 and thumbnail to Firebase Storage and saves song metadata to Firestore."""
        try:
            # Upload the MP3 to Firebase Storage
            song_url = upload_file_to_storage(mp3_path, os.path.basename(mp3_path), folder, "music")
            print(f"MP3 uploaded to: {song_url}")

            # Check if thumbnail was generated before attempting upload
            if thumbnail_path:
                thumbnail_url = upload_file_to_storage(thumbnail_path, os.path.basename(thumbnail_path), folder, "thumbnails")
                print(f"Thumbnail uploaded to: {thumbnail_url}")
            else:
                print("No thumbnail was generated.")
                thumbnail_url = "default_thumbnail_url"  # Set a default thumbnail URL if needed

            # Save metadata to Firestore using your add_song_metadata function
            add_song_metadata(title, song_url, thumbnail_url, folder, duration)
            print(f"Song metadata saved for '{title}'")

            # Delete the MP3 file after uploading
            if os.path.exists(mp3_path):
                os.remove(mp3_path)
                print(f"Deleted local MP3 file: {mp3_path}")

            # Clear widgets and display success message
            self.clear_widgets()
            self.display_success_message()

        except Exception as e:
            print(f"Error uploading to Firebase: {e}")


    def clear_widgets(self):
        """Clears all widgets from the current frame."""
        for widget in self.winfo_children():
            widget.destroy()

    def display_success_message(self):
        """Displays a success message after video upload."""
        success_label = ctk.CTkLabel(self, text="Video Successfully Uploaded!", font=ctk.CTkFont(size=24, weight="bold"))
        success_label.pack(pady=50)

        self.after(3000,self.reset())
        
    def reset(self):
        """Resets the frame by clearing all widgets and recreating the initial layout."""
        self.clear_widgets()
        self.create_widgets()  # Recreate the original layout after clearing everything


    def upload_script(self, title, folder, script_content):
        """Uploads script to Firebase Storage and saves metadata to Firestore."""
        try:
            # Create a temporary file for the script
            save_path = os.path.join(tempfile.gettempdir(), f"{title}.txt")
            with open(save_path, "w") as script_file:
                script_file.write(script_content)

            # Upload the script to Firebase Storage
            script_url = upload_file_to_storage(save_path, os.path.basename(save_path), folder, "scripts")
            print(f"Script uploaded to: {script_url}")

            # Save metadata to Firestore (using the same function, or you can create a new one if needed)
            add_script_metadata(title, script_url, script_content, "")  # No duration for scripts

            # Delete the temporary script file after uploading
            if os.path.exists(save_path):
                os.remove(save_path)
                print(f"Deleted local script file: {save_path}")

            # Clear widgets and display success message
            self.clear_widgets()
            self.display_success_message()

        except Exception as e:
            print(f"Error uploading script to Firebase: {e}")
