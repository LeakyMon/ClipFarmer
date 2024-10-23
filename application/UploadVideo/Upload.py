import customtkinter as ctk
import yt_dlp
import os
import sys
import tempfile
import ffmpeg

# Add project root to Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

# Import Firebase functions
from backend.firebase import upload_file_to_storage, add_video_metadata

class UploadFrame(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)

        # Title
        self.title_label = ctk.CTkLabel(self, text="Upload Video", font=ctk.CTkFont(size=24, weight="bold"))
        self.title_label.pack(pady=20)

        # Title Textbox
        self.title_entry = ctk.CTkEntry(self, width=400, placeholder_text="Enter Title")
        self.title_entry.pack(pady=10)

        # Folder Dropdown (Background/Overlay)
        self.folder_dropdown = ctk.CTkOptionMenu(self, values=["Background", "Overlay"])
        self.folder_dropdown.pack(pady=10)

        # YouTube URL Textbox
        self.url_entry = ctk.CTkEntry(self, width=400, placeholder_text="Enter YouTube URL")
        self.url_entry.pack(pady=20)

        # Submit Button
        self.submit_button = ctk.CTkButton(self, text="Submit", command=self.submit_url)
        self.submit_button.pack(pady=20)

    def submit_url(self):
        # Get the title, folder, and URL from the UI
        title = self.title_entry.get()
        folder = self.folder_dropdown.get()
        url = self.url_entry.get()

        if title and folder and url:
            print(f"Submitted YouTube URL: {url}")
            print(f"Title: {title}, Folder: {folder}")

            # Download the video
            self.download_video(url, title, folder)
        else:
            print("Title, Folder, or URL is empty")

    def download_video(self, url, title, folder):
        save_path = os.path.join(os.getcwd(), "videos")
        os.makedirs(save_path, exist_ok=True)  # Ensure the save path exists

        filename = f'{title}.mp4'

        ydl_opts = {
            'format': 'best',
            'outtmpl': f'{save_path}/{filename}',
            'rm-cache-dir': True  # Clear the cache before downloading
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        video_path = f'{save_path}/{filename}'
        print(f"Downloaded video to {video_path}")

        # Generate a thumbnail
        thumbnail_path = self.generate_thumbnail(video_path)

        # Upload Video and Thumbnail to Firebase Storage
        self.upload_to_firebase(title, folder, video_path, thumbnail_path)

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

    def upload_to_firebase(self, title, folder, video_path, thumbnail_path):
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
            add_video_metadata(title, video_url, thumbnail_url, folder)
            print(f"Video metadata saved for '{title}'")

        except Exception as e:
            print(f"Error uploading to Firebase: {e}")
